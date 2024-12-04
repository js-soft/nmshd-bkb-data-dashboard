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
                                    id="forcegraph$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Relationship Network"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                html.Iframe(
                    # src of iframe is controlled through callbacks.
                    id="forcegraph$iframe",
                    style={"height": "80vh", "width": "100%"},
                ),
            ],
            id="forcegraph$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="relationship_status_distribution$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Relationship Status Distribution"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="relationship_status_distribution$graph"),
            ],
            id="relationship_status_distribution$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="relationship_duration_pending$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Duration of Relationships in 'Pending' State"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="relationship_duration_pending$graph"),
            ],
            id="relationship_duration_pending$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="num_peers_per_identity$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Number of Peers per Identity"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_peers_per_identity$graph"),
            ],
            id="num_peers_per_identity$div",
            className="graph-div",
        ),
    ]
)
