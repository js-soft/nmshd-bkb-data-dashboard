from contextlib import contextmanager
from typing import Any, Literal

import dash
import plotly.graph_objs as go
import sqlalchemy
from dash import Dash, State, Input, Output, dcc, html, ALL
from dash.dash import no_update
from flask import Flask, redirect, render_template, request

from src import config, network
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
                # XXX: Layout aufhübschen
                dcc.RadioItems(
                    id="hide-test-clients-radio-group",
                    options=[{"label": "Hide", "value": "hide"}, {"label": "Show", "value": "show"}],
                    value="hide" if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else "show",
                    inline=True,
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
            Input({"type": "hide-test-clients-checkbox", "plot": "num-max-rel-templ-allocations"}, "value"),
        )
        def num_max_rel_templ_allocations(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_max_rel_templ_allocations(cnxn, hide)
            return plots.num_max_rel_templ_allocations(df)

        @self._app.callback(
            Output("size_of_file_contents$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "size-of-file-contents"}, "value"),
        )
        def size_of_file_contents(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_file_contents(cnxn, hide)
            return plots.size_of_file_contents(df)

        @self._app.callback(
            Output("num_external_events_per_sync_run$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-external-events-per-sync-run"}, "value"),
        )
        def num_external_events_per_sync_run(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_external_events_per_sync_run(cnxn, hide)
            return plots.num_external_events_per_sync_run(df)

        @self._app.callback(
            Output("type_of_external_events$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "type-of-external-events"}, "value"),
        )
        def type_of_external_events(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.type_of_external_events(cnxn, hide)
            return plots.type_of_external_events(df)

        @self._app.callback(
            Output("payload_category_of_datawallet_modifications$graph", "figure"),
            Input(
                {"type": "hide-test-clients-checkbox", "plot": "payload-category-of-datawallet-modifications"}, "value"
            ),
        )
        def payload_category_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.payload_category_of_datawallet_modifications(cnxn, hide)
            return plots.payload_category_of_datawallet_modifications(df)

        @self._app.callback(
            Output("collection_of_datawallet_modifications$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "collection-of-datawallet-modifications"}, "value"),
        )
        def collection_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.collection_of_datawallet_modifications(cnxn, hide)
            return plots.collection_of_datawallet_modifications(df)

        @self._app.callback(
            Output("type_of_datawallet_modifications$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "type-of-datawallet-modifications"}, "value"),
        )
        def type_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.type_of_datawallet_modifications(cnxn, hide)
            return plots.type_of_datawallet_modifications(df)

        @self._app.callback(
            Output("size_of_datawallet_modifications$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "size-of-datawallet-modifications"}, "value"),
        )
        def size_of_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_datawallet_modifications(cnxn, hide)
            return plots.size_of_datawallet_modifications(df)

        @self._app.callback(
            Output("num_datawallet_modifications$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-datawallet-modifications"}, "value"),
            # Input({"type": "hide-test-clients-checkbox", "plot": "num-datawallet-modifications", "index": 0}, "value"),
        )
        def num_datawallet_modifications(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_datawallet_modifications_per_identity(cnxn, hide)
            return plots.num_datawallet_modifications_per_identity(df)

        @self._app.callback(
            Output("forcegraph$iframe", "src"),
            Input({"type": "hide-test-clients-checkbox", "plot": "forcegraph"}, "value"),
        )
        def update_forcegraph(value: list | None) -> str:
            hide_test_clients = value is not None and len(value) > 0
            if hide_test_clients:
                return "/forcegraph.html?hide-test-clients=1"
            return "/forcegraph.html"

        @self._app.callback(
            Output("num_identities_per_client$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-identities-per-client"}, "value"),
        )
        def num_identities_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_identities_per_client(cnxn, hide)
            return plots.num_identities_per_client(df)

        @self._app.callback(
            Output("num_sent_messages_per_client$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-sent-messages-per-client"}, "value"),
        )
        def num_sent_messages_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_sent_messages_per_client(cnxn, hide)
            return plots.num_sent_messages_per_client(df)

        @self._app.callback(
            Output("num_received_messages_per_client$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-received-messages-per-client"}, "value"),
        )
        def num_received_messages_per_client(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_received_messages_per_client(cnxn, hide)
            return plots.num_received_messages_per_client(df)

        @self._app.callback(
            Output({"type": "graph", "plot": "num-devices-per-identity"}, "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-devices-per-identity"}, "value"),
        )
        def num_devices_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_devices_per_identity(cnxn, hide)
            return plots.num_devices_per_identity(df)

        @self._app.callback(
            Output("num_recipients_per_sender_client_type$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-recipients-per-sender-client-type"}, "value"),
        )
        def num_recipients_per_sender_client_type(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_recipients_per_sender_client_type(cnxn, hide)
            return plots.num_recipients_per_sender_client_type(df)

        @self._app.callback(
            Output("activity_identity_creations$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "activity-identity-creations"}, "value"),
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
            Input({"type": "hide-test-clients-checkbox", "plot": "num-peers-per-identity"}, "value"),
        )
        def num_peers_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_peers_per_identity(cnxn, hide)
            return plots.num_peers_per_identity(df)

        @self._app.callback(
            Output("num_tokens_per_identity$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-tokens-per-identity"}, "value"),
        )
        def num_tokens_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_tokens_per_identity(cnxn, hide)
            return plots.num_tokens_per_identity(df)

        @self._app.callback(
            Output("num_relationship_templates_per_identity$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "num-relationship-templates-per-identity"}, "value"),
        )
        def num_relationship_templates_per_identity(value: list | None) -> go.Figure:
            hide = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_relationship_templates_per_identity(cnxn, hide)
            return plots.num_relationship_templates_per_identity(df)

        @self._app.callback(
            Output("token_size$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "token-size"}, "value"),
        )
        def token_size(value: list | None) -> go.Figure:
            hide_test_clients = value is not None and len(value) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.token_size(cnxn, hide_test_clients)
            return plots.token_size(df)

        @self._app.callback(
            Output("activity_num_sent_messages$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "activity-num-sent-messages"}, "value"),
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
            Input({"type": "hide-test-clients-checkbox", "plot": "activity-external-events"}, "value"),
        )
        def activity_external_events(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.external_events(cnxn, hide)
            return plots.activity_plot(
                df,
                time_col="CreatedAt",
                split_col="ClientType",
            )

        @self._app.callback(
            Output("sync_errors$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "sync-errors"}, "value"),
        )
        def sync_errors(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.sync_errors(cnxn, hide)
            return plots.sync_errors(df)

        @self._app.callback(
            Output("relationship_status_distribution$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "relationship-status-distribution"}, "value"),
        )
        def relationship_status_distribution(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.relationships(cnxn, hide)
            return plots.relationship_status_distribution(df)

        @self._app.callback(
            Output("relationship_duration_pending$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "relationship-duration-pending"}, "value"),
        )
        def relationship_duration_pending(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.relationships(cnxn, hide)
            return plots.relationship_duration_pending(df)

        @self._app.callback(
            Output({"type": "graph", "plot": "device-type-distribution"}, "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "device-type-distribution"}, "value"),
        )
        def device_type_distribution(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.device_push_channel_types(cnxn, hide)
            return plots.device_push_channel_type(df)

        @self._app.callback(
            Output("message_content_size$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "message-content-size"}, "value"),
        )
        def message_content_size(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.messages(cnxn, hide)
            return plots.message_content_size(df)

        @self._app.callback(
            Output("size_of_relationship_templates$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "size-of-relationship-templates"}, "value"),
        )
        def size_of_relationship_templates(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.size_of_relationship_templates(cnxn, hide)
            return plots.size_of_relationship_templates(df)

        @self._app.callback(
            Output("activity_num_created_files$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "activity-num-created-files"}, "value"),
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
            Input({"type": "hide-test-clients-checkbox", "plot": "num-files-per-identity"}, "value"),
        )
        def num_files_per_identity(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.num_files_per_identity(cnxn, hide)
            return plots.num_files_per_identity(df)

        @self._app.callback(
            Output("rlt_time_until_first_usage$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "rlt-time-until-first-usage"}, "value"),
        )
        def rlt_time_until_first_usage(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.rlt_time_until_first_usage(cnxn, hide)
            return plots.rlt_time_until_first_usage(df)

        @self._app.callback(
            Output("rlt_validity_period$graph", "figure"),
            Input({"type": "hide-test-clients-checkbox", "plot": "rlt-validity-period"}, "value"),
        )
        def rlt_validity_period(hide_list: list | None) -> go.Figure:
            hide = hide_list is not None and len(hide_list) > 0
            with self._grab_cnxn() as cnxn:
                df = queries.rlt_validity_period(cnxn, hide)
            return plots.rlt_validity_period(df)

        @self._app.callback(
            Output("hide-test-clients-radio-group", "value"),
            Output({"type": "hide-test-clients-checkbox", "plot": ALL}, "value"),
            Input("hide-test-clients-radio-group", "value"),
            Input({"type": "hide-test-clients-checkbox", "plot": ALL}, "value"),
            State({"type": "graph", "plot": ALL}, "figure"),
            # prevent_initial_call=True,
        )
        def sync_hide_test_clients_widgets(
            radio: str | None, checkboxes: list[list[str]], graphs,
        ) -> tuple[str | None, list[list[str]]]:
            def mask_unnecessary_updates(
                _radio: str | None, _checkboxes: list[list[str]]
            ) -> tuple[str | None, list[list[str]]]:
                new_radio = no_update if _radio == radio else _radio
                new_checkboxes = []
                for new, old in zip(_checkboxes, checkboxes):
                    if len(new) == len(old):
                        new_checkboxes.append(no_update)
                    else:
                        new_checkboxes.append(new)
                return new_radio, new_checkboxes

            triggered_by = dash.ctx.triggered_id
            if triggered_by is None:
                # XXX: dash.ctx.{outputs,inputs}_list[1] sind leer beim initialen (F5) laden. Kann es sein, dass
                # beim initialen Laden die Page-Widgets noch nicht existieren und dass erst anschließend
                # in einem zweiten Callback die Checkboxes geladen werden?

                # Laden der Radiogroup im Header, Pageinhalt existiert noch nicht
                if len(checkboxes) == 0:
                    raise dash.exceptions.PreventUpdate

                # While switching between pages, when the radio group is unset
                # due to mixed checkbox states, set its value from the config.
                if radio is None:
                    radio = "hide" if config.get().DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT else "show"
                if radio == "hide":
                    result = mask_unnecessary_updates("hide", [["hide_test_clients"]] * len(dash.ctx.outputs_list[1]))
                else:
                    result = mask_unnecessary_updates("show", [[]] * len(dash.ctx.outputs_list[1]))

            elif triggered_by == "hide-test-clients-radio-group":
                if radio == "show":
                    result = mask_unnecessary_updates("show", [[]] * len(dash.ctx.outputs_list[1]))
                else:
                    result = mask_unnecessary_updates("hide", [["hide_test_clients"]] * len(dash.ctx.outputs_list[1]))

            # XXX: Maskieren verhindert, dass die Plots initial geladen werden.
            #      Wie kann das gelöst werden?
            else:

                if all(g is None for g in graphs):
                    if radio == "hide":
                        return "hide", [["hide_test_clients"]] * len(dash.ctx.outputs_list[1])
                    return "show", [[]] * len(dash.ctx.outputs_list[1])

                num_checked = sum(len(v) != 0 for v in checkboxes)
                if num_checked == 0:
                    result =  mask_unnecessary_updates("show", checkboxes)
                elif num_checked == len(checkboxes):
                    result = mask_unnecessary_updates("hide", checkboxes)
                else:
                    result = mask_unnecessary_updates(None, checkboxes)

            import time
            # TODO: in abhängigkeit davon ob graphs is None maskieren oder nicht
            s = time.time()
            print(f"callback {time.time()}: {result=}")
            return result

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
