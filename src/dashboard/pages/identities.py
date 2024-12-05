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
                                    id="num_identities_per_client$checkbox",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Identities per Backbone Client"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_identities_per_client$graph"),
            ],
            id="num_identities_per_client$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="activity_identity_creations$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Identity Creations per Day"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="activity_identity_creations$graph"),
            ],
            id="activity_identity_creations$div",
            className="graph-div",
        ),
    ]
)
