import dash
from dash import html, dcc, callback, Output, Input, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd  # remove when done

# df = pd.read_csv("scopus_test.csv")  # remove when done testing
# df_dict = df.to_dict("records")  # remove when done
dash.register_page(__name__, path="/")

layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H1("MAnTA"),
                                                html.H6(
                                                    "Multiple Analysis Text mining Application"
                                                ),
                                                html.H3(
                                                    "Select data import method:",
                                                    style={"font-style": "italic"},
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            html.Div(
                                                html.Img(src="assets/owlWhite.png"),
                                                style={"text-align": "right"},
                                            ),
                                            width=6,
                                        ),
                                    ]
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Import Files",
                                                href="http://127.0.0.1:8052/manta-filesimport",  # testing
                                                # href="http://spidsmus.sdma.nzcorp.net:8051/manta-filesimport",  # actual location
                                                className="me-1",
                                                style={
                                                    "lineHeight": "30px",
                                                    "borderWidth": "5px",
                                                    "borderStyle": "groove",
                                                    "borderRadius": "5px",
                                                    "textAlign": "center",
                                                    "margin": "0px",
                                                    "margin-bottom": "10px",
                                                    "background-color": "rgb(180, 180, 180)",
                                                    "color": "black",
                                                    "font-weight": "850",
                                                    "border-color": "white",
                                                    "font-family": "monospace",
                                                    "width": "100%",
                                                },
                                            ),
                                            width=6,
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Search Scopus",
                                                href="http://127.0.0.1:8052/manta-scopus",  # for testing
                                                # href="http://spidsmus.sdma.nzcorp.net:8051/manta-scopus",  # actual location
                                                className="me-1",
                                                style={
                                                    "lineHeight": "30px",
                                                    "borderWidth": "5px",
                                                    "borderStyle": "groove",
                                                    "borderRadius": "5px",
                                                    "textAlign": "center",
                                                    "margin": "0px",
                                                    "margin-bottom": "10px",
                                                    "background-color": "rgb(180, 180, 180)",
                                                    "color": "black",
                                                    "font-weight": "850",
                                                    "border-color": "white",
                                                    "font-family": "monospace",
                                                    "width": "100%",
                                                },
                                            ),
                                            width=6,
                                        ),
                                    ]
                                )
                                ########################################
                                ,
                                #######################################
                            ]
                        ),
                        dbc.Row(
                            html.Div(
                                [
                                    dbc.Button(
                                        "Help",
                                        id="infobtn",
                                        color="warning",
                                        class_name="me-0",
                                        n_clicks=0,
                                    ),
                                    dbc.Tooltip(
                                        dcc.Markdown(
                                            """
                **Import Files** button will let you text mine  .csv or .xlsx documents saved on your machine.\n
                **Search Scopus** button will let you search the Scopus scientific literature database by using a search query.\n
                **For more information visit the Wiki:**\n
                https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                """,
                                            link_target="_blank",
                                            dangerously_allow_html=True,
                                        ),
                                        id="tooltip",
                                        is_open=False,
                                        target="infobtn",
                                        trigger=None,
                                    ),
                                ],
                                style={"text-align": "left"},
                            )
                        ),
                    ],
                    width=12,
                )
            ],
            style={
                "width": "105vw",
                "backgroundColor": "rgb(0,0,0,0.50)",
                "margin-top": "40vh",
                "margin-bottom": "50vh",
            },
        )
    ]
)


@callback(
    Output("tooltip", "is_open"),
    [Input("infobtn", "n_clicks")],
    [State("tooltip", "is_open")],
)
def toggle_tooltip(n, is_open):
    if n:
        return not is_open
    return is_open
