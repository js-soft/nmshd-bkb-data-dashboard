import re
from typing import Literal, get_args

import pandas as pd

from src import config

ClientType = Literal["App", "Connector"]
DeviceType = Literal["Android", "SSE", "Apple", "Unknown"]


def client_types() -> list[str]:
    """
    Returns all possible client types as a tuple of strings.
    """

    v = sorted(str(t) for t in get_args(ClientType))
    return v


# See https://github.com/nmshd/backbone/blob/main/Modules/Relationships/src/Relationships.Domain/Aggregates/Relationships/RelationshipStatus.cs
bb_rel_status_map = {
    10: "Pending",
    20: "Active",
    30: "Rejected",
    40: "Revoked",
    50: "Terminated",
    60: "DeletionProposed",
    70: "ReadyForDeletion",
}

bb_datawallet_modification_type_map = {
    0: "Create",
    1: "Update",
    2: "Delete",
    3: "CacheChanged",
}

# See https://github.com/nmshd/backbone/blob/9f72386994f343b548e0ba694f45ab2b1b7d023a/Modules/Devices/src/Devices.Domain/Entities/Identities/Identity.cs#L343
bb_id_status_map = {
    0: "Active",
    1: "ToBeDeleted",
    2: "Deleting",
}

# See https://github.com/nmshd/backbone/commit/5428a91ce549f996f616f0610a3a46d3de546a32#diff-fc8cc975a5ea3bd621080a4a1b318d0a0f2ce9b99ce283931ff0d84a357d4671
bb_external_event_type_map = {
    0: "MessageReceived",
    1: "MessageDelivered",
    2: "RelationshipChangeCreated",
    3: "RelationshipChangeCompleted",
    4: "IdentityDeletionProcessStarted",
    5: "IdentityDeletionProcessStatusChanged",
    6: "PeerToBeDeleted",
    7: "PeerDeletionCancelled",
    8: "PeerDeleted",
}

bb_datawallet_modification_collections = [
    "Tokens", "Notifications", "IdentityDeletionProcess",
    "Templates", "Settings", "Secrets", "Requests", "Relationships",
    "Messages", "Files", "Devices", "Attributes",
]


def is_app_client(client_id: str) -> bool:
    pattern = config.get().DASHBOARD_APP_CLIENTS_REGEX
    return re.fullmatch(pattern, client_id) is not None


def bb_client_type_from_id(client_id: str) -> ClientType:
    if is_app_client(client_id):
        return "App"
    return "Connector"


def is_test_client(client_id: str) -> bool:
    pattern = config.get().DASHBOARD_TEST_CLIENTS_REGEX
    return re.fullmatch(pattern, client_id) is not None


def seconds_to_human_readable(seconds):
    days = seconds // (24 * 3600)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    human_readable = []
    if days > 0:
        return f"{int(days)}d"
    if hours > 0:
        human_readable.append(f"{int(hours)}h")
        if minutes > 0:
            human_readable.append(f"{int(minutes)}m")
    else:
        if minutes > 0:
            human_readable.append(f"{int(minutes)}m")
        if seconds > 0:
            human_readable.append(f"{int(seconds)}s")

    return " ".join(human_readable) or "0s"


def bb_device_type_from_pns_handle(pns_handle: str | None) -> DeviceType:
    if pns_handle is None:
        return "Unknown"
    if pns_handle.startswith("fcm|"):
        return "Android"
    if pns_handle.startswith("apns|"):
        return "Apple"
    if pns_handle.startswith("sse|"):
        return "SSE"
    return "Unknown"


def int_bucket_label(bucket: pd.Interval) -> str:
    """
    Given an integer Interval, returns a single integer string for unary buckets.

    E.g. [[0, 1), [1, 10)] -> ["0", "[1, 10)"],
    """
    assert bucket.closed == "left", "not implemented"

    if bucket.right - bucket.left == 1:
        return f"{bucket.left:,}"
    return f"{bucket.left:,} - {bucket.right-1:,}"
