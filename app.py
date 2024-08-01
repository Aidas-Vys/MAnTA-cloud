from dash import Dash, html
import dash_bootstrap_components as dbc
import dash
import sys

from prometheus_flask_exporter import PrometheusMetrics


dash_app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    # use_pages=True,
)  # initialising dash app

server = dash_app.server

# dash_app.layout = html.Div(dash.page_container, className="overlay")
dash_app.layout = html.Div(html.H1("MAnTAUUUU"))


if __name__ == "__main__":
    # app.run_server(debug=True, host="0.0.0.0", port=8051)
    # dash_app.run_server(debug=True, host="0.0.0.0", port=8052)
    dash_app.run_server(debug=True)
