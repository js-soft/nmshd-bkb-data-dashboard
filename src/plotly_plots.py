import calendar
import math
from typing import Literal

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio

from src import client_types, int_bucket_label

pio.templates[pio.templates.default].layout.font.family = "Work Sans"
pio.templates[pio.templates.default].layout.hoverlabel.font.family = "Work Sans"
pio.templates[pio.templates.default].layout.paper_bgcolor = "rgba(0,0,0,0)"


client_type_colmap = dict(zip(client_types(), px.colors.qualitative.D3))

default_color_seq = px.colors.qualitative.Safe

# Used to abbreviate and pretty print pd.Timestamps.
time_unit_abbreviations = {
    "days": "d",
    "hours": "h",
    "minutes": "min",
    "seconds": "s",
    "milliseconds": "ms",
    "microseconds": "us",
    "nanoseconds": "ns",
}


def make_timedelta_intervalindex(
    td_max: np.timedelta64,
    resolution: Literal["s", "ms", "us", "ns"],
) -> pd.IntervalIndex:
    # pd.Timedelta's constructor offers no means to diverge from the default of
    # nanosecond precision. This makes using this function cumbersome for any
    # timedeltas beyond 2**64-1 ns. Thus we use np.timedelta64 directly, the
    # representation underlying pd.Timedelta
    #
    # Note that pd.Timedeltas with different precisions can be created
    # indirectly, however, e.g.
    #
    #     s1 = pd.Series(["9999-11-22"], dtype="datetime64[us]")
    #     s2 = pd.Series(["0000-01-01"], dtype="datetime64[us]")
    #     td = (s1 - s2)
    #     td.iloc[0], td.iloc[0].asm8

    # -1s is included so the first interval includes 0.
    interval_breaks = [(-1, "s"), (1, "s"), (1, "m"), (1, "D"), (7, "D"), (31, "D"), (365, "D")]
    bins: list[np.timedelta64] = []
    for br in interval_breaks:
        bins.append(np.timedelta64(*br))
    if td_max > bins[-1]:
        bins.append(td_max)

    return pd.IntervalIndex.from_breaks(
        bins,
        closed="right",
        dtype=pd.IntervalDtype(subtype=f"timedelta64[{resolution}]"),
    )


def make_timedelta_interval_label(interval: pd.Interval) -> str:
    if interval.closed_right:
        # pd.Timedelta.components is namedtuple-like and defines _asdict().
        components = interval.right.components._asdict()

        num_nonempty_components = sum(bool(v) for v in components.values())
        if num_nonempty_components == 1:
            for unit, amount in components.items():
                if amount > 0:
                    return f"≤ {amount}{time_unit_abbreviations[unit]}"
        return f"≤ {interval.right}"

    # Implement different boundedness when needed.
    return str(interval)


def no_data() -> go.Figure:
    p = (
        go.Figure()
        .add_annotation({"text": "No data available to display", "showarrow": False})
        .update_layout({"yaxis": {"visible": False}, "xaxis": {"visible": False}})
    )
    return p


def num_identities_per_client(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientDisplayName: category (ordered)
    - ClientId: category (ordered)
    - ClientType: category (ordered)
    - NumIdentities
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientDisplayName", "ClientId", "ClientType", "NumIdentities"])
    # TODO: We have to set the category orders explicitly by sorting our values
    #       manually, instead of using plotly's xaxis_categoryorder layout
    #       option. plotly.js seems to cache data between updates, leading to
    #       ghost categories being displayed. See
    #       https://github.com/streamlit/streamlit/issues/5902 for a similar
    #       issue.
    df = df.sort_values(by=["NumIdentities"], ascending=False)
    df["ClientPlotName"] = pd.Categorical(
            df["ClientDisplayName"].astype(object).where(
            (~df["ClientDisplayName"].isna()) & (df["ClientDisplayName"].str.len() != 0),
            df["ClientId"]
        ),
        ordered=True
    )

    p = px.bar(
        df,
        x="ClientPlotName",
        y="NumIdentities",
        color="ClientType",
        log_y=True,
        labels={
            "ClientId": "BB Client ID",
            "NumIdentities": "Number of Identities",
            "ClientType": "BB Client Type",
            "ClientDisplayName": "BB Client Display Name"
        },
        hover_data={
            "NumIdentities": True,
            "ClientDisplayName": True,
            "ClientId": True,
            "ClientType": False,
            "ClientPlotName": False
        },
        color_discrete_map=client_type_colmap,
        category_orders={"ClientPlotName": df["ClientPlotName"]},
    )

    return p


def num_sent_messages_per_client(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - NumMessages
    - SenderClientDisplayName: category (ordered)
    - SenderClientId: category (ordered)
    - SenderClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["NumMessages", "SenderClientId", "SenderClientType", "SenderClientDisplayName"])
    df = df.sort_values(by=["NumMessages"], ascending=False)
    df["SenderClientPlotName"] = pd.Categorical(
            df["SenderClientDisplayName"].astype(object).where(
            (~df["SenderClientDisplayName"].isna()) & (df["SenderClientDisplayName"].str.len() != 0),
            df["SenderClientId"]
        ),
        ordered=True
    )

    p = px.bar(
        df,
        x="SenderClientPlotName",
        y="NumMessages",
        color="SenderClientType",
        log_y=True,
        labels={
            "SenderClientId": "BB Client ID",
            "NumMessages": "Number of Messages",
            "SenderClientType": "BB Client Type",
            "SenderClientDisplayName": "BB Client Display Name",
        },
        hover_data={
            "NumMessages": True,
            "SenderClientId": True,
            "SenderClientType": False,
            "SenderClientDisplayName": True,
            "SenderClientPlotName": False,
        },
        color_discrete_map=client_type_colmap,
        category_orders={"SenderClientPlotName": df["SenderClientPlotName"]},
    )

    return p


def num_received_messages_per_client(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - NumMessages
    - RecipientClientDisplayName: category (ordered)
    - RecipientClientId: category (ordered)
    - RecipientClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["NumMessages", "RecipientClientId", "RecipientClientType", "RecipientClientDisplayName"])
    df = df.sort_values(by=["NumMessages"], ascending=False)
    df["RecipientClientPlotName"] = pd.Categorical(
            df["RecipientClientDisplayName"].astype(object).where(
            (~df["RecipientClientDisplayName"].isna()) & (df["RecipientClientDisplayName"].str.len() != 0),
            df["RecipientClientId"]
        ),
        ordered=True
    )

    p = px.bar(
        df,
        x="RecipientClientPlotName",
        y="NumMessages",
        color="RecipientClientType",
        log_y=True,
        labels={
            "RecipientClientId": "BB Client ID",
            "NumMessages": "Number of Messages",
            "RecipientClientType": "BB Client Type",
            "RecipientClientDisplayName": "BB Client Display Name"
        },
        hover_data={
            "NumMessages": True,
            "RecipientClientId": True,
            "RecipientClientType": False,
            "RecipientClientDisplayName": True,
            "RecipientClientPlotName": False,
        },
        color_discrete_map=client_type_colmap,
        category_orders={"RecipientClientPlotName": df["RecipientClientPlotName"]},
    )

    return p


def message_content_size(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - MessageSize
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "MessageSize"])

    p = px.histogram(
        df,
        x="MessageSize",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={"MessageSize": "Message Size [B]"},
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    # Somehow labeling of y-axis in hist does not work with labels param in histogram method itself :(
    p.update_layout(yaxis_title_text="Number of Messages")
    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def num_devices_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumDevices
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumDevices", "count"])

    # TODO: make_int_interval_index(), make_int_interval_label
    maxexp = int(max(2, np.ceil(np.log10(df["NumDevices"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["NumDevicesBucket"] = pd.cut(df["NumDevices"], bins=bins).map(int_bucket_label).astype("category")

    p = px.bar(
        df,
        x="NumDevicesBucket",
        y="count",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "NumDevicesBucket": "Number of Devices",
            "count": "Number Of Identities",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p


def num_recipients_per_sender_client_type(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - NumRecipients
    - NumSentMessages
    - SenderClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["NumRecipients", "NumSentMessages", "SenderClientType"])

    maxexp = int(max(2, np.floor(np.log10(df["NumRecipients"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["NumRecipientsBucket"] = pd.cut(df["NumRecipients"], bins=bins).map(int_bucket_label).astype("category")

    p = px.bar(
        df,
        x="NumRecipientsBucket",
        y="NumSentMessages",
        color="SenderClientType",
        facet_col="SenderClientType",
        log_y=True,
        labels={
            "NumRecipientsBucket": "Number of Messages Recipients",
            "NumSentMessages": "Number Of Sent Messages",
            "SenderClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "SenderClientType": df["SenderClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p


def num_peers_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumPeers
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumPeers"])
    df = (
        df.groupby("ClientType", observed=True, as_index=False)
        .value_counts()
        .rename(columns={"count": "NumIdentities"})
    )

    maxexp = int(max(2, np.floor(np.log10(df["NumPeers"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")

    df["NumPeersBucket"] = pd.cut(df["NumPeers"], bins=bins).map(int_bucket_label).astype("category")
    df = df.groupby(["ClientType", "NumPeersBucket"], observed=False, as_index=False)["NumIdentities"].sum()

    p = px.bar(
        df,
        x="NumPeersBucket",
        y="NumIdentities",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "NumIdentities": "Number of Identities",
            "NumPeersBucket": "Number of Peers",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def activity_plot(
    df: pd.DataFrame,
    time_col: str,
    split_col: str = "ClientType",
) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - [time_col]: datetime64[ns]
    - [split_col]: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    # FIXME: density_heatmap expects data to be aggregated, while all we need
    #        is a heatmap of values for every pair of workday and week. Using
    #        px.imshow or go.Heatmap would be a better fit but neither provide
    #        simple dataframe or faceting support. density_heatmap doesn't let
    #        us specify pretty hover information.

    df = df.filter([time_col, split_col])
    df[time_col] = df[time_col].dt.normalize()
    df["Weekday"] = pd.Categorical(df[time_col].dt.day_of_week, categories=list(range(0, 7)), ordered=True)
    df["Week"] = pd.Categorical(df[time_col].dt.isocalendar().week, categories=list(range(0, 53)), ordered=True)
    df["Year"] = pd.Categorical(df[time_col].dt.year, ordered=True)
    df = df.groupby([time_col, split_col, "Weekday", "Week", "Year"], as_index=False, observed=False).size()

    fig = px.density_heatmap(
        df,
        x="Week",
        y="Weekday",
        z="size",
        facet_row="Year",
        facet_col=split_col,
        nbinsx=len(df["Week"].cat.categories),
        nbinsy=len(df["Weekday"].cat.categories),
        color_continuous_scale=[
            # TODO: Skala logarithmisch-freundlich machen / schwache Aktivitäten besser hervorheben
            [0.0, "rgb(255,255,255)"],  # white
            [0.5, "rgb(49,163,84)"],  # medium green
            [1.0, "rgb(0,109,44)"],  # dark green
        ],
        category_orders={
            split_col: df[split_col].cat.categories,
            "Weekday": df["Weekday"].cat.categories,
        },
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=df["Weekday"].cat.categories,
        ticktext=list(calendar.day_abbr),
    )
    fig.update_traces(
        xgap=1.5,
        ygap=1.5,
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    fig.update_layout(
        xaxis={"fixedrange": True},
        yaxis={"fixedrange": True},
    )
    fig.update_coloraxes(colorbar_title="Count")
    return fig


def sync_errors(df: pd.DataFrame) -> go.Figure:
    # FUTURE: Nach Errorcode aufspalten, Histogram gestapelt (Errorcodes), 1D-Bins
    """
    Accepts a dataframe with the following columns:
    - CreatedAt: datetime64[ns]
    - ErrorCode: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["CreatedAt", "ErrorCode"])
    df["CreatedAt"] = df["CreatedAt"].dt.normalize()
    df = (
        df.groupby(["CreatedAt", "ErrorCode"], as_index=False, observed=True)
        .value_counts()
        .rename(columns={"count": "NumErrors"})
    )
    p = px.scatter(
        df,
        x="CreatedAt",
        y="NumErrors",
        color="ErrorCode",
        labels={
            "NumErrors": "Number of Errors per Day",
            "CreatedAt": "Error Timestamp",
            "ErrorCode": "Error Code",
        },
        category_orders={
            "ErrorCode": df["ErrorCode"].cat.categories,
        },
    )
    p.update_layout()
    return p


def relationship_status_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - Status: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["Status"])
    df = df.groupby(["Status"], as_index=False, observed=True).value_counts()
    p = px.bar(
        df,
        x="count",
        y="Status",
        log_x=True,
        labels={"count": "No. Relationships"},
        category_orders={
            "Status": df["Status"].cat.categories,
        },
        color_discrete_sequence=default_color_seq,
    )
    p.update_layout(
        yaxis_categoryorder="total ascending",
    )
    return p


def relationship_duration_pending(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - CreatedAt: datetime64[ns]
    - AnsweredAt: datetime64[ns]
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["AnsweredAt", "CreatedAt"])

    df["Duration"] = df["AnsweredAt"] - df["CreatedAt"]
    intervals = make_timedelta_intervalindex(df["Duration"].max().asm8, "ns")
    df["DurationBucket"] = pd.cut(df["Duration"], bins=intervals).cat.rename_categories(make_timedelta_interval_label)
    df["DurationBucket"] = (
        df["DurationBucket"]
        .cat.set_categories(["Pending", *df["DurationBucket"].cat.categories], ordered=True)
        .fillna("Pending")
        .cat.remove_unused_categories()
    )
    df = df.filter(["DurationBucket"]).groupby(["DurationBucket"], observed=True, as_index=False).value_counts()

    p = px.bar(
        df,
        x="DurationBucket",
        y="count",
        log_y=True,
        labels={
            "DurationBucket": "Duration in 'Pending' State",
            "count": "Number of Relationships",
        },
        category_orders={
            "DurationBucket": df["DurationBucket"].cat.categories,
        },
        color_discrete_sequence=default_color_seq,
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p


def device_push_channel_type(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - DeviceType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "DeviceType"])
    df = df.groupby(["ClientType"], as_index=False, observed=False).value_counts()

    p = px.bar(
        df,
        x="count",
        y="DeviceType",
        color="ClientType",
        facet_col="ClientType",
        log_x=True,
        orientation="h",
        labels={
            "DeviceType": "Device Type",
            "count": "Number of Devices",
        },
        title="Device Push Channel Type (PNS Prefix)",
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
            "DeviceType": df["DeviceType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def num_relationship_templates_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
     - ClientType: category (ordered)
     - NumTemplates
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumTemplates"])
    df = df.groupby("ClientType", observed=True, as_index=False).value_counts()

    maxexp = int(max(2, np.floor(np.log10(df["NumTemplates"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")

    df["NumTemplatesBucket"] = pd.cut(df["NumTemplates"], bins=bins).map(int_bucket_label).astype("category")
    df = df.groupby(["ClientType", "NumTemplatesBucket"], observed=False, as_index=False)["count"].sum()

    p = px.bar(
        df,
        x="NumTemplatesBucket",
        y="count",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "count": "Number of Identities",
            "NumTemplatesBucket": "Number of Relationship Templates Created",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def num_tokens_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
     - ClientType: category (ordered)
     - NumTokens
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumTokens"])
    df = (
        df.groupby("ClientType", observed=True, as_index=False)
        .value_counts()
        .rename(columns={"count": "NumIdentities"})
    )

    maxexp = int(max(2, np.floor(np.log10(df["NumTokens"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")

    df["NumTokensBucket"] = pd.cut(df["NumTokens"], bins=bins).map(int_bucket_label).astype("category")
    df = df.groupby(["ClientType", "NumTokensBucket"], observed=False, as_index=False)["NumIdentities"].sum()

    p = px.bar(
        df,
        x="NumTokensBucket",
        y="NumIdentities",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "NumIdentities": "Number of Identities",
            "NumTokensBucket": "Number of Tokens",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def token_size(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - TokenSize
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "TokenSize"])

    p = px.histogram(
        df,
        x="TokenSize",
        color="ClientType",
        facet_col="ClientType",
        log_x=False,  # log_x=True breaks the plot
        log_y=True,
        nbins=100,
        labels={
            "TokenSize": "Size of Token [B]",
            "y": "Count",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def num_datawallet_modifications_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumDWM
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumDWM", "count"])

    maxexp = int(max(2, np.floor(np.log10(df["NumDWM"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["NumDWMBucket"] = pd.cut(df["NumDWM"], bins=bins).map(int_bucket_label).astype("category")
    df = df.groupby(["ClientType", "NumDWMBucket"], observed=False, as_index=False)["count"].sum()

    p = px.bar(
        df,
        x="NumDWMBucket",
        y="count",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "count": "Number of Identities",
            "NumDWMBucket": "Number of Datawallet Modifications",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def size_of_datawallet_modifications(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - Size
    - ClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["Size", "ClientType"])

    # FUTURE: Payloadkategorie innerhalb der Balken anzeigen
    bin_width = 50
    num_bins = math.ceil((df["Size"].max() - df["Size"].min()) / bin_width)
    p = px.histogram(
        df,
        x="Size",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        nbins=num_bins,
        labels={
            "Size": "Size [B]",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
        yaxis_title_text="Number of Datawallet Modifications",
    )

    return p


def type_of_datawallet_modifications(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - Type: category (ordered)
    - ClientType: category (ordered)
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "Type", "count"])

    p = px.bar(
        df,
        x="count",
        y="Type",
        log_x=True,
        color="ClientType",
        facet_col="ClientType",
        labels={
            "count": "Number of Datawallet Modifications",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
            "Type": df["Type"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def collection_of_datawallet_modifications(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - Collection: category (ordered)
    - ClientType: category (ordered)
    - Count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["Collection", "ClientType", "count"])

    p = px.bar(
        df,
        x="count",
        y="Collection",
        color="ClientType",
        facet_col="ClientType",
        log_x=True,
        labels={
            "count": "Number of Datawallet Modifications",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
            "Collection": df["Collection"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def payload_category_of_datawallet_modifications(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - PayloadCategory: category (ordered)
    - ClientType: category (ordered)
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["PayloadCategory", "ClientType", "count"])

    p = px.bar(
        df,
        x="count",
        y="PayloadCategory",
        color="ClientType",
        facet_col="ClientType",
        log_x=True,
        labels={
            "PayloadCategory": "Payload Category",
            "count": "Number of Datawallet Modifications",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
            "PayloadCategory": df["PayloadCategory"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def type_of_external_events(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - count
    - ClientType: category (ordered)
    - Type: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "Type", "count"])

    p = px.bar(
        df,
        x="count",
        y="Type",
        color="ClientType",
        facet_col="ClientType",
        log_x=True,
        labels={
            "Type": "External Event Type",
            "count": "Number of External Events",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
            "Type": df["Type"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def num_external_events_per_sync_run(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumExternalEvents
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumExternalEvents", "count"])

    maxexp = int(max(2, np.floor(np.log10(df["NumExternalEvents"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["NumExternalEventsBucket"] = pd.cut(df["NumExternalEvents"], bins=bins).map(int_bucket_label).astype("category")

    p = px.bar(
        df,
        x="NumExternalEventsBucket",
        y="count",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "NumExternalEventsBucket": "Number of External Events per Sync Run",
            "count": "Number of Sync Runs",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )

    return p


def size_of_relationship_templates(df: pd.DataFrame):
    """
    Accepts a dataframe with the following columns:
    - RelationshipTemplateSize
    - ClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["RelationshipTemplateSize", "ClientType"])

    bin_width = 50
    num_bins = math.ceil((df["RelationshipTemplateSize"].max() - df["RelationshipTemplateSize"].min()) / bin_width)
    p = px.histogram(
        df,
        x="RelationshipTemplateSize",
        color="ClientType",
        facet_col="ClientType",
        nbins=num_bins,
        log_y=True,
        labels={
            "RelationshipTemplateSize": "Size of Relationship Template [B]",
            "ClientType": "Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
        yaxis_title_text="Number of Relationship Templates",
    )

    return p


def size_of_file_contents(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - FileSize
    - ClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["FileSize", "ClientType"])

    p = px.histogram(
        df,
        x="FileSize",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={"FileSize": "File Size [B]"},
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
        yaxis_title_text="Number of Files",
    )

    return p


def num_max_rel_templ_allocations(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - RLTCreatorClientType: category (ordered)
    - MaxAllocs
    - NumAllocs
    - RelRLTAllocs
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["RLTCreatorClientType", "MaxAllocs", "NumAllocs", "RelRLTAllocs"])

    maxexp = int(max(2, np.floor(np.log10(df["MaxAllocs"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["MaxAllocsBucket"] = (
        pd.cut(df["MaxAllocs"], bins=bins)
        .map(int_bucket_label)
        .map(lambda x: x if x != "0" else "Unlimited")
        .astype("category")
    )
    # TODO: Prüfen, ob leere Buckets im Plot angezeigt werden. Ggf. value_count verwenden()
    df = df.groupby(["RLTCreatorClientType", "MaxAllocsBucket"], observed=True, as_index=False).agg(
        MeanAllocs=("RelRLTAllocs", "mean"), NumRLT=("RLTCreatorClientType", "size")
    )
    df["MeanAllocs"] = df["MeanAllocs"].fillna(0)
    p = px.bar(
        df,
        x="MaxAllocsBucket",
        y="NumRLT",
        color="RLTCreatorClientType",
        facet_col="RLTCreatorClientType",
        log_y=True,
        labels={
            "MaxAllocsBucket": "Max. Number of Allocations",
            "NumRLT": "Number of Relationship Templates",
        },
        hover_data="MeanAllocs",
        color_discrete_map=client_type_colmap,
        category_orders={
            "RLTCreatorClientType": df["RLTCreatorClientType"].cat.categories,
        },
    )
    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    p.update_traces(
        hovertemplate="<br>".join(
            [
                "Rel. amount of allocs in bucket: %{customdata[0]:.3%}",
                "Max. Number of allocs: %{x}",
                "Number of Relationship Templates: %{y:.2f}",
            ]
        )
    )
    return p


def num_files_per_identity(df: pd.DataFrame) -> go.Figure:
    """
    Accepts dataframe with the following columns:
    - ClientType: category (ordered)
    - NumFiles
    - count
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ClientType", "NumFiles", "count"])

    maxexp = int(max(2, np.floor(np.log10(df["NumFiles"].max())) + 1))
    bins = list(range(0, 6)) + list(int(x) for x in np.logspace(1, maxexp, num=maxexp))
    bins = pd.IntervalIndex.from_breaks(bins, closed="left")
    df["NumFilesBucket"] = pd.cut(df["NumFiles"], bins=bins).map(int_bucket_label).astype("category")

    p = px.bar(
        df,
        x="NumFilesBucket",
        y="count",
        color="ClientType",
        facet_col="ClientType",
        log_y=True,
        labels={
            "NumFilesBucket": "Number of Files",
            "count": "Number Of Identities",
            "ClientType": "BB Client Type",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "ClientType": df["ClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p


def rlt_time_until_first_usage(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ExpiredUnallocated: bool
    - RLTCreatorClientType: category (ordered)
    - TimeUntilFirstUsage: timedelta64[us]
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ExpiredUnallocated", "RLTCreatorClientType", "TimeUntilFirstUsage"])

    intervals = make_timedelta_intervalindex(df["TimeUntilFirstUsage"].max().asm8, "us")
    df["TimeBucket"] = pd.cut(df["TimeUntilFirstUsage"], bins=intervals).cat.rename_categories(
        make_timedelta_interval_label
    )

    def fill_na_buckets(row):
        if pd.isna(row["TimeUntilFirstUsage"]):
            if row["ExpiredUnallocated"]:
                return "Unallocated, expired"
            return "Unallocated, active"
        return row["TimeBucket"]

    df["TimeBucket"] = pd.Categorical(
        df.apply(fill_na_buckets, axis=1),
        categories=["Unallocated, expired", "Unallocated, active", *df["TimeBucket"].cat.categories],
        ordered=True,
    )
    df["TimeBucket"] = df["TimeBucket"].cat.remove_unused_categories()
    df = (
        df.filter(["RLTCreatorClientType", "TimeBucket"])
        .groupby(["RLTCreatorClientType"], observed=True, as_index=False)
        .value_counts()
    )

    p = px.bar(
        df,
        x="TimeBucket",
        y="count",
        color="RLTCreatorClientType",
        facet_col="RLTCreatorClientType",
        log_y=True,
        labels={
            "TimeBucket": "Time until first usage of Relationship Template",
            "count": "Number of Relationship Templates",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "TimeBucket": df["TimeBucket"].cat.categories,
            "RLTCreatorClientType": df["RLTCreatorClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p


def rlt_validity_period(df: pd.DataFrame) -> go.Figure:
    """
    Accepts a dataframe with the following columns:
    - ValidityPeriod: timedelta64[us]
    - RLTCreatorClientType: category (ordered)
    """

    if len(df) == 0:
        return no_data()

    df = df.filter(["ValidityPeriod", "RLTCreatorClientType"])

    intervals = make_timedelta_intervalindex(df["ValidityPeriod"].max().asm8, "us")
    df["TimeBucket"] = pd.cut(df["ValidityPeriod"], bins=intervals).cat.rename_categories(make_timedelta_interval_label)
    df = (
        df.filter(["RLTCreatorClientType", "TimeBucket"])
        .groupby(["RLTCreatorClientType"], as_index=False, observed=False)
        .value_counts()
    )

    p = px.bar(
        df,
        x="TimeBucket",
        y="count",
        facet_col="RLTCreatorClientType",
        color="RLTCreatorClientType",
        log_y=True,
        labels={
            "TimeBucket": "Validity Period of Relationship Template",
            "count": "Number of Relationship Templates",
        },
        color_discrete_map=client_type_colmap,
        category_orders={
            "TimeBucket": df["TimeBucket"].cat.categories,
            "RLTCreatorClientType": df["RLTCreatorClientType"].cat.categories,
        },
    )

    p.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    p.update_layout(
        showlegend=False,
    )
    return p
