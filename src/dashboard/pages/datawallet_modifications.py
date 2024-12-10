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
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-datawallet-modifications"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Number of Datawallet Modifications per Identity"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_datawallet_modifications$graph"),
            ],
            id="num_datawallet_modifications$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "size-of-datawallet-modifications"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Size of Datawallet Modifications"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="size_of_datawallet_modifications$graph"),
            ],
            id="size_of_datawallet_modifications$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "type-of-datawallet-modifications"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Type of Datawallet Modifications"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="type_of_datawallet_modifications$graph"),
            ],
            id="type_of_datawallet_modifications$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "collection-of-datawallet-modifications"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Collection of Datawallet Modifications"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="collection_of_datawallet_modifications$graph"),
            ],
            id="collection_of_datawallet_modifications$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "payload-category-of-datawallet-modifications"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Distribution of Payload Category of Datawallet Modifications"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="payload_category_of_datawallet_modifications$graph"),
            ],
            id="payload_category_of_datawallet_modifications$div",
            className="graph-div",
        ),
    ]
)
