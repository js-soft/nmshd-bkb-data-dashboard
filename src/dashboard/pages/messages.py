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
                                    # id="num_sent_messages_per_client$hideTestClients",
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-sent-messages-per-client"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Sent Messages per Backbone Client"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_sent_messages_per_client$graph"),
            ],
            id="num_sent_messages_per_client$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-received-messages-per-client"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Received Messages per Backbone Client"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_received_messages_per_client$graph"),
            ],
            id="num_received_messages_per_client$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "num-recipients-per-sender-client-type"},
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Number of Recipients of Sent Messages"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="num_recipients_per_sender_client_type$graph"),
            ],
            id="num_recipients_per_sender_client_type$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "message-content-size"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Size of Message Content"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="message_content_size$graph"),
            ],
            id="message_content_size$div",
            className="graph-div",
        ),
        html.Div(
            [
                html.Div(
                    children=[
                        _get_dropdown(
                            children=[
                                dcc.Checklist(
                                    id={"type": "hide-test-clients-checkbox", "plot": "activity-num-sent-messages"},
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=[],
                                ),
                            ]
                        ),
                        html.Span(
                            children=["Messages Sent over time"],
                            className="plot-title",
                        ),
                    ],
                    className="plot-header",
                ),
                dcc.Graph(id="activity_num_sent_messages$graph"),
            ],
            id="activity_num_sent_messages$div",
            className="graph-div",
        ),
    ]
)
