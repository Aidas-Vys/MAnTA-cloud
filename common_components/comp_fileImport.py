from global_variables.style_formats import (
    LPAGE_STYLE,
    HR_line_styled,
    ANALYSIS_STYLE,
    HR_STYLE,
    CONTENT_STYLE,
    CONTENT_STYLE_2,
)
import dash_bootstrap_components as dbc
from dash import html, dcc
from global_variables.vocab_groups import voc_groups, vocabs_all

slider_rank = dbc.Col(
    [dbc.Label("  Concepts to display:"), dcc.Slider(0, 20, 1, value=3, id="slider")],
    width=10,
)

Radio_button = dbc.Col(
    [
        dbc.Label("Choose one:"),
        dbc.RadioItems(
            options=[
                {"label": "# of Documents", "value": 1},
                {"label": "# of Concepts", "value": 2},
            ],
            value=1,
            inline=True,
            id="radio_button_hits",
        ),
    ]
)

upload_element = html.Div(
    [
        dcc.Upload(
            id="upload",
            children=html.Div(
                [
                    html.A(
                        ["Drag and Drop", html.Br(), "or Click to Select Files"],
                        style={"font-family": "monospace", "font-weight": "850"},
                    )
                ]
            ),
            style={
                "lineHeight": "30px",
                "borderWidth": "5px",
                "borderStyle": "groove",
                "borderRadius": "5px",
                "textAlign": "center",
                "background-color": "rgb(180, 180, 180)",
                "color": "black",
                "font-weight": "700",
                "border-color": "white",
                "margin-bottom": "10px",
            },
            multiple=True,
        )
    ]
)

landing_p = dbc.Container(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1("MAnTA"),
                                html.H6("Multiple Analysis Text mining Application"),
                                html.H3(
                                    "Import a file below (.xlsx/.csv):",
                                    style={"font-style": "italic"},
                                ),
                            ]
                        ),
                        dbc.Col(
                            html.Div(html.Img(src="assets/owlWhite.png")),
                            style={"text-align": "right"},
                        ),
                    ]
                ),
                dbc.Row([upload_element]),
            ],
            width=12,
            style={"height": "auto"},
        )
    ],
    className="landing_page",
)

tab1 = dcc.Loading(
    id="loading_import_scopus",
    children=html.Pre(
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Div(id="output-data-upload")),
                    ],
                    style={"overflow": "inherit", "max-width": "100%"},
                ),
                dbc.Row(html.Div(id="Vocab_and_column", className="content_style")),
            ]
        )
    ),
    type="cube",
)


overview_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Overview",
                        id="Topic_collapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                ),
            ]
        ),
        dbc.Collapse(
            dbc.Row(
                [
                    html.Div(id="topic_overview"),
                    dbc.Col(
                        html.Div(
                            [
                                dbc.Button(
                                    "Help",
                                    id="infobtn_overview",
                                    color="warning",
                                    class_name="me-0",
                                    n_clicks=0,
                                ),
                                dbc.Tooltip(
                                    dcc.Markdown(
                                        """
                                                **Topic distribution overview** showcases the pecentage of identified concepts falling under specific subjects.\n
                                                Navigate and Save plots/graphs by using the tools in the top right corner of each plot/graph.\n
                                                **For more information visit the Wiki:**\n
                                                https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                                """,
                                        link_target="_blank",
                                        dangerously_allow_html=True,
                                    ),
                                    id="tooltip_overview",
                                    is_open=False,
                                    target="infobtn_overview",
                                    trigger=None,
                                ),
                            ],
                            style={"text-align": "left", "margin-top": "1rem"},
                        )
                    ),
                    html.Br(),
                ]
            ),
            id="TopicCollapse",
            is_open=False,
        ),
    ]
)

concept_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Concept frequency analysis",
                        id="ConceptBarCollapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                )
            ]
        ),
        dbc.Collapse(
            [
                dbc.Row([Radio_button, slider_rank]),
                dbc.Row(id="concept_analysis"),
                dbc.Row(
                    html.Div(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Help",
                                            id="infobtn_bar",
                                            color="warning",
                                            class_name="me-0",
                                            n_clicks=0,
                                        ),
                                        dbc.Tooltip(
                                            dcc.Markdown(
                                                """
                                                **Concept frequency analysis** - columns represent detected concepts, colors represent different subjects and different graphs represent different text mined columns. \n
                                                Each graph shows the most frequent concepts per subject within the field.\n
                                                Adjust the number of most frequent concepts showed by **using the slider** above the graphs. \n
                                                Select the concept frequency representation by number of documents they are detected in or by their total number by **using the two selection marks**. \n
                                                **Clicking the graph bars** will find the corresponding documents and highlight the concept.\n
                                                You can review the selected documents and **add them to "Collected Documents"** by clicking the checkbox in the first column of the table.\n
                                                Navigate and Save plots/graphs by using the tools in the top right corner of each plot/graph.\n
                                                **For more information visit the Wiki:**\n
                                                https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                                """,
                                                link_target="_blank",
                                                dangerously_allow_html=True,
                                            ),
                                            id="tooltip_bar",
                                            is_open=False,
                                            target="infobtn_bar",
                                            trigger=None,
                                        ),
                                    ],
                                    style={"text-align": "left", "margin-top": "1rem"},
                                )
                            ),
                            html.Br(),
                            HR_line_styled,
                            dcc.Loading(
                                children=[
                                    html.Pre(
                                        id="click-data", style={"overflowY": "auto"}
                                    )
                                ],
                                type="cube",
                            ),
                        ],
                        style={"color": "white"},
                    )
                ),
            ],
            id="ConceptBarCollapse",
            is_open=False,
        ),
    ]
)

Timeline_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Timeline analysis",
                        id="Timeline_collapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                ),
            ]
        ),
        dbc.Collapse(
            [
                html.Div(
                    dbc.Row(
                        [
                            dbc.Col(id="timeline_analysis", width=3),
                            dbc.Col(html.Div(id="Timeline Graph")),
                        ]
                    )
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Help",
                            id="infobtn_timeline",
                            color="warning",
                            class_name="me-0",
                            n_clicks=0,
                        ),
                        dbc.Tooltip(
                            dcc.Markdown(
                                """
                                        **Timeline analysis** shows the usage and frequency of concepts through the years.\n
                                        **Select a year/date column**, if this is not available the analysis will fail.\n
                                        Select any number of the detected concepts from the table by **checking the square box** with a click in the first column.\n
                                        **Clicking the graph** will find the corresponding documents from the specific year containing the concept of interest.\n
                                        You can review the documents and add them to "Collected Documents" by **clicking the checkbox** in the first column.\n
                                        Navigate and Save plots/graphs by using the tools in the top right corner of each plot/graph.\n
                                        **For more information visit the Wiki:**\n
                                        https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                        """,
                                link_target="_blank",
                                dangerously_allow_html=True,
                            ),
                            id="tooltip_timeline",
                            is_open=False,
                            target="infobtn_timeline",
                            trigger=None,
                        ),
                    ],
                    style={"text-align": "left", "margin-top": "1rem"},
                ),
                html.Br(),
                dcc.Loading(
                    children=[
                        html.Pre(id="click-data-year", style={"overflowY": "auto"})
                    ],
                    type="cube",
                ),
                # this is for collapsing:
            ],
            id="TimelineCollapse",
            is_open=False,
        ),
    ]
)

Overlap_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Concept Overlap",
                        id="OverlapCollapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                ),
            ]
        ),
        dbc.Collapse(
            [
                dbc.Row(id="overlap_analysis"),
                dbc.Row(id="overlap_results"),
                html.Br(),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_overlap",
                                color="warning",
                                class_name="me-0",
                                n_clicks=0,
                            ),
                            dbc.Tooltip(
                                dcc.Markdown(
                                    """
                                        **Concept overlap** shows detects documents with at least 2 selected concepts used in the same field.\n
                                        *e.g.: if "Title" is selected together with "enzyme" and "diet", the overlap will find documents that have both "enzyme" and "diet" in its title.*\n
                                        **Select the column/-s that the concepts should appear in**, available columns will be the same ones selected in the analysis setup in the begining.\n
                                        **Select at least 2 concepts that need to appear together** - the list is searchable, just start typing. 
                                        You can review the documents and add them to "Collected Documents" by **clicking the checkbox** in the first column.\n
                                        **For more information visit the Wiki:**\n
                                        https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                            """,
                                    link_target="_blank",
                                    dangerously_allow_html=True,
                                ),
                                id="tooltip_overlap",
                                is_open=False,
                                target="infobtn_overlap",
                                trigger=None,
                            ),
                        ],
                        style={"text-align": "left", "margin-top": "1rem"},
                    )
                ),
                html.Br(),
            ],
            id="OverlapCollapse",
            is_open=False,
        ),
    ]
)


Collected_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Collected Documents",
                        id="CollectedCollapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                ),
            ]
        ),
        dbc.Collapse(
            [
                dbc.Row(id="collected_documents"),
                html.Br(),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_collect",
                                color="warning",
                                class_name="me-0",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Export as Excel",
                                id="export-button",
                                n_clicks=0,
                                style={"margin-left": "1rem"},
                                color="secondary",
                            ),
                            dbc.Tooltip(
                                dcc.Markdown(
                                    """
                                            **Collected Documents** - here you can review your collected documents from previous analyses.\n 
                                            **Clicking the "x"** symbol will remove the corresponding row from the table.\n
                                            By **clicking "Export"** at the top left corner the table will be downloaded to your computer in Excel format.\n
                                            **For more information visit the Wiki:**\n
                                            https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                            """,
                                    link_target="_blank",
                                    dangerously_allow_html=True,
                                ),
                                id="tooltip_collect",
                                is_open=False,
                                target="infobtn_collect",
                                trigger=None,
                            ),
                        ],
                        style={
                            "text-align": "left",
                            "margin-top": "1rem",
                            "margin-bottom": "25vh",
                        },
                    )
                ),
                html.Br(),
            ],
            id="CollectedCollapse",
            is_open=False,
        ),
    ]
)


Summary_child = html.Div(
    [
        HR_line_styled,
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Summary Generation",
                        id="SummaryCollapse-button",
                        class_name="mb-3",
                        color="secondary",
                        n_clicks=0,
                        style={"width": "inherit"},
                    )
                ),
            ]
        ),
        dbc.Collapse(
            [
                dbc.Row(
                    [html.Div(id="summary")],
                ),
                dbc.Row(
                    [html.Div(id="summary_results")],
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_summary",
                                color="warning",
                                class_name="me-0",
                                n_clicks=0,
                            ),
                            dbc.Tooltip(
                                dcc.Markdown(
                                    """
                                                **Topic distribution overview** showcases the pecentage of identified concepts falling under specific subjects.\n
                                                Navigate and Save plots/graphs by using the tools in the top right corner of each plot/graph.\n
                                                **For more information visit the Wiki:**\n
                                                https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                                """,
                                    link_target="_blank",
                                    dangerously_allow_html=True,
                                ),
                                id="tooltip_summary",
                                is_open=False,
                                target="infobtn_summary",
                                trigger=None,
                            ),
                        ],
                        style={"text-align": "left", "margin-top": "1rem"},
                    )
                ),
                html.Br(),
            ],
            is_open=False,
            id="SummaryCollapse",
        ),
    ]
)


tab2 = dbc.Container(
    [
        html.H2(
            children="Analysis:",
            id="analysisH2",
            style={"display": "none", "margin-left": "1rem"},
        ),
        dbc.Row(
            html.Div(
                children=Summary_child,
                id="summary_display",
                style={"display": "none"},
            )
        ),
        dbc.Row(
            html.Div(
                children=overview_child,
                id="topic_overview_display",
                style={"display": "none"},
            )
        ),
        dbc.Col(
            [
                dbc.Row(
                    html.Div(
                        id="concept_analysis_display",
                        children=concept_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="overlap_analysis_display",
                        children=Overlap_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="timeline_analysis_display",
                        children=Timeline_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="collected_documents_display",
                        style={"display": "none"},
                        children=Collected_child,
                    )
                ),
            ],
            width=12,
        ),
    ],
    className="content_style",
    fluid=True,
)

# collected_documents = html.Div(id="collected_articles")

Vocab_groups_drop = dcc.Dropdown(
    id="GroupSelect",
    options=[{"label": k, "value": voc_groups[k]} for k in voc_groups],
    multi=True,
)

Vocabs_drop = dcc.Dropdown(
    id="VocabSelect",
    options=[{"label": k, "value": vocabs_all[k]} for k in vocabs_all],
    multi=True,
)
