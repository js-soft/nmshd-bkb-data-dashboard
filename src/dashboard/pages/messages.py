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
                                    id="num_sent_messages_per_client$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
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
                                    id="num_received_messages_per_client$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
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
                                    id="num_recipients_per_sender_client_type$hideTestClients",
                                    options=[{"label": "Hide Test Clients?", "value": "hide_test_clients"}],
                                    value=["hide_test_clients"],
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
                                    id="message_content_size$hideTestClients",
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=["hide_test_clients"],
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
                                    id="activity_num_sent_messages$hideTestClients",
                                    options=[
                                        {"label": "Hide Test Clients?", "value": "hide_test_clients"},
                                    ],
                                    value=["hide_test_clients"],
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
