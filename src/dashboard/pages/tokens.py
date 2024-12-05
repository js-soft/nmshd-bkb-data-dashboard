import dash
from dash import dcc, html

from src import config
from src.dashboard import _get_dropdown

dash.register_page(__name__)
layout = html.Div(
    children=[
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="num_tokens_per_identity$hideTestClients",
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"}
                                    ],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Number of Tokens per Identity"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_tokens_per_identity$graph"),
            ],
            id="num_tokens_per_identity$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="token_size$hideTestClients",
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"}
                                    ],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Token Size"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="token_size$graph"),
            ],
            id="token_size$div",
            className="graph-div",
        ),
    ]
)
