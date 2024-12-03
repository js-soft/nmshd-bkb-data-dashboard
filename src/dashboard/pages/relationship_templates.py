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
                                    id="size_of_relationship_templates$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Size of Relationship Templates"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="size_of_relationship_templates$graph"),
            ],
            id="size_of_relationship_templates$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="num_relationship_templates_per_identity$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Number of Relationship Templates Created per Identity"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_relationship_templates_per_identity$graph"),
            ],
            id="num_relationship_templates_per_identity$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="num_max_rel_templ_allocations$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Max. Number of Relationship Template Allocations"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_max_rel_templ_allocations$graph"),
            ],
            id="num_max_rel_templ_allocations$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="rlt_time_until_first_usage$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Time until first usage of Relationship Template"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="rlt_time_until_first_usage$graph"),
            ],
            id="rlt_time_until_first_usage$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id="rlt_validity_period$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Validity Period of Relationship Templates"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="rlt_validity_period$graph"),
            ],
            id="rlt_validity_period$div",
            className="graph-div",
        ),
    ],
)
