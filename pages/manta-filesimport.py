from cmath import isnan
from html.entities import html5
from termite_toolkit import termite
from dash import html, dcc, dash_table, Input, Output, State, callback, register_page
from sklearn import preprocessing  # check code to change to sckitlearn
import base64
import io
import pandas as pd
import plotly.io as pio
import plotly.express as px
import pypdf

pio.renderers.default = "browser"
import dash_bootstrap_components as dbc
import re
import visdcc

# import sys
# local import:
from methods.appFunctions import (
    Mark_up,
    set_binary_content,
    contains_all_strings,
    df_mine,
    make_timeline_df,
    send_to_completions,
    openai_api_calculate_cost_for_prompt,
)
from global_variables.others import palette_set, esc_dict
from common_components.comp_fileImport import (
    landing_p,
    tab1,
    tab2,
    Vocab_groups_drop,
    Vocabs_drop,
)
from global_variables.style_formats import HR_line_styled

register_page(__name__)
termite.TermiteRequestBuilder.set_binary_content = set_binary_content

# just testing some visuals
# df_result_bar = pd.read_csv("mine_res_for_test_2.csv")
# fig = px.bar(df_result_bar, x='name', y="hitCount")

# for k in fig.layout:
#     if re.search('xaxis[1-9]+', k):
#         fig.layout[k].update(matches=None)
#     if re.search('yaxis[1-9]+', k):
#         fig.layout[k].update(matches=None)

# fig.update_yaxes(visible=False)
# fig.update_layout(
#     autosize=True,
#     height=800,
#     yaxis_categoryorder = 'total ascending',
#     paper_bgcolor='rgba(25,25,25,0.5)',
#     plot_bgcolor='rgba(0,0,0,0.5)',#legend=dict(font=dict(color="white"))
#     font_color="white")

layout = html.Div(
    [
        visdcc.Run_js(id="javascript"),
        dcc.Store(id="Front_page", storage_type="memory"),
        dcc.Store(id="tm_df", storage_type="memory"),
        dcc.Store(id="color_palette", storage_type="memory"),
        dcc.Store(id="collected_list", storage_type="memory"),
        dcc.Download(id="download_collected_component"),
        landing_p,
        tab1,
        tab2,
        html.Div(" ", style={"margin-top": "40vh"}),
    ],
    className="overlay",
)


def parse_contents(contents, filename):
    # if multiple files:
    content_list = []
    for i in contents:
        content_type, content_string = i.split(",")
        content_list.append(content_string)
    content_dict = dict(zip(filename, content_list))

    # content_type, content_string = contents[0].split(",")
    decoded = base64.b64decode(content_string)
    try:
        if ".csv" in filename[0]:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        # elif 'xlsx' in filename[0]:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
        elif ".xlsx" in filename[0]:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), engine="openpyxl")
        elif ".xls" in filename[0]:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), engine="xlrd")
        elif ".pdf" in filename[0]:
            df = pd.DataFrame()
            for key in content_dict.keys():
                item = content_dict[key]
                decoded = base64.b64decode(item)
                pdf_content = pypdf.PdfReader(io.BytesIO(decoded))
                num_pages = len(pdf_content.pages)
                content = ""
                for i in range(0, num_pages):
                    content += pdf_content.pages[i].extract_text() + "\n"
                content = " ".join(content.replace("\xa0", " ").strip().split())
                page_number_removal = r"\d{1,3} of \d{1,3}"
                page_number_removal_pattern = re.compile(
                    page_number_removal, re.IGNORECASE
                )
                content = re.sub(page_number_removal_pattern, "", content)
                df1 = pd.DataFrame(
                    {"Document_name": [key], "Extracted Text": [content]}
                )
                df = pd.concat([df, df1])

        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    except Exception as e:
        df = pd.DataFrame({"ExceptionError": [""], str(e): [""]})
        table_data = df.to_dict("records")
        return table_data
    if "df" in locals():
        df = df.reset_index()
        df["docID"] = "Row_" + (df.index + 1).astype(str)
        # drop empty cols, make this into an OPTION later
        df.dropna(how="all", axis=1, inplace=True)
        df["Comments"] = ""
        table_data = df.to_dict("records")
        # return table_data
    else:
        df = pd.DataFrame({"NoneError": [""], "None": [""]})
        table_data = df.to_dict("records")
        # return table_data
    return table_data


@callback(
    Output("Front_page", "data"),
    [Input("upload", "contents")],
    State("upload", "filename"),
)
def update_output(contents, filename):
    if contents is not None:
        data = parse_contents(contents, filename)
        return data


@callback(
    [Output("output-data-upload", "children"), Output("Vocab_and_column", "children")],
    [Input("Front_page", "modified_timestamp")],
    State("Front_page", "data"),
)
def make_front(ts, table_data):
    if ts is None:
        return "", ""
    else:
        if table_data is None:
            return "", ""
        elif "ExceptionError" in table_data[0].keys():
            return html.Div("Exception Error occured, check the file and try again"), ""
        elif "NoneError" in table_data[0].keys():
            return (
                html.Div("Incorrect file format - try .csv, .xlsx or .xls formats"),
                "",
            )
        else:
            cols = table_data[0]
            table_lay = html.Div(
                [
                    html.H2(
                        "Imported data preview - total number of documents: "
                        + str(len(table_data))
                    ),
                    dash_table.DataTable(
                        style_data={
                            "height": "auto",
                            "whiteSpace": "normal",
                            "backgroundColor": "rgb(50, 50, 50)",
                            "color": "white",
                            "font-size": "medium",
                            "font-family": "monospace",
                            "max-width": "15vh",
                        },
                        style_cell={"textAlign": "left"},
                        style_header={"backgroundColor": "rgb(30, 30, 30)"},
                        css=[
                            {
                                "selector": ".dash-spreadsheet td div",
                                "rule": "line-height: 15px; max-height: 65px; min-heigh: 30px; height: 30px; display: block; overflow-y: hidden; overflow-wrap: anywhere",
                            }
                        ],
                        data=table_data[0:5],
                        columns=[{"name": i, "id": i} for i in cols],
                        # hidden_columns = ["docID"],
                        page_size=6,
                        tooltip_duration=None,
                        tooltip_data=[
                            {
                                column: {"value": str(value), "type": "markdown"}
                                for column, value in row.items()
                            }
                            for row in table_data
                        ],
                    ),
                    HR_line_styled,
                ],
                style={
                    "margin-left": "1rem",
                    "margin-right": "1rem",
                    "color": "white",
                    "max-width": "100vw",
                },
            )

            dropdowns = html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5(
                                        "1) Select at least one column for analysis:"
                                    ),
                                    dcc.Dropdown(
                                        id="selected_columns",
                                        options=[
                                            {"label": x, "value": x}
                                            for x in table_data[0].keys()
                                        ],
                                        multi=True,
                                        clearable=True,
                                        value="description",
                                    ),
                                ]
                            )
                        ]
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5("2) Select a subject group:"),
                                    Vocab_groups_drop,
                                ],
                                width=5,
                            ),
                            dbc.Col(
                                [
                                    html.Br(),
                                    html.H5("or", style={"text-align": "center"}),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.H5("Select subjects individually:"),
                                    Vocabs_drop,
                                ],
                                width=5,
                            ),
                        ]
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            html.Div(
                                [
                                    dbc.Button(
                                        id="tm_button",
                                        children="Text mine",
                                        class_name="me-0",
                                        color="secondary",
                                    ),
                                    dbc.Button(
                                        "Help",
                                        id="infobtn_dropdowns",
                                        color="warning",
                                        class_name="me-0",
                                        n_clicks=0,
                                        style={"margin-left": "1rem"},
                                    ),
                                    dbc.Tooltip(
                                        dcc.Markdown(
                                            """
                                                **Subject** - refers to a collection of words/concepts that MAnTA can identify. \n
                                                **Subject group** - refers to a group of pre-selected subjects covering a wider area. \n
                                                **Select columns to analyze** - select columns from your data to analyze by text mining *(e.g. Title, Description)*.\n
                                                **Select a subject group** - select broad subject groups to analyze by text mining *(e.g. "Food and Beverage" area will find words such as "meat","flavor","dairy", etc..)* \n
                                                **Select subjects individually** - select any number of specific subjects to analyze by text mining *(e.g. Fungal taxonomy will find words such as "Aspergillus oryzae")*\n
                                                **For more information visit the Wiki:**\n
                                                https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki                                                        
                                                """,
                                            link_target="_blank",
                                            dangerously_allow_html=True,
                                        ),
                                        id="tooltip_dropdowns",
                                        is_open=False,
                                        target="infobtn_dropdowns",
                                        trigger=None,
                                    ),
                                ],
                                style={"text-align": "left"},
                            )
                        ]
                    ),
                ],
                style={
                    "margin-bottom": "5px",
                    "margin-right": "2rem",
                    "margin-left": "1rem",
                    "whiteSpace": "normal",
                },
            )

            return table_lay, dropdowns


@callback(
    Output("tooltip_dropdowns", "is_open"),
    [Input("infobtn_dropdowns", "n_clicks")],
    [State("tooltip_dropdowns", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_overview", "is_open"),
    [Input("infobtn_overview", "n_clicks")],
    [State("tooltip_overview", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_bar", "is_open"),
    [Input("infobtn_bar", "n_clicks")],
    [State("tooltip_bar", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_timeline", "is_open"),
    [Input("infobtn_timeline", "n_clicks")],
    [State("tooltip_timeline", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_collect", "is_open"),
    [Input("infobtn_collect", "n_clicks")],
    [State("tooltip_collect", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_overlap", "is_open"),
    [Input("infobtn_overlap", "n_clicks")],
    [State("tooltip_overlap", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("tooltip_summary", "is_open"),
    [Input("infobtn_summary", "n_clicks")],
    [State("tooltip_summary", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    [
        Output("tm_df", "data"),
        Output("topic_overview", "children"),
        Output("analysisH2", "style"),
        Output("concept_analysis", "children"),
        Output("overlap_analysis", "children"),
        Output("timeline_analysis", "children"),
        Output("collected_documents", "children"),
        Output("summary", "children"),
        Output("color_palette", "data"),
        Output("topic_overview_display", "style"),
        Output("concept_analysis_display", "style"),
        Output("timeline_analysis_display", "style"),
        Output("collected_documents_display", "style"),
        Output("overlap_analysis_display", "style"),
        Output("summary_display", "style"),
    ],
    [Input("tm_button", "n_clicks")],
    State("Front_page", "data"),
    State("selected_columns", "value"),
    State("VocabSelect", "value"),
    State("GroupSelect", "value"),
    State("GroupSelect", "options"),
)
def test_selection(n, data, column, vocab, vocab_group, voc_lab):
    if n is None:
        data = " "
        return (
            data,
            " ",
            {"display": "none"},
            " ",
            " ",
            " ",
            " ",
            " ",
            "",
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        )
    elif column == [] or column is None:
        return (
            "",
            dbc.Container(
                [
                    dbc.Row(
                        [
                            html.H2(
                                "No columns selected for Text mining, please select columns with text-based data."
                            )
                        ],
                        justify="center",
                        align="center",
                        className="h-50",
                    )
                ],
                style={"height": "50vh"},
            ),
            {"display": "none"},
            " ",
            " ",
            " ",
            " ",
            " ",
            "",
            {"display": "inline-block"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        )
    elif (vocab is None or vocab == []) and (vocab_group == [] or vocab_group is None):
        return (
            "",
            dbc.Container(
                [
                    dbc.Row(
                        [
                            html.H2(
                                "No Subject groups or Subjects selected, please select Subject groups or Subjects to text mine for."
                            )
                        ],
                        justify="center",
                        align="center",
                        className="h-50",
                    )
                ],
                style={"height": "50vh"},
            ),
            {"display": "none"},
            " ",
            " ",
            " ",
            " ",
            " ",
            "",
            {"display": "inline-block"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        )
    else:
        # deal with groups or individual vocab lists:
        if type(column) != list:
            column = [column]
        if vocab is None:
            vocab = []
        if vocab_group is None:
            vocab_group = []
        vocab = [
            *set(
                [
                    item
                    for sublist in [i.split(",") for i in vocab_group]
                    for item in sublist
                ]
                + vocab
            )
        ]
        # Vocab and data mining:
        vocab = ",".join(vocab)
        data_df = pd.DataFrame.from_dict(data)
        df_result, Color_scheme = df_mine(data_df, column, vocab)
        if df_result.empty:
            return (
                "",
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                html.H2(
                                    "No concepts found for selected topics or data columns, try selecting different subjects and make sure you selected columns with relevant data"
                                )
                            ],
                            justify="center",
                            align="center",
                            className="h-50",
                        )
                    ],
                    style={"height": "50vh"},
                ),
                {"display": "none"},
                " ",
                " ",
                " ",
                " ",
                " ",
                "",
                {"display": "inline-block"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
                {"display": "none"},
            )
        else:
            a_norm = preprocessing.normalize(
                df_result["hitCount"].to_numpy().reshape(1, -1)
            )
            df_result["Norm_hits"] = a_norm.tolist()[0]

            df_result["Color"] = df_result["entityType"].map(Color_scheme)
            df_result[["hitCount"]] = df_result[["hitCount"]].apply(pd.to_numeric)
            the_labels = []
            for g in vocab_group:
                for x in voc_lab:
                    if x["value"] == g:
                        a = x["label"]
                        the_labels.append(a)

            df_result.loc[
                ~df_result["SubjectGroup"].isin(the_labels), "SubjectGroup"
            ] = df_result["entityType"]

            df_tm = df_result.to_dict("records")
            # TOTAL # of articles + Total hitCount
            df_summary3 = (
                df_result.drop_duplicates(["name", "docID"])
                .groupby("SubjectGroup")
                .name.value_counts()
                .rename_axis(["SubjectGroup", "name"])
                .reset_index(name="# documents")
                .sort_values(["# documents"], ascending=False)
                .merge(
                    df_result[["SubjectGroup", "name", "hitCount"]]
                    .groupby(["SubjectGroup", "name"])
                    .sum("hitCount")
                    .reset_index()
                    .sort_values(["hitCount"], ascending=False),
                    on="name",
                    how="left",
                )
                .sort_values(["# documents"], ascending=False)
                .rename(columns={"name": "Concepts", "hitCount": "Total #"})
            )

            df_summary3["Concepts"] = df_summary3["Concepts"].str.lower()
            df_summary3 = df_summary3.drop_duplicates(subset=["Concepts"])

            df_result_bar = (
                df_result[["field", "SubjectGroup", "name", "hitCount"]]
                .groupby(["field", "SubjectGroup", "name"])
                .sum("hitCount")
                .reset_index()
                .sort_values(["hitCount"], ascending=False)
                .groupby(["field", "SubjectGroup"])
                .head(3)
            )

            fig = px.bar(
                df_result_bar,
                x="name",
                y="hitCount",
                text="hitCount",
                text_auto=".2s",
                custom_data=["field"],
                facet_col="field",
                title="Concept frequency: Total # of Concepts in documents - click bars to fetch documents",
                color="SubjectGroup",
                color_discrete_map=Color_scheme,
            )

            # this makes the separate ticvk for each facet plot
            for k in fig.layout:
                if re.search("xaxis[1-9]+", k):
                    fig.layout[k].update(matches=None)
                if re.search("yaxis[1-9]+", k):
                    fig.layout[k].update(matches=None)

            fig.update_yaxes(visible=False)
            fig.update_layout(
                autosize=True,
                # height=800,
                yaxis_categoryorder="total ascending",
                paper_bgcolor="rgba(25,25,25,0.5)",
                plot_bgcolor="rgba(0,0,0,0.5)",  # legend=dict(font=dict(color="white"))
                font_color="white",
            )

            # distribution by vocab
            Pie_counts = (
                df_result.groupby(["SubjectGroup"])["hitCount"].sum().reset_index()
            )
            total = df_result["hitCount"].sum()
            pie_fig = px.pie(
                Pie_counts,
                values="hitCount",
                names="SubjectGroup",
                title="Topic distribution by total amount of detected concepts",
                color="SubjectGroup",
                color_discrete_map=Color_scheme,
            )
            pie_fig.update_layout(
                paper_bgcolor="rgba(25,25,25,0.5)",
                plot_bgcolor="rgba(0,0,0,0.5)",  # legend=dict(font=dict(color="white"))
                font_color="white",
            )

            # Pie_counts_articles = df_result.groupby('SubjectGroup')['docID'].nunique().rename_axis(['SubjectGroup']).reset_index(name="Number of occurances in Documents")

            # pie_fig_articles = px.pie(Pie_counts_articles, values='Number of occurances in Documents',
            #     names='SubjectGroup', title = "Topic Abundance by number of Documents",
            #     color="SubjectGroup",
            #     # color_discrete_map = Color_scheme
            #     )
            # pie_fig_articles.update_layout(
            #     paper_bgcolor='rgba(25,25,25,0.5)',
            #     plot_bgcolor='rgba(0,0,0,0.5)',
            #     font_color="white")

            pie_graph = html.Div(
                dbc.Row(
                    [
                        dbc.Label(
                            "Total number of detected concepts via text mining:"
                            + str(total),
                            style={"font-style": "italic", "font-size": "150%"},
                        ),
                        dbc.Col(
                            dcc.Graph(
                                figure=pie_fig,
                                style={"overflowY": "auto", "height": "auto"},
                            ),
                            width=12,
                        ),
                        # dbc.Col
                        # (
                        #     dcc.Graph
                        #     (
                        #         figure=pie_fig_articles,
                        #         style={'overflowY': 'auto', 'height': "auto"}
                        #     ),
                        # width=12),
                    ]
                ),
            )

            Concept_child = html.Div(
                dbc.Row(
                    [
                        dcc.Graph(
                            id="concepts-bar",
                            figure=fig,
                            style={
                                "overflowY": "auto",
                                "overflowX": "auto",
                            },
                        ),
                    ],
                    style={"overflow": "auto"},
                )
            )

            Timeline_child = html.Div(
                [
                    html.H4("Select date/year column:"),
                    HR_line_styled,
                    dbc.Row(
                        dcc.Dropdown(
                            id="year_column",
                            options=[{"label": x, "value": x} for x in data[0].keys()],
                            multi=False,
                        )
                    ),
                    html.Br(),
                    dbc.Row(
                        html.Hr(
                            style={
                                "width": "100%",
                                "color": "white",
                                "margin-left": "0.7rem",
                            }
                        )
                    ),
                    html.Div(
                        id="selection table",
                        children=[
                            html.H4("Select concepts to get timeline:"),
                            HR_line_styled,
                            html.H6("Table Filter:"),
                            dcc.Dropdown(
                                id="Timeline_dropdown",
                                options=[
                                    {"label": x, "value": x}
                                    for x in df_result["entityType"].unique()
                                ],
                                multi=True,
                                clearable=True,
                            ),
                            HR_line_styled,
                            dash_table.DataTable(
                                id="Timeline Table",
                                style_table={"overflowX": "auto", "max-height": "50vh"},
                                style_header={"backgroundColor": "rgb(30, 30, 30)"},
                                style_data={
                                    "backgroundColor": "rgb(50, 50, 50)",
                                    "whiteSpace": "normal",
                                },
                                style_cell={"textAlign": "left", "max-width": "20vw"},
                                data=df_summary3.to_dict("records"),
                                columns=[
                                    {"name": i, "id": i}
                                    for i in ["Concepts", "# documents", "Total #"]
                                ],
                                row_selectable="multi",
                                page_size=50,
                            ),
                        ],
                    ),
                ]
            )

            overlap_child = html.Div(
                [
                    dbc.Row(
                        [
                            HR_line_styled,
                            dbc.Col(
                                [
                                    html.H4("1) Select Column/-s to contain concepts:"),
                                    # HR_line_styled,
                                    dcc.Dropdown(
                                        id="overlap_columns",
                                        options=[
                                            {"label": x, "value": x} for x in column
                                        ],
                                        multi=True,
                                        clearable=True,
                                        value=column[0],
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.H4(
                                        "2) Select at least 2 concepts that appear together:"
                                    ),
                                    # HR_line_styled,
                                    dcc.Dropdown(
                                        id="overlap_concepts",
                                        options=[
                                            {"label": x, "value": x}
                                            for x in df_result["name"].unique()
                                        ],
                                        multi=True,
                                        clearable=True,
                                        # value=df_result['name'].unique()[0:2],
                                        searchable=True,
                                    ),
                                ]
                            ),
                        ],
                        style={"margin-bottom": "1rem"},
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                id="generate_overlap_button",
                                children="Get Documents",
                                class_name="me-0",
                                color="secondary",
                            )
                        ],
                        style={"margin-bottom": "1rem"},
                    ),
                ]
            )

            collected_child = html.Div(
                [
                    html.Div(
                        dash_table.DataTable(
                            id="collected_data",
                            columns=[
                                {"name": i, "id": i, "presentation": "markdown"}
                                for i in data[0].keys()
                            ],
                        ),
                        style={"display": "none"},
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id="collected_data_time",
                            columns=[
                                {"name": i, "id": i, "presentation": "markdown"}
                                for i in data[0].keys()
                            ],
                        ),
                        style={"display": "none"},
                    ),
                    html.Div(
                        dash_table.DataTable(
                            id="collected_data_overlap",
                            columns=[
                                {"name": i, "id": i, "presentation": "markdown"}
                                for i in data[0].keys()
                            ],
                            editable=True,
                        ),
                        style={"display": "none"},
                    ),
                    html.Div(id="collection_table_div"),
                ]
            )
            Summary_child = html.Div(
                [
                    dbc.Row(
                        [
                            html.H4(
                                "Select 1 Column to use for summary of the dataset: "
                            ),
                            dcc.Dropdown(
                                id="summary_columns",
                                options=[
                                    {"label": x, "value": x} for x in data[0].keys()
                                ],
                                multi=False,
                                clearable=True,
                            ),
                        ]
                    ),
                    html.Br(),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dbc.Button(
                                        "Generate Summary",
                                        id="open",
                                        n_clicks=0,
                                        class_name="me-0",
                                        color="secondary",
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader(
                                                dbc.ModalTitle("Summary Generation"),
                                                style={
                                                    "backgroundColor": "rgb(50, 50, 50)"
                                                },
                                            ),
                                            dbc.ModalBody(
                                                id="modal_text",
                                                style={
                                                    "backgroundColor": "rgb(30, 30, 30)"
                                                },
                                            ),
                                            dbc.ModalFooter(
                                                [
                                                    dbc.Button(
                                                        id="generate_summary_button",
                                                        children="Generate Summary",
                                                        class_name="me-0",
                                                        color="secondary",
                                                    ),
                                                    dbc.Button(
                                                        "Close",
                                                        id="close",
                                                        className="ms-auto",
                                                        n_clicks=0,
                                                    ),
                                                ],
                                                style={
                                                    "backgroundColor": "rgb(50, 50, 50)"
                                                },
                                            ),
                                        ],
                                        id="modal",
                                        is_open=False,
                                    ),
                                ]
                            ),
                        ],
                        style={"margin-bottom": "1rem"},
                    ),
                ]
            )

        return (
            df_tm,
            pie_graph,
            {"display": "inline-block"},
            Concept_child,
            overlap_child,
            Timeline_child,
            collected_child,
            Summary_child,
            Color_scheme,
            {"display": "inline-block"},
            {"display": "inline-block"},
            {"display": "inline-block"},
            {"display": "inline-block"},
            {"display": "inline-block"},
            {"display": "inline-block"},
        )


@callback(
    Output("concepts-bar", "figure"),
    [Input("slider", "value"), Input("radio_button_hits", "value")],
    State("tm_df", "data"),
    State("color_palette", "data"),
)
def update_concept_bar(slider_val, radio_b, data, color_palette):
    df_result = pd.DataFrame.from_dict(data)
    if radio_b == 1:
        # this is the bar plot for named entity counts
        df_result_bar = (
            df_result.groupby(["field", "SubjectGroup"])
            .name.value_counts()
            .rename_axis(["field", "SubjectGroup", "name"])
            .reset_index(name="number_of_articles")
            .groupby(["field", "SubjectGroup"])
            .head(slider_val)
        )
        fig = px.bar(
            df_result_bar,
            x="name",
            y="number_of_articles",
            text_auto=".2s",
            facet_col="field",
            custom_data=["field"],
            title="Concept frequency: # of documents with Concept - click bars to fetch documents",
            color="SubjectGroup",
            color_discrete_map=color_palette,
        )
    else:
        df_result_bar = (
            df_result[["field", "SubjectGroup", "name", "hitCount"]]
            .groupby(["field", "SubjectGroup", "name"])
            .sum("hitCount")
            .reset_index()
            .sort_values(["hitCount"], ascending=False)
            .groupby(["field", "SubjectGroup"])
            .head(slider_val)
        )
        fig = px.bar(
            df_result_bar,
            x="name",
            y="hitCount",
            text="hitCount",
            text_auto=".2s",
            custom_data=["field"],
            facet_col="field",
            title="Concept frequency: Total # of Concepts in documents - click bars to fetch documents",
            color="SubjectGroup",
            color_discrete_map=color_palette,
        )

    # this makes the separate ticvk for each facet plot
    for k in fig.layout:
        if re.search("xaxis[1-9]+", k):
            fig.layout[k].update(matches=None)
        if re.search("yaxis[1-9]+", k):
            fig.layout[k].update(matches=None)

    fig.update_yaxes(visible=False)
    fig.update_layout(
        autosize=True,
        # height=800,
        yaxis_categoryorder="total ascending",
        paper_bgcolor="rgba(25,25,25,0.5)",
        plot_bgcolor="rgba(0,0,0,0.5)",  # legend=dict(font=dict(color="white"))
        font_color="white",
    )

    return fig


@callback(
    Output("click-data", "children"),
    [Input("concepts-bar", "clickData")],
    State("Front_page", "data"),
    State("tm_df", "data"),
    State("selected_columns", "value"),
)
def display_click_data(clickData, data_front, data_tm, columns):
    a = pd.DataFrame.from_dict(data_front)
    b = pd.DataFrame.from_dict(data_tm)
    string = clickData["points"][0]["label"]
    field = clickData["points"][0]["customdata"][0]
    # field = clickData['points'][0]['customdata']
    # try to do something about this
    result_mine = b.loc[(b["name"] == string) & (b["field"] == field)]
    result = a[a.docID.isin((pd.Series.tolist(result_mine["docID"])))]

    Mark_up(result, result_mine, columns)
    syn_list = result_mine[result_mine["name"].str.contains(string)][
        "realSynList"
    ].tolist()
    syn_unlist = sum(syn_list, [])
    string_synonyms = ", ".join(list(set(syn_unlist)))

    tbl = result.to_dict("records")

    child = html.Div(
        [
            dbc.Row(
                dbc.Label(
                    (
                        "concept and synonyms: "
                        + string_synonyms
                        + " - in "
                        + field
                        + " (number of documents: "
                        + str(len(result.index))
                        + ")",
                    ),
                    className="synonym_display_text",
                )
            ),
            dbc.Row(
                dbc.Label(
                    'Add documents to "Collected Documents" by clicking the checkbox in the first column of the table.',
                    className="document_collection_label",
                )
            ),
            dash_table.DataTable(
                id="bar_documents",
                markdown_options={"html": True},
                style_header={"backgroundColor": "rgb(30, 30, 30)"},
                style_data={
                    "backgroundColor": "rgb(50, 50, 50)",
                },
                style_cell={
                    "textAlign": "left",
                },
                data=tbl,
                columns=[
                    {"name": i, "id": i, "presentation": "markdown"}
                    for i in result.columns
                ],
                row_selectable="multi",
                page_size=3,
                hidden_columns=list(set(result.columns) - set(columns)),
            ),
            HR_line_styled,
        ],
        style={"margin-left": "1rem", "margin-right": "1rem"},
    )

    return child


@callback(Output("javascript", "run"), [Input("output-data-upload", "children")])
def myfun(x):
    if x:
        return """
        const element = document.getElementById('output-data-upload')
        element.scrollIntoView({behavior: "smooth", block: "start", inline: "center"})
        """
    return ""


@callback(
    # [Output('Timeline Graph', 'children'), Output('tm_df', 'data')], this doesnty probably like that you use it as state and then use it as output tm_df, maybe change it
    [Output("Timeline Graph", "children")],
    [
        Input("Timeline Table", "derived_virtual_data"),
        Input("Timeline Table", "derived_virtual_selected_rows"),
    ],
    State("Front_page", "data"),
    State("tm_df", "data"),
    State("year_column", "value"),
)
def update_timeline(rows, selected_rows, main_data, tm_data, year_c):
    if selected_rows is None:
        selected_rows = [0]
        return [""]
    elif selected_rows == []:
        selected_rows = [0]
        return [""]
    else:
        df_summary = (
            pd.DataFrame({"kk": ["kkk"], "kkk": [88]})
            if rows is None
            else pd.DataFrame(rows)
        )
        # df_summary3 = df_result.groupby('entityType').name.value_counts().rename_axis(['entityType','name']).reset_index(name="number_of_articles").sort_values(['number_of_articles'],ascending=False).merge(df_result[["entityType", "name","hitCount"]].groupby(['entityType', 'name']).sum('hitCount').reset_index().sort_values(['hitCount'],ascending=False), on='name', how='left').sort_values(['hitCount'],ascending=False)
        names_list = df_summary.iloc[selected_rows].Concepts.values.tolist()
        # the reserved string
        # the mapped escaped values
        # performing transformation using join and list comprehension
        names_list = [
            "".join(esc_dict.get(chr, chr) for chr in sub) for sub in names_list
        ]

        if len(palette_set) < len(names_list):
            n = 0
            while len(palette_set) < len(names_list):
                palette_set.append(palette_set[n])
                n = n + 1
        Color_scheme = {names_list[i]: palette_set[i] for i in range(len(names_list))}

        names_list = ["^" + item + "$" for item in names_list]

        # Timeline graph
        data_df = pd.DataFrame.from_dict(main_data)
        df_result = pd.DataFrame.from_dict(tm_data)

        df_plot = make_timeline_df(year_c, data_df, df_result, names_list)

        fig_time = px.line(
            df_plot,
            x=year_c,
            y="# documents",
            color="name",
            custom_data=["name"],
            color_discrete_map=Color_scheme,
        )
        fig_time.update_traces(mode="markers+lines")
        fig_time.update_xaxes(tickmode="linear")
        fig_time.update_layout(
            paper_bgcolor="rgba(25,25,25,0.5)",
            plot_bgcolor="rgba(0,0,0,0.5)",
            font_color="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True),
            # legend_x=0, legend_y=1
        )

        # fig_time.update_traces(customdata=df_plot[df_plot['name'] == yaxis_column_name]['Country Name'])
        children = [
            dcc.Graph(
                id="timeline_graph",
                figure=fig_time,
            )
        ]
        return children


#### MARK TIMELINE AND GET ARTICLES/DOCUMENTS: Finish this.
@callback(
    Output("click-data-year", "children"),
    [Input("timeline_graph", "clickData")],
    State("Front_page", "data"),
    State("tm_df", "data"),
    State("year_column", "value"),
    State("selected_columns", "value"),
)
def display_click_data(clickData, data_front, data_tm, year_c, column):
    a = pd.DataFrame.from_dict(data_front)
    b = pd.DataFrame.from_dict(data_tm)
    if type(column) != list:
        column = [column]

    df_timeline = b.merge(a[[year_c, "docID"]], "left", "docID")
    df_timeline[year_c] = df_timeline[year_c].astype(str).str[:4]

    name_entity = clickData["points"][0]["customdata"]
    year_entity = clickData["points"][0]["x"]

    d = df_timeline.loc[
        (df_timeline["name"] == name_entity[0])
        & (df_timeline[year_c] == str(year_entity))
    ]
    doc_df = a[a.docID.isin(d["docID"].tolist())]

    Mark_up(doc_df, d, column)

    tbl = doc_df.to_dict("records")
    # if "link" not in column:column.append("link")

    syn_list = b[b["name"].str.contains(name_entity[0])]["realSynList"].tolist()
    syn_unlist = sum(syn_list, [])
    string_synonyms = ", ".join(list(set(syn_unlist)))

    child = [
        dbc.Row(
            dbc.Label(
                "concept and synonyms: "
                + name_entity[0]
                + ", "
                + string_synonyms
                + " (number of documents: "
                + str(len(doc_df.index))
                + ")",
                className="synonym_display_text",
            )
        ),
        dbc.Row(
            dbc.Label(
                'Add documents to "Collected Documents" by clicking the checkbox in the first column of the table.',
                className="document_collection_label",
            )
        ),
        dash_table.DataTable(
            id="timeline_docs",
            markdown_options={"html": True},
            style_header={"backgroundColor": "rgb(30, 30, 30)"},
            style_data={
                "backgroundColor": "rgb(50, 50, 50)",
            },
            style_cell={
                "textAlign": "left",
            },
            data=tbl,
            columns=[{"name": i, "id": i, "presentation": "markdown"} for i in column],
            row_selectable="multi",
            page_size=3,
        ),
    ]
    return child


@callback(
    Output("collected_data", "data"),
    Input("bar_documents", "derived_virtual_data"),
    Input("bar_documents", "derived_virtual_selected_rows"),
)
def update_timeline(df_bar, rows_bar):
    if rows_bar is not None:
        a = pd.DataFrame(df_bar).iloc[rows_bar]
        return a.to_dict("records")
    else:
        return []


@callback(
    Output("collected_data_time", "data"),
    Input("timeline_docs", "derived_virtual_data"),
    Input("timeline_docs", "derived_virtual_selected_rows"),
)
def update_timeline(df_timeline, rows_timeline):
    if rows_timeline is not None:
        b = pd.DataFrame(df_timeline).iloc[rows_timeline]
        return b.to_dict("records")
    else:
        return []


@callback(
    Output("collected_data_overlap", "data"),
    Input("overlap_documents", "derived_virtual_data"),
    Input("overlap_documents", "derived_virtual_selected_rows"),
)
def collect_overlap(df_overlap, rows_overlap):
    if rows_overlap is not None:
        b = pd.DataFrame(df_overlap).iloc[rows_overlap]
        return b.to_dict("records")
    else:
        return []


@callback(
    Output("collection_table_div", "children"),
    Output("collected_list", "data"),
    Input("collected_data", "data"),
    Input("collected_data_time", "data"),
    Input("collected_data_overlap", "data"),
    State("selected_columns", "value"),
    State("collected_list", "data"),
)
def combine_collected(bar_data, timeline_data, overlap_data, column, collected_list):
    if type(column) != list:
        column = [column]
    if type(bar_data) != list:
        bar_data = []
    if type(timeline_data) != list:
        timeline_data = []
    if type(overlap_data) != list:
        overlap_data = []
    joined = bar_data + timeline_data + overlap_data

    for j in range(len(joined)):
        for i in column:
            joined[j][i] = re.sub(
                '<span style="background-color:rgb(.*?)">', " ", joined[j][i]
            )
            joined[j][i] = re.sub("</span>", "", joined[j][i])

    if collected_list is None:
        collected_list = []
    joined = joined + collected_list
    joined = [dict(t) for t in {tuple(d.items()) for d in joined}]

    return (
        dash_table.DataTable(
            id="collected_export",
            style_header={"backgroundColor": "rgb(30, 30, 30)"},
            style_data={
                "backgroundColor": "rgb(50, 50, 50)",
            },
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            data=joined,
            columns=[{"name": i, "id": i} for i in joined[0].keys()],
            page_size=50,
            editable=True,
            row_deletable=True,
            css=[
                {
                    "selector": ".dash-spreadsheet td div",
                    "rule": "line-height: 15px; max-height: 200px; min-height: 30px; height: auto; display: block; overflow-y: hidden;",
                }
            ],
            tooltip_data=[
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in joined
            ],
        ),
        joined,
    )


# Callbacks for tabs
@callback(
    Output("TimelineCollapse", "is_open"),
    [Input("Timeline_collapse-button", "n_clicks")],
    [State("TimelineCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("ConceptBarCollapse", "is_open"),
    [Input("ConceptBarCollapse-button", "n_clicks")],
    [State("ConceptBarCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("TopicCollapse", "is_open"),
    [Input("Topic_collapse-button", "n_clicks")],
    [State("TopicCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("CollectedCollapse", "is_open"),
    [Input("CollectedCollapse-button", "n_clicks")],
    [State("CollectedCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("OverlapCollapse", "is_open"),
    [Input("OverlapCollapse-button", "n_clicks")],
    [State("OverlapCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("SummaryCollapse", "is_open"),
    [Input("SummaryCollapse-button", "n_clicks")],
    [State("SummaryCollapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    Output("overlap_results", "children"),
    [Input("generate_overlap_button", "n_clicks")],
    [
        State("overlap_columns", "value"),
        State("overlap_concepts", "value"),
        State("tm_df", "data"),
        State("Front_page", "data"),
    ],
)
def get_overlap_docs(n, columns, concepts, tm_df, main_df):
    if n is not None:
        if type(columns) != list:
            columns = [columns]
        if type(concepts) != list:
            concepts = [concepts]
        res_df = pd.DataFrame.from_dict(tm_df)
        doc_df = pd.DataFrame.from_dict(main_df)

        result = res_df.groupby("docID").apply(
            contains_all_strings, search_list=concepts
        )
        res_df = res_df.loc[res_df["docID"].isin(result.loc[result].index.tolist())]
        doc_ids = (
            res_df.loc[
                (res_df["field"].isin(columns)) & (res_df["name"].isin(concepts))
            ]
            .loc[
                res_df.loc[
                    (res_df["field"].isin(columns)) & (res_df["name"].isin(concepts))
                ].duplicated("docID", False),
                "docID",
            ]
            .unique()
        )
        res_df = res_df.loc[
            res_df["docID"].isin(doc_ids) & res_df["name"].isin(concepts)
        ]

        # doc_ids = res_df.loc[(res_df["field"].isin(columns)) & (res_df["name"].isin(concepts))].loc[res_df.loc[(res_df["field"].isin(columns)) & (res_df["name"].isin(concepts))].duplicated("docID",False),"docID"].unique()

        doc_df = doc_df.loc[doc_df["docID"].isin(doc_ids)]
        doc_num = len(doc_df.index)
        Color_scheme = {
            res_df["name"].unique()[i]: palette_set[i]
            for i in range(len(res_df["name"].unique()))
        }
        res_df["Color"] = res_df["name"].map(Color_scheme)
        Mark_up(doc_df, res_df, columns)

        doc_df = doc_df.to_dict("records")

        syn_list = res_df[res_df["name"].isin(concepts)]["realSynList"].tolist()
        words = ", ".join(list(set(list(map(str.lower, sum(syn_list, []))))))

        overlap_result_child = html.Div(
            [
                dbc.Row(
                    dbc.Label(
                        (
                            "concept and synonyms: "
                            + words
                            + " - in "
                            + ", ".join(columns)
                            + " (number of documents: "
                            + str(doc_num)
                            + ")",
                        ),
                        className="synonym_display_text",
                    )
                ),
                dbc.Row(
                    dbc.Label(
                        'Add documents to "Collected Documents" by clicking the checkbox in the first column of the table.',
                        className="document_collection_label",
                    )
                ),
                dash_table.DataTable(
                    id="overlap_documents",
                    markdown_options={"html": True},
                    style_header={"backgroundColor": "rgb(30, 30, 30)"},
                    style_data={
                        "backgroundColor": "rgb(50, 50, 50)",
                    },
                    style_cell={
                        "textAlign": "left",
                    },
                    data=doc_df,
                    columns=[
                        {"name": i, "id": i, "presentation": "markdown"}
                        for i in columns
                    ],
                    row_selectable="multi",
                    page_size=3,
                ),
            ]
        )
        return overlap_result_child
    else:
        return ""


@callback(
    Output("download_collected_component", "data"),
    Input("export-button", "n_clicks"),
    State("collected_export", "data"),
    prevent_initial_call=True,
)
def export_data(n_clicks, data):
    if n_clicks is not None:
        # Perform the server-side export
        df = pd.DataFrame.from_dict(data)
        # Generate the CSV file
        # Send the export file to the client for download
        return dcc.send_data_frame(df.to_excel, "MAnTA_export.xlsx")


@callback(
    Output("Timeline Table", "data"),
    Input("Timeline_dropdown", "value"),
    State("tm_df", "data"),
)
def update_timeline_table(drop_val, tm_df):
    df_result = pd.DataFrame.from_dict(tm_df)
    if drop_val is None:
        pass
    elif not drop_val:
        pass
    else:
        df_result = df_result.loc[df_result["entityType"].isin(drop_val)]
    df_summary3 = (
        df_result.drop_duplicates(["name", "docID"])
        .groupby("SubjectGroup")
        .name.value_counts()
        .rename_axis(["SubjectGroup", "name"])
        .reset_index(name="# documents")
        .sort_values(["# documents"], ascending=False)
        .merge(
            df_result[["SubjectGroup", "name", "hitCount"]]
            .groupby(["SubjectGroup", "name"])
            .sum("hitCount")
            .reset_index()
            .sort_values(["hitCount"], ascending=False),
            on="name",
            how="left",
        )
        .sort_values(["# documents"], ascending=False)
        .rename(columns={"name": "Concepts", "hitCount": "Total #"})
    )

    df_summary3["Concepts"] = df_summary3["Concepts"].str.lower()
    df_summary3 = df_summary3.drop_duplicates(subset=["Concepts"])
    return df_summary3.to_dict("records")


@callback(
    Output("summary_results", "children"),
    [Input("generate_summary_button", "n_clicks")],
    [
        State("summary_columns", "value"),
        State("Front_page", "data"),
    ],
)
def generate_sumamry_action(n, columns, main_df):
    if columns is None:
        return [""]
    else:
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_colwidth", None)
        # push everything into a string
        doc_df = pd.DataFrame.from_dict(main_df)
        summary_str = "Provide a summary of the text below: \n" + doc_df[
            columns
        ].to_string(index=False)
        summary_response = send_to_completions(summary_str)
        summ_child = dash_table.DataTable(
            id="generated_summary",
            markdown_options={"html": True},
            style_header={"backgroundColor": "rgb(30, 30, 30)"},
            style_data={
                "backgroundColor": "rgb(50, 50, 50)",
            },
            style_cell={"textAlign": "left", "whiteSpace": "normal"},
            data=[{"Generated_Summary": summary_response}],
            columns=[
                {
                    "name": "Generated Summary",
                    "id": "Generated_Summary",
                    "presentation": "markdown",
                }
            ],
        )
        return summ_child


@callback(
    Output("modal", "is_open"),
    Output("modal_text", "children"),
    [
        Input("open", "n_clicks"),
        Input("close", "n_clicks"),
        Input("generate_summary_button", "n_clicks"),
    ],
    [
        State("modal", "is_open"),
        State("summary_columns", "value"),
        State("Front_page", "data"),
    ],
)
def toggle_modal(n1, n2, n3, is_open, columns, main_df):
    doc_df = pd.DataFrame.from_dict(main_df)
    summary_str = "Provide a summary of the text below: \n" + doc_df[columns].to_string(
        index=False
    )

    cost = openai_api_calculate_cost_for_prompt(summary_str)
    cost_call = (
        "The summary generation will cost the Library: "
        + str("{:.6f}".format(cost))
        + "$ \n Would you like to continue?"
    )
    if n1 or n2 or n3:

        return not is_open, cost_call
    return is_open, cost_call
