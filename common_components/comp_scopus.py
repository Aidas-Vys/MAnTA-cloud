from dash import html, dcc
import dash_bootstrap_components as dbc
from global_variables.style_formats import (
    CONTENT_STYLE,
    LPAGE_STYLE,
    TEXT_STYLE,
    CONTENT_STYLE_2,
    HR_line_styled,
)
from global_variables.vocab_groups import voc_groups, vocabs_all

slider_rank = dbc.Col(
    [
        dbc.Label("  Concepts to display:"),
        dcc.Slider(0, 20, 1, value=3, id="slider_scopus"),
    ],
    width=10,
)

Radio_button = dbc.Col(
    [
        dbc.Label("Choose one:"),
        dbc.RadioItems(
            options=[
                {"label": "# of Articles", "value": 1},
                {"label": "# of Concepts", "value": 2},
            ],
            value=1,
            inline=True,
            id="radio_button_hits_scopus",
        ),
    ]
)

search_bar_scopus = dbc.Container(
    [
        dbc.Col(
            dbc.Input(
                id="Query",
                type="text",
                placeholder='Ex.:"TITLE-ABS-KEY(Scopus AND research)"',
            ),
            width=12,
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Search Scopus",
                        id="ScopusSearch",
                        class_name="mb-3",
                        color="secondary",
                    )
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Row(
                                dcc.Link(
                                    children="Scopus Search Engine",
                                    href="https://www.scopus.com/search/form.uri?display=advanced",
                                    target="_blank",
                                    style={"margin-left": "8px"},
                                )
                            ),
                            dbc.Row(
                                dcc.Link(
                                    children="Search help",
                                    href="https://service.elsevier.com/app/answers/detail/a_id/34325/supporthub/scopus/related/1/",
                                    target="_blank",
                                    style={"margin-left": "8px"},
                                )
                            ),
                            dbc.Row(
                                dcc.Link(
                                    children="Scopus Cheat Sheet",
                                    href="https://novozymes.sharepoint.com/sites/Library/Shared%20Documents/Cheat%20Sheets.pdf#page=12",
                                    target="_blank",
                                    style={"margin-left": "8px"},
                                )
                            ),
                        ],
                        style={"text-align": "right"},
                    )
                ),
            ]
        ),
    ],
)

landing_p_scopus = dbc.Container(
    [
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1("MAnTA"),
                                html.H6("Multiple Analysis Text mining Application"),
                                html.H4(
                                    "Search Scopus:", style={"font-style": "italic"}
                                ),
                            ]
                        ),
                        dbc.Col(
                            html.Div(html.Img(src="assets/owlWhite.png")),
                            style={"text-align": "right"},
                        ),
                    ]
                ),
                search_bar_scopus,
            ],
            width=12,
        )
    ],
    className="landing_page",
)


tab1_scopus = dcc.Loading(
    id="loading_import",
    children=html.Pre(
        html.Div(
            [
                dbc.Row(
                    [
                        html.Div(id="output-data-upload-scopus"),
                    ],
                    style={"overflow": "inherit", "max-width": "100%"},
                ),
                dbc.Row(
                    html.Div(id="Vocab_and_column-scopus", className="content_style")
                ),
            ],
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
                        id="Topic_collapse-button_scopus",
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
                    html.Div(id="topic_overview_scopus"),
                    dbc.Col(
                        html.Div(
                            [
                                dbc.Button(
                                    "Help",
                                    id="infobtn_overview_scopus",
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
                                    id="tooltip_overview_scopus",
                                    is_open=False,
                                    target="infobtn_overview_scopus",
                                    trigger=None,
                                ),
                            ],
                            style={"text-align": "left", "margin-top": "1rem"},
                        )
                    ),
                    html.Br(),
                ]
            ),
            id="TopicCollapse_scopus",
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
                        id="ConceptBarCollapse-button_scopus",
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
                dbc.Row(id="concept_analysis_scopus"),
                dbc.Row(
                    html.Div(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Help",
                                            id="infobtn_bar_scopus",
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
                                            id="tooltip_bar_scopus",
                                            is_open=False,
                                            target="infobtn_bar_scopus",
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
                                        id="click-data_scopus",
                                        style={"overflowY": "auto"},
                                    )
                                ],
                                type="cube",
                            ),
                        ],
                        style={"color": "white"},
                    )
                ),
            ],
            id="ConceptBarCollapse_scopus",
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
                        id="Timeline_collapse-button_scopus",
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
                            dbc.Col(id="timeline_analysis_scopus", width=3),
                            dbc.Col(html.Div(id="Timeline Graph_scopus")),
                        ]
                    )
                ),
                html.Div(
                    [
                        dbc.Button(
                            "Help",
                            id="infobtn_timeline_scopus",
                            color="warning",
                            class_name="me-0",
                            n_clicks=0,
                        ),
                        dbc.Tooltip(
                            dcc.Markdown(
                                """
                                        **Timeline analysis** shows the usage and frequency of concepts through the years.\n
                                        **Select the column "Cover Date"**, if this is not available the analysis will not work.\n
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
                            id="tooltip_timeline_scopus",
                            is_open=False,
                            target="infobtn_timeline_scopus",
                            trigger=None,
                        ),
                    ],
                    style={"text-align": "left", "margin-top": "1rem"},
                ),
                html.Br(),
                dcc.Loading(
                    children=[
                        html.Pre(
                            id="click-data-year_scopus", style={"overflowY": "auto"}
                        )
                    ],
                    type="cube",
                ),
                # this is for collapsing:
            ],
            id="TimelineCollapse_scopus",
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
                        id="OverlapCollapse-button_scopus",
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
                dbc.Row(id="overlap_analysis_scopus"),
                dbc.Row(id="overlap_results_scopus"),
                html.Br(),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_overlap_scopus",
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
                                id="tooltip_overlap_scopus",
                                is_open=False,
                                target="infobtn_overlap_scopus",
                                trigger=None,
                            ),
                        ],
                        style={"text-align": "left", "margin-top": "1rem"},
                    )
                ),
                html.Br(),
            ],
            id="OverlapCollapse_scopus",
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
                        id="CollectedCollapse-button_scopus",
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
                dbc.Row(id="collected_documents_scopus"),
                html.Br(),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_collect_scopus",
                                color="warning",
                                class_name="me-0",
                                n_clicks=0,
                            ),
                            # Serverside Export
                            dbc.Button(
                                "Export as Excel",
                                id="export-button_scopus",
                                n_clicks=0,
                                style={"margin-left": "1rem"},
                                color="secondary",
                            ),
                            dbc.Tooltip(
                                dcc.Markdown(
                                    """
                                            **Collected Documents** - review your collected documents from previous analyses.\n 
                                            **Clicking the "x"** symbol will remove the corresponding row from the table.\n
                                            By **clicking "Export"** at the top left corner the table will be downloaded to your computer in Excel format.\n
                                            **For more information visit the Wiki:**\n
                                            https://gitlab.nzcorp.net/library/patents_textmining_app/-/wikis/MAnTA-Wiki
                                            """,
                                    link_target="_blank",
                                    dangerously_allow_html=True,
                                ),
                                id="tooltip_collect_scopus",
                                is_open=False,
                                target="infobtn_collect_scopus",
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
            id="CollectedCollapse_scopus",
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
                        id="SummaryCollapse-button_scopus",
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
                    [html.Div(id="summary_scopus")],
                ),
                dbc.Row(
                    [html.Div(id="summary_results_scopus")],
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Button(
                                "Help",
                                id="infobtn_summary_scopus",
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
                                id="tooltip_summary_scopus",
                                is_open=False,
                                target="infobtn_summary_scopus",
                                trigger=None,
                            ),
                        ],
                        style={"text-align": "left", "margin-top": "1rem"},
                    )
                ),
                html.Br(),
            ],
            is_open=False,
            id="SummaryCollapse_scopus",
        ),
    ]
)

tab2_scopus = dbc.Container(
    [
        dbc.Row(
            html.H2(
                children="Analysis:",
                id="analysisH2_scopus",
                style={"display": "none", "margin-left": "1rem"},
            )
        ),
        dbc.Row(
            html.Div(
                children=Summary_child,
                id="summary_display_scopus",
                style={"display": "none"},
            )
        ),
        dbc.Row(
            html.Div(
                children=overview_child,
                id="topic_overview_scopus_display",
                style={"display": "none"},
            )
        ),
        dbc.Col(
            [
                dbc.Row(
                    html.Div(
                        id="concept_analysis_scopus_display",
                        children=concept_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="overlap_analysis_scopus_display",
                        children=Overlap_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="timeline_analysis_scopus_display",
                        children=Timeline_child,
                        style={"display": "none"},
                    )
                ),
                dbc.Row(
                    html.Div(
                        id="collected_documents_scopus_display",
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


# time_test_lay = dbc.Row(html.Div(id="timeline_analysis_scopus_display",
#                              children=Timeline_child,
#                              style={"display":"none"}),
#                     style={"margin-left": "0.5rem", "margin-right":"0.5rem"})

Vocab_groups_drop = dcc.Dropdown(
    id="GroupSelect_scopus",
    options=[{"label": k, "value": voc_groups[k]} for k in voc_groups],
    multi=True,
    placeholder="Select 1-2 at a time",
    clearable=True,
)
Vocabs_drop = dcc.Dropdown(
    id="VocabSelect_scopus",
    options=[{"label": k, "value": vocabs_all[k]} for k in vocabs_all],
    placeholder="Select any number of subjects",
    multi=True,
    clearable=True,
)
