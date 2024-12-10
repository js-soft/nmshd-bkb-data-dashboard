import dash
from dash import dcc, html

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
                                    id={"type": "hide-test-clients-checkbox", "plot": "forcegraph"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
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
                                    id={"type": "hide-test-clients-checkbox", "plot": "relationship-status-distribution"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
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
                                    id={"type": "hide-test-clients-checkbox", "plot": "relationship-duration-pending"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
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
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-peers-per-identity"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
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
