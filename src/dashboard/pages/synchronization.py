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
                                    id="sync_errors$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Synchronization Errors over Time"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="sync_errors$graph"),
            ],
            id="sync_errors$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="type_of_external_events$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["External Event Types"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="type_of_external_events$graph"),
            ],
            id="type_of_external_events$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="num_external_events_per_sync_run$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of the number of External Events Per Sync Run"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_external_events_per_sync_run$graph"),
            ],
            id="num_external_events_per_sync_run$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="activity_external_events$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Sync runs over time"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="activity_external_events$graph"),
            ],
            id="activity_external_events$div",
            className="graph-div",
        ),
    ]
)
