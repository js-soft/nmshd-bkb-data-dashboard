from contextlib import contextmanager
from typing import Any

import dash
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html
from flask import render_template, request, Flask, redirect
import sqlalchemy

from src import network
from src import plotly_plots as plots
from src import queries


class DashboardApp:
    def __init__(self, cnxn_pool: sqlalchemy.QueuePool):
        self._cnxn_pool = cnxn_pool

        # We explicitly set up a flask server to override dash's default
        # root-url route for which there seems no good way to reconfigure it
        # once it has been set.
        #
        # We redirect "/" to the first page in our page registry.
        flask = Flask(
            __name__,
            static_url_path="/static",
            static_folder="./static",
            template_folder="./templates",
        )
        flask.add_url_rule(
            "/",
            view_func=lambda: redirect(next(iter(dash.page_registry.values()))["relative_path"]),
        )

        self._app = Dash(
            use_pages=True,
            pages_folder="./pages",
            assets_folder="./static/assets",
            server=flask,
        )
        self._app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.H1(id="dashboard-title", children="Backbone Data Dashboard"),
                html.Div(
                    id="page-links",
                    children=[
                        dcc.Link(
                            html.Div(
                                children=[page["name"]],
                                className="page-link",
                                id=f"page-link-{page["relative_path"].lstrip("/").replace("/", "-")}",
                            ),
                            href=page["relative_path"],
                        )
                        for page in dash.page_registry.values()
                    ],
                ),
                html.Div(dash.page_container, className="page-container"),
            ]
        )

        # HACK: DRY; siehe oben
        # List of page paths for use in the callback
        page_paths = [page["relative_path"] for page in dash.page_registry.values()]
        # Generate Output objects for each link
        outputs = [Output(f"page-link-{path.lstrip("/").replace('/', '-')}", "className") for path in page_paths]

        @self._app.callback(
            outputs,
            Input("url", "pathname"),
        )
        def update_active_links(pathname):
            classnames = []
            for path in page_paths:
                if path == pathname:
                    classnames.append("page-link active")  # Active page style
                else:
                    classnames.append("page-link")  # Inactive page style
            return classnames

        self._setup_callbacks()
        self._app.server.add_url_rule("/forcegraph.html", view_func=self.render_forcegraph)

    @contextmanager
    def _grab_cnxn(self):
        cnxn = self._cnxn_pool.connect()
        yield cnxn
        cnxn.close()

    def _setup_callbacks(self):
        @self._app.callback(
            Output("num_max_rel_templ_allocations$graph", "figure"),
            Input("num_max_rel_templ_allocations$hideTestClients", "value"),
        )
        def num_max_rel_templ_allocations(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_max_rel_templ_allocations(cnxn, hide)
            return plots.num_max_rel_templ_allocations(df)

        @self._app.callback(
            Output("size_of_file_contents$graph", "figure"),
            Input("size_of_file_contents$hideTestClients", "value"),
        )
        def size_of_file_contents(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_file_contents(cnxn, hide)
            return plots.size_of_file_contents(df)

        @self._app.callback(
            Output("num_external_events_per_sync_run$graph", "figure"),
            Input("num_external_events_per_sync_run$hideTestClients", "value"),
        )
        def num_external_events_per_sync_run(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_external_events_per_sync_run(cnxn, hide)
            return plots.num_external_events_per_sync_run(df)

        @self._app.callback(
            Output("type_of_external_events$graph", "figure"),
            Input("type_of_external_events$hideTestClients", "value"),
        )
        def type_of_external_events(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.type_of_external_events(cnxn, hide)
            return plots.type_of_external_events(df)

        @self._app.callback(
            Output("payload_category_of_datawallet_modifications$graph", "figure"),
            Input("payload_category_of_datawallet_modifications$hideTestClients", "value"),
        )
        def payload_category_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.payload_category_of_datawallet_modifications(cnxn, hide)
            return plots.payload_category_of_datawallet_modifications(df)

        @self._app.callback(
            Output("collection_of_datawallet_modifications$graph", "figure"),
            Input("collection_of_datawallet_modifications$hideTestClients", "value"),
        )
        def collection_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.collection_of_datawallet_modifications(cnxn, hide)
            return plots.collection_of_datawallet_modifications(df)

        @self._app.callback(
            Output("type_of_datawallet_modifications$graph", "figure"),
            Input("type_of_datawallet_modifications$hideTestClients", "value"),
        )
        def type_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.type_of_datawallet_modifications(cnxn, hide)
            return plots.type_of_datawallet_modifications(df)

        @self._app.callback(
            Output("size_of_datawallet_modifications$graph", "figure"),
            Input("size_of_datawallet_modifications$hideTestClients", "value"),
        )
        def size_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_datawallet_modifications(cnxn, hide)
            return plots.size_of_datawallet_modifications(df)

        @self._app.callback(
            Output("num_datawallet_modifications$graph", "figure"),
            Input("num_datawallet_modifications$hideTestClients", "value"),
        )
        def num_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_datawallet_modifications_per_identity(cnxn, hide)
            return plots.num_datawallet_modifications_per_identity(df)

        @self._app.callback(
            Output("forcegraph$iframe", "src"),
            Input("forcegraph$hideTestClients", "value"),
        )
        def update_forcegraph(value: list | None) -> str:
            hide_test_clients = value is not None and len(value) > 0
            if hide_test_clients:
                return "/forcegraph.html?hide-test-clients=1"
            return "/forcegraph.html"

        @self._app.callback(
            Output("num_identities_per_client$graph", "figure"),
            Input("num_identities_per_client$checkbox", "value"),
        )
        def num_identities_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_identities_per_client(cnxn, hide)
            return plots.num_identities_per_client(df)

        @self._app.callback(
            Output("num_sent_messages_per_client$graph", "figure"),
            Input("num_sent_messages_per_client$hideTestClients", "value"),
        )
        def num_sent_messages_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_sent_messages_per_client(cnxn, hide)
            return plots.num_sent_messages_per_client(df)

        @self._app.callback(
            Output("num_received_messages_per_client$graph", "figure"),
            Input("num_received_messages_per_client$hideTestClients", "value"),
        )
        def num_received_messages_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_received_messages_per_client(cnxn, hide)
            return plots.num_received_messages_per_client(df)

        @self._app.callback(
            Output("num_devices_per_identity$graph", "figure"),
            Input("num_devices_per_identity$checkbox", "value"),
        )
        def num_devices_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_devices_per_identity(cnxn, hide)
            return plots.num_devices_per_identity(df)

        @self._app.callback(
            Output("num_recipients_per_sender_client_type$graph", "figure"),
            Input("num_recipients_per_sender_client_type$hideTestClients", "value"),
        )
        def num_recipients_per_sender_client_type(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_recipients_per_sender_client_type(cnxn, hide)
            return plots.num_recipients_per_sender_client_type(df)

        @self._app.callback(
            Output("activity_identity_creations$graph", "figure"),
            Input("activity_identity_creations$hideTestClients", "value"),
        )
        def activity_identity_creations(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.identity_creations(cnxn, hide)
            return plots.activity_plot(
                df,
                time_col="CreatedAt",
                split_col="ClientType",
            )

        @self._app.callback(
            Output("num_peers_per_identity$graph", "figure"),
            Input("num_peers_per_identity$hideTestClients", "value"),
        )
        def num_peers_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_peers_per_identity(cnxn, hide)
            return plots.num_peers_per_identity(df)

        @self._app.callback(
            Output("num_tokens_per_identity$graph", "figure"),
            Input("num_tokens_per_identity$hideTestClients", "value"),
        )
        def num_tokens_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_tokens_per_identity(cnxn, hide)
            return plots.num_tokens_per_identity(df)

        @self._app.callback(
            Output("num_relationship_templates_per_identity$graph", "figure"),
            Input("num_relationship_templates_per_identity$hideTestClients", "value"),
        )
        def num_relationship_templates_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_relationship_templates_per_identity(cnxn, hide)
            return plots.num_relationship_templates_per_identity(df)

        @self._app.callback(
            Output("token_size$graph", "figure"),
            Input("token_size$hideTestClients", "value"),
        )
        def token_size(value: list | None) -> go.Figure:
            hide_test_clients = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.token_size(cnxn, hide_test_clients)
            return plots.token_size(df)

        @self._app.callback(
            Output("activity_num_sent_messages$graph", "figure"),
            Input("activity_num_sent_messages$hideTestClients", "value"),
        )
        def activity_num_sent_messages(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.messages(cnxn, hide)
            return plots.activity_plot(
                df,
                time_col="CreatedAt",
                split_col="ClientType",
            )

        @self._app.callback(
            Output("activity_external_events$graph", "figure"),
            Input("activity_external_events$hideTestClients", "value"),
        )
        def activity_external_events(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.external_events(cnxn, hide)
            return plots.activity_plot(df, time_col="CreatedAt", split_col="ClientType",)

        @self._app.callback(
            Output("sync_errors$graph", "figure"),
            Input("sync_errors$hideTestClients", "value"),
        )
        def sync_errors(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.sync_errors(cnxn, hide)
            return plots.sync_errors(df)

        @self._app.callback(
            Output("relationship_status_distribution$graph", "figure"),
            Input("relationship_status_distribution$hideTestClients", "value"),
        )
        def relationship_status_distribution(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.relationships(cnxn, hide)
            return plots.relationship_status_distribution(df)

        @self._app.callback(
            Output("relationship_duration_pending$graph", "figure"),
            Input("relationship_duration_pending$hideTestClients", "value"),
        )
        def relationship_duration_pending(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.relationships(cnxn, hide)
            return plots.relationship_duration_pending(df)

        @self._app.callback(
            Output("device_type_distribution$graph", "figure"),
            Input("device_type_distribution$hideTestClients", "value"),
        )
        def device_type_distribution(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.device_push_channel_types(cnxn, hide)
            return plots.device_push_channel_type(df)

        @self._app.callback(
            Output("message_content_size$graph", "figure"),
            Input("message_content_size$hideTestClients", "value"),
        )
        def message_content_size(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.messages(cnxn, hide)
            return plots.message_content_size(df)

        @self._app.callback(
            Output("size_of_relationship_templates$graph", "figure"),
            Input("size_of_relationship_templates$hideTestClients", "value"),
        )
        def size_of_relationship_templates(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_relationship_templates(cnxn, hide)
            return plots.size_of_relationship_templates(df)

        @self._app.callback(
            Output("activity_num_created_files$graph", "figure"),
            Input("activity_num_created_files$hideTestClients", "value"),
        )
        def activity_num_created_files(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.activity_num_created_files(cnxn, hide)
            return plots.activity_plot(
                df,
                time_col="CreatedAt",
                split_col="ClientType",
            )

        @self._app.callback(
            Output("num_files_per_identity$graph", "figure"),
            Input("num_files_per_identity$hideTestClients", "value"),
        )
        def num_files_per_identity(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_files_per_identity(cnxn, hide)
            return plots.num_files_per_identity(df)

        @self._app.callback(
            Output("rlt_time_until_first_usage$graph", "figure"),
            Input("rlt_time_until_first_usage$hideTestClients", "value"),
        )
        def rlt_time_until_first_usage(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.rlt_time_until_first_usage(cnxn, hide)
            return plots.rlt_time_until_first_usage(df)

        @self._app.callback(
            Output("rlt_validity_period$graph", "figure"),
            Input("rlt_validity_period$hideTestClients", "value"),
        )
        def rlt_validity_period(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.rlt_validity_period(cnxn, hide)
            return plots.rlt_validity_period(df)


    def render_forcegraph(self):
        hide_test_clients = request.args.get("hide-test-clients", default=False, type=bool)
        with self._grab_cnxn() as cnxn:
            net = network.make_rel_network(cnxn, hide_test_clients)
        data = network.forcegraph_data(net)
        return render_template("forcegraph.html", data=data)


def _get_dropdown(children: list[Any] | None = None):
    return html.Div(
        className="dropdown",
        children=[
            html.Button(className="dropbtn", children=["☰"]),
            html.Div(
                className="dropdown-content",
                children=children,
            ),
        ],
    )
