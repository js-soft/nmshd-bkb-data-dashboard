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
                                    # id="num_datawallet_modifications$hideTestClients",
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-datawallet-modifications"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
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
                # dcc.Graph(id="num_datawallet_modifications$graph"),
                dcc.Graph(id={"type": "graph", "plot": "num-datawallet-modifications"}),
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
                                    # id="size_of_datawallet_modifications$hideTestClients",
                                    id={"type": "hide-test-clients-checkbox", "plot": "size-of-datawallet-modifications"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
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
                dcc.Graph(id={"type": "graph", "plot": "size-of-datawallet-modifications"}),
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
                                    id="type_of_datawallet_modifications$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
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
                                    id="collection_of_datawallet_modifications$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
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
                                    id="payload_category_of_datawallet_modifications$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"] if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else [],
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
