from dash import html

HR_STYLE = {"width": "100%", "color": "white"}


CONTENT_STYLE = {
    "backgroundColor": "rgb(0,0,0,0.50)",
}

CONTENT_STYLE_2 = {
    "backgroundColor": "rgb(0,0,0,0.50)",
    "margin-top": "1rem",
    "margin-left": "10vh",
    "margin-right": "10vh",
}


ANALYSIS_STYLE = {
    "backgroundColor": "rgb(0,0,0,0.50)",
}

LPAGE_STYLE = {
    "backgroundColor": "rgb(0,0,0,0.50)",
    "margin-top": "40vh",
    "margin-bottom": "50vh",
}
TEXT_STYLE = {"color": "rgb(255, 255, 255)", "font-family": "monospace"}

HR_line_styled = html.Hr(style=HR_STYLE)
