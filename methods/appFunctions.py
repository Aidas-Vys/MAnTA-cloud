import os
from io import StringIO
from termite_toolkit import termite
from pandas import DataFrame, concat, to_datetime
import pybliometrics as pb
from global_variables.vocab_groups import vocabs_all, voc_groups
from global_variables.others import palette_set
import plotly.express as px
import re
from openai import AzureOpenAI
import tiktoken


def Find_in_scopus(query: str):
    try:
        pb.scopus.init(config_dir="config.ini")
        a = pb.scopus.ScopusSearch(query)
        if a.results is None:
            return DataFrame([{"None error": "None Error"}])
        else:
            df = DataFrame(DataFrame(a.results))[
                [
                    "eid",
                    "title",
                    "description",
                    "author_names",
                    "authkeywords",
                    "publicationName",
                    "coverDate",
                    "citedby_count",
                ]
            ]
            list_of_links = []
            for part in a.__dict__["_json"]:
                list_of_links.append([part["link"][2]["@href"], part.get("eid")])
            df = df.merge(DataFrame(list_of_links, columns=["link", "eid"]), on="eid")
            df["docID"] = "Row_" + (df.index + 1).astype(str)
            return df
    except Exception as e:
        df = DataFrame([{"scopus error": str(e)}])
        return df


def Mark_up(df_to_mark, mined_df, columns_to_mark):
    if type(columns_to_mark) != list:
        columns_to_mark = [columns_to_mark]
    df_syn = mined_df[["entityType", "realSynList", "docID", "Color"]]
    for i in df_to_mark.index:
        row_id = df_to_mark.loc[i]["docID"]
        all_syn = df_syn[df_syn.docID == row_id]
        if all_syn.empty:
            continue
        for syn in all_syn["Color"].index:
            color_code = all_syn["Color"][syn]
            word_list = all_syn["realSynList"][syn]
            for w in word_list:
                for c in columns_to_mark:
                    if not isinstance(df_to_mark.loc[i, c], str):
                        continue
                    else:
                        df_to_mark.loc[i, c] = df_to_mark.loc[i][c].replace(
                            w, f'<span style="background-color:{color_code}">{w}</span>'
                        )
    return df_to_mark


def set_binary_content(self, input_file_path):
    try:
        file_obj = open(input_file_path, "rb")
        file_name = os.path.basename(input_file_path)
    except TypeError:
        file_obj = input_file_path
        file_name = os.path.basename("binary")

    self.binary_content = {"binary": (file_name, file_obj)}


# termite.TermiteRequestBuilder.set_binary_content = set_binary_content


def termite_request_df(vocab, bytes_df):
    t = termite.TermiteRequestBuilder()
    t.set_url("http://spidsmus.sdma.nzcorp.net:9090/termite/")
    t.set_binary_content(bytes_df)
    t.set_input_format("xlsx")
    t.set_entities(vocab)
    t.set_output_format("json")
    # execute the request
    resp = t.execute()
    term_df = termite.get_termite_dataframe(resp)
    return term_df


def get_key(val, my_dict):
    for key, value in my_dict.items():
        if val == value:
            return key


def df_mine(df_to_mine, columns, vocab):
    full_df = DataFrame()
    if type(columns) != list:
        columns = [columns]

    for col in columns:
        col_df = DataFrame(df_to_mine[col].replace(r"\n", " ", regex=True))
        col_df.fillna("")
        b_buf = StringIO()
        b_buf.write(col_df.to_csv(sep=","))
        b_buf.seek(0)
        termite_df = termite_request_df(vocab, b_buf)
        termite_df["field"] = col
        full_df = concat([full_df, termite_df], ignore_index=True)
        full_df["SubjectGroup"] = None

        for i in full_df["entityType"].unique():
            for age in voc_groups.values():
                if age.__contains__(i):
                    name = get_key(age, voc_groups)
                    full_df.loc[full_df["entityType"] == i, "SubjectGroup"] = name

    if len(palette_set) < len(full_df["entityType"].unique()):
        n = 0
        while len(palette_set) < len(vocab):
            palette_set.append(palette_set[n])
            n = n + 1

    full_df.loc[full_df["SubjectGroup"].isnull(), "SubjectGroup"] = full_df[
        "entityType"
    ]
    full_df["name"] = full_df["name"].str.casefold()
    full_df = full_df.drop_duplicates(["name", "docID", "field"])

    d_swap = {v: k for k, v in vocabs_all.items()}
    full_df["entityType"] = full_df["entityType"].replace(d_swap)

    Color_scheme = {
        full_df["entityType"].unique()[i]: palette_set[i]
        for i in range(len(full_df["entityType"].unique()))
    }
    full_df["Color"] = full_df["entityType"].map(Color_scheme)

    return full_df, Color_scheme


def make_timeline_df(
    year_c: str, data_df: DataFrame, result_df: DataFrame, list_names: list
):
    df_timeline = result_df.merge(data_df[[year_c, "docID"]], "left", "docID")
    df_timeline = df_timeline.dropna(subset=[year_c])
    pattern = re.compile("^[12]\d\d\d")

    if pattern.match(str(df_timeline[year_c][0])[:4]):
        df_timeline[year_c] = df_timeline[year_c].astype(str).str[:4]
    elif pattern.match(str(df_timeline[year_c][0])[-4:]):
        df_timeline[year_c] = df_timeline[year_c].astype(str).str[-4:]

    df_timeline = df_timeline[["name", year_c, "docID"]][
        df_timeline.name.str.contains("|".join(list_names), case=False)
    ]
    df_timeline = (
        df_timeline.drop_duplicates(["name", "docID"])
        .groupby([year_c, "name"])
        .docID.value_counts()
        .rename_axis([year_c, "name", "docID"])
        .reset_index(name="# documents")
        .groupby([year_c, "name"])
        .sum("# documents")
        .reset_index()
    )

    df_timeline[year_c] = to_datetime(df_timeline[year_c], format="%Y")
    df_timeline.groupby("name")[(year_c)].min()
    mina = df_timeline.groupby("name")[(year_c)].min().reset_index()

    df_timeline = (
        df_timeline.set_index([year_c, "name"])
        .unstack(fill_value=0)
        .asfreq("AS", fill_value=0)
        .stack()
        .sort_index(level=1)
        .reset_index()
    )
    mina = df_timeline.groupby("name")[(year_c)].min().reset_index()
    for i in range(len(mina)):
        a = mina["name"][i]
        b = mina[year_c][i]
        df_timeline = df_timeline.drop(
            df_timeline[(df_timeline["name"] == a) & (df_timeline[year_c] < b)].index
        )
    df_timeline[year_c] = df_timeline[year_c].astype(str).str[:4].astype(int)

    return df_timeline


def make_scopus_timeline(data_df: DataFrame):
    data_df["coverDate"] = data_df["coverDate"].astype(str).str[:4]
    article_timeline = (
        data_df.groupby("coverDate")
        .eid.count()
        .rename_axis(["year"])
        .reset_index(name="# articles")
    )
    article_timeline["year"] = to_datetime(article_timeline["year"], format="%Y")
    article_timeline = (
        article_timeline.resample("AS", on="year").mean().fillna(0).reset_index()
    )
    article_timeline["year"] = article_timeline["year"].astype(str).str[:4].astype(int)
    fig_time_publication = px.line(
        article_timeline,
        x="year",
        y="# articles",
        text="# articles",
        title="Number of articles published per year",
    )
    fig_time_publication.update_traces(textposition="top center")
    fig_time_publication.update_xaxes(tickmode="linear")
    fig_time_publication.update_layout(
        paper_bgcolor="rgba(25,25,25,0.5)",
        plot_bgcolor="rgba(0,0,0,0.5)",
        font_color="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True),
    )
    return fig_time_publication


def contains_all_strings(group, search_list):
    return all(item in group["name"].values for item in search_list)


# def generate_csv_file(df):
#     # Process your data as needed
#     # For example, if your data is a list of dictionaries, convert it to a DataFrame
#     df = DataFrame.from_dict(df)

#     # Generate the CSV file
#     csv_content = df.to_csv(index=False)
#     return csv_content


# asd = Find_in_scopus("TITLE-ABS-KEY ( bread AND enzyme AND baking )")
def send_to_completions(string):
    # gets the API Key from environment variable AZURE_OPENAI_API_KEY
    client = AzureOpenAI(
        # https://learn.microsoft.com/azure/ai-services/openai/reference#rest-api-versioning
        api_version="2023-09-15-preview",
        # https://learn.microsoft.com/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
        azure_endpoint="https://librarydalletest.openai.azure.com/",
        api_key="45c2e72bbf7645d5aa974781c7a7237f",
    )

    completion = client.chat.completions.create(
        model="MAnTA_Summary",  # e.g. gpt-35-instant
        messages=[
            {
                "role": "user",
                "content": string,
            },
        ],
        # max_tokens=10, u can set the response length to limit costs
        temperature=0,
        # messages: Iterable[ChatCompletionMessageParam],
        # model: Union[str, ChatModel],
        # frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        # function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        # functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        # logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        # logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        # max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        # n: Optional[int] | NotGiven = NOT_GIVEN,
        # parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        # presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        # response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        # seed: Optional[int] | NotGiven = NOT_GIVEN,
        # service_tier: Optional[Literal["auto", "default"]] | NotGiven = NOT_GIVEN,
        # stop: Union[Optional[str], List[str]] | NotGiven = NOT_GIVEN,
        # stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        # stream_options: Optional[ChatCompletionStreamOptionsParam] | NotGiven = NOT_GIVEN,
        # temperature: Optional[float] | NotGiven = NOT_GIVEN,
        # tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        # tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        # top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        # top_p: Optional[float] | NotGiven = NOT_GIVEN,
        # user: str | NotGiven = NOT_GIVEN,
        # # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # # The extra values given here take precedence over values defined on the client or passed to this method.
        # extra_headers: Headers | None = None,
        # extra_query: Query | None = None,
        # extra_body: Body | None = None,
        # timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    )
    text_message = completion.to_dict()
    return text_message["choices"][0]["message"]["content"]


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def openai_api_calculate_cost_for_prompt(string, model="gpt-3.5-turbo-1106"):
    pricing = {
        "gpt-3.5-turbo-1106": {
            "prompt": 0.0015,
            "completion": 0.002,
        },
        "gpt-4-1106-preview": {
            "prompt": 0.01,
            "completion": 0.03,
        },
        "gpt-4": {
            "prompt": 0.03,
            "completion": 0.06,
        },
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        raise ValueError("Invalid model specified")
    tokens = num_tokens_from_string(string, model) + 100
    prompt_cost = tokens * model_pricing["prompt"] / 1000

    # round to 6 decimals
    prompt_cost = round(prompt_cost, 6)

    return prompt_cost
