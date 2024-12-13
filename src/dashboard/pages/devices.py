import dash
from dash import dcc, html

from src.dashboard import _get_dropdown
from src import config

dash.register_page(__name__)


layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-devices-per-identity"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Devices per Identity"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id={"type": "graph", "plot": "num-devices-per-identity"}),
            ],
            id="num_devices_per_identity$div",
            className="graph-div",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "device-type-distribution"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Device Push Channel Type (PNS Prefix)"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id={"type": "graph", "plot": "device-type-distribution"}),
            ],
            id="device_type_distribution$div",
            className="graph-div",
        ),
    ]
)
