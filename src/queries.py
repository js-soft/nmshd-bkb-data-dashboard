from datetime import datetime
from typing import get_args

import pandas as pd
from pymssql import Connection

from src import (
    bb_client_type_from_id,
    bb_device_type_from_pns_handle,
    bb_datawallet_modification_collections,
    bb_datawallet_modification_type_map,
    bb_external_event_type_map,
    bb_rel_status_map,
    is_test_client,
    DeviceType,
)


def num_identities_per_client(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientId: category (ordered)
    - ClientType: category (ordered)
    - NumIdentities
    """

    # TODO: Right Join anstatt Union 0
    query = """
    SELECT ClientId,
           count(ClientId) AS NumIdentities
    FROM Devices.Identities
    GROUP BY ClientId
    UNION
    SELECT ClientId,
           0
    FROM AdminUi.ClientOverviews
    WHERE ClientId NOT IN
        (SELECT DISTINCT ClientId
         FROM Devices.Identities);
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        # Subsetting with an empty mask degenerates a dataframe, removing all
        # column information. This holds true even for empty dataframes where
        # one would naturally expect any subsetting or filtering to be a no-op.
        # In our case we obtain empty masks where an empty result set is
        # returned by the database and thus we apply a mask if and only if it
        # is non-empty.
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df["ClientId"] = pd.Categorical(df["ClientId"], ordered=True)

    return df


def num_sent_messages_per_client(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - NumMessages
    - SenderClientId: category (ordered)
    - SenderClientType: category (ordered)
    """

    query = """
    SELECT B.ClientId AS SenderClientId,
           count(A.Id) AS NumMessages
    FROM Messages.Messages AS A
    RIGHT JOIN Devices.Identities AS B ON A.CreatedBy = B.Address
    GROUP BY B.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["SenderClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["SenderClientType"] = pd.Categorical(df["SenderClientId"].map(bb_client_type_from_id), ordered=True)
    df["SenderClientId"] = pd.Categorical(df["SenderClientId"], ordered=True)

    return df


def num_received_messages_per_client(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - NumMessages
    - RecipientClientId: category (ordered)
    - RecipientClientType: category (ordered)
    """

    query = """
    SELECT B.ClientId AS RecipientClientId,
           count(A.MessageId) as NumMessages
    FROM Messages.RecipientInformation AS A
    RIGHT JOIN Devices.Identities AS B ON A.Address = B.Address
    GROUP BY B.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["RecipientClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["RecipientClientType"] = pd.Categorical(df["RecipientClientId"].map(bb_client_type_from_id), ordered=True)
    df["RecipientClientId"] = pd.Categorical(df["RecipientClientId"], ordered=True)

    return df


def num_devices_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumDevices
    - count
    """

    query = """
    SELECT count(A.Id) as NumDevices,
           B.ClientId
    FROM
        Devices.Devices as A RIGHT JOIN Devices.Identities as B
    ON A.IdentityAddress = B.Address
    GROUP BY A.IdentityAddress, B.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df = df.groupby(["ClientType", "NumDevices"], as_index=False, observed=True).value_counts()
    return df


def num_recipients_per_sender_client_type(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - NumRecipients
    - NumSentMessages
    - SenderClientType: category (ordered)
    """

    query = """
    SELECT i.ClientId,
           count(ri.MessageId) as NumRecipients
    FROM Messages.RecipientInformation AS ri JOIN Messages.Messages AS m
    ON m.Id = ri.MessageId
    JOIN Devices.Identities i
    ON m.CreatedBy = i.Address
    GROUP BY ri.MessageId, m.CreatedBy, i.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["SenderClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df = (
        df.groupby(["SenderClientType", "NumRecipients"], observed=True, as_index=False)
        .value_counts()
        .rename(columns={"count": "NumSentMessages"})
    )
    return df


def identity_creations(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - CreatedAt: datetime64[ns]
    """

    query = """
    SELECT i.CreatedAt, i.ClientId
    FROM Devices.Identities i
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[ns]")
    return df


def messages(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - CreatedAt: datetime64[ns]
    - MessageSize
    """

    query = """
    SELECT m.CreatedAt, i.ClientId, len(m.Body) as MessageSize
    FROM Messages.Messages m
    JOIN Devices.Identities i
    ON i.Address = m.CreatedBy
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[ns]")
    return df


def external_events(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - CreatedAt: datetime64[ns]
    """

    query = """
    SELECT ee.CreatedAt, i.ClientId
    FROM Synchronization.ExternalEvents ee
    JOIN Devices.Identities i
    ON i.Address = ee.Owner
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[ns]")
    return df


def num_peers_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumPeers
    """

    query = """
    SELECT C.ClientId,
           count(C.Peer) as NumPeers
    FROM
    (
        (
            SELECT B.Address AS IdentityAddress,
                   B.ClientId,
                   A.[To] AS Peer
            FROM Relationships.Relationships as A RIGHT JOIN Devices.Identities as B
            ON A.[From] = B.Address
        )
        UNION
        (
            SELECT B.Address AS IdentityAddress,
                   B.ClientId,
                   A.[From] AS Peer
            FROM Relationships.Relationships as A RIGHT JOIN Devices.Identities as B
            ON A.[To] = B.Address
        )
    ) AS C
    GROUP BY C.IdentityAddress, C.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])

    return df


def sync_errors(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ErrorCode: category (ordered)
    - CreatedAt: datetime64[ns]
    - ClientType: category (ordered)
    """

    query = """
    SELECT se.ErrorCode, sr.CreatedAt, i.ClientId
    FROM Synchronization.SyncErrors se
    JOIN Synchronization.SyncRuns sr
    ON sr.Id = se.SyncRunId
    JOIN Devices.Identities i
    ON sr.CreatedBy = i.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[ns]")
    df["ErrorCode"] = pd.Categorical(df["ErrorCode"], ordered=True)

    return df


def relationships(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - Status: category (ordered)
    - CreatedAt: datetime64[ns]
    - AnsweredAt: datetime64[ns]
    - FromClientType: category (ordered)
    - ToClientType: category (ordered)
    """

    # TODO: Die AdminUi.XYZ Views sollten nicht verwendet werden.
    # Das Admin-UI ist relativ neu und daher noch stark in Entwicklung.
    # Entsprechend besteht die Gefahr, dass die Views sich ändern.
    query = """
    SELECT ro.Status, ro.AnsweredAt, ro.CreatedAt,
        i.ClientId as FromClientId,i2.ClientId as ToClientId
    FROM AdminUi.RelationshipOverviews ro
    JOIN Devices.Identities i
    ON i.Address = ro.[From]
    JOIN Devices.Identities i2
    ON i2.Address = ro.[To]
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["FromClientId"].map(is_test_client) & ~df["ToClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["FromClientType"] = pd.Categorical(df["FromClientId"].map(bb_client_type_from_id), ordered=True)
    df["ToClientType"] = pd.Categorical(df["ToClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["FromClientId", "ToClientId"])
    df["AnsweredAt"] = df["AnsweredAt"].astype("datetime64[ns]")
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[ns]")
    df["Status"] = pd.Categorical(
        df["Status"].map(bb_rel_status_map),
        categories=sorted(bb_rel_status_map.values()),
        ordered=True,
    )

    return df


def device_push_channel_types(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - DeviceType: category (ordered)
    """

    query = """
    SELECT X.ClientId,
           Y.Handle
    FROM
    (SELECT A.Id AS DeviceId,
            A.IdentityAddress,
            B.ClientId
    FROM Devices.Devices AS A
    JOIN Devices.Identities AS B ON A.IdentityAddress = B.Address) AS X
    LEFT JOIN Devices.PnsRegistrations AS Y ON X.DeviceId = Y.DeviceId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["DeviceType"] = pd.Categorical(
        df["Handle"].map(bb_device_type_from_pns_handle),
        sorted(get_args(DeviceType)),
        ordered=True,
    )
    df = df.drop(columns=["Handle"])
    return df


def num_relationship_templates_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumTemplates
    """

    query = """
    SELECT C.ClientId,
           count(C.TemplateId) AS NumTemplates
    FROM
    (
        SELECT
            B.Address AS IdentityAddress,
            B.ClientId as ClientId,
            A.Id as TemplateId
        FROM
            Relationships.RelationshipTemplates AS A
        RIGHT OUTER JOIN Devices.Identities AS B
            ON A.CreatedBy = B.Address
    ) AS C
    GROUP BY C.IdentityAddress, C.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])

    return df


def num_tokens_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumTokens
    """

    query = """
    SELECT C.ClientId,
           count(TokenId) as NumTokens
    FROM
    (
        SELECT A.Id as TokenId, B.Address as IdentityAddress, B.ClientId
        FROM Tokens.Tokens as A RIGHT JOIN Devices.Identities as B
        ON A.CreatedBy = B.Address
    ) AS C
    GROUP BY C.IdentityAddress, C.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])

    return df


def token_size(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - IdentityAddress
    - ClientType: category (ordered)
    - TokenSize
    """

    query = """
    SELECT B.Address as IdentityAddress,
           B.ClientId,
           LEN(A.Content) as TokenSize
    FROM Tokens.Tokens as A INNER JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)

    return df


def num_datawallet_modifications_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumDWM
    - count
    """

    query = """
    SELECT count(A.Id) as NumDWM,
           B.ClientId
    FROM Synchronization.DatawalletModifications as A RIGHT JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    GROUP BY B.Address, B.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df = df.groupby(["NumDWM", "ClientType"], as_index=False, observed=True).value_counts()

    return df


def size_of_datawallet_modifications(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - Size
    - ClientType: category (ordered)
    """

    query = """
    SELECT LEN(A.EncryptedPayload) as Size,
           B.ClientId
    FROM Synchronization.DatawalletModifications as A INNER JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["Size"] = df["Size"].fillna(0.0)

    return df


def type_of_datawallet_modifications(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - Type: category (ordered)
    - ClientType: category (ordered)
    - count
    """

    query = """
    SELECT A.Type,
           B.ClientId
    FROM Synchronization.DatawalletModifications as A JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df["Type"] = pd.Categorical(
        df["Type"].map(bb_datawallet_modification_type_map),
        sorted(bb_datawallet_modification_type_map.values()),
        ordered=True,
    )
    df = df.drop(columns=["ClientId"])
    df = df.groupby(["Type", "ClientType"], as_index=False, observed=False).value_counts()

    return df


def collection_of_datawallet_modifications(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - Collection: category (ordered)
    - ClientType: category (ordered)
    - count
    """

    query = """
    SELECT A.Collection,
           B.ClientId
    FROM Synchronization.DatawalletModifications as A JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["Collection"] = pd.Categorical(
        df["Collection"],
        sorted(bb_datawallet_modification_collections),
        ordered=True,
    )
    df = df.groupby(["Collection", "ClientType"], as_index=False, observed=False).value_counts()

    return df


def payload_category_of_datawallet_modifications(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - PayloadCategory: category (ordered)
    - ClientType: category (ordered)
    - count
    """
    # TODO: Alle möglichen Kategorien zentral hinterlegen und leere anzeigen.
    # Vgl. External Events.

    query = """
    SELECT A.PayloadCategory,
           B.ClientId
    FROM Synchronization.DatawalletModifications as A RIGHT JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["PayloadCategory"] = pd.Categorical(df["PayloadCategory"].fillna("Empty"), ordered=True)
    df = df.groupby(["PayloadCategory", "ClientType"], as_index=False, observed=True).value_counts()

    return df


def type_of_external_events(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - Count
    - ClientType: category (ordered)
    - Type: category (ordered)
    """

    query = """
    SELECT A.Type,
           B.ClientId
    FROM Synchronization.ExternalEvents as A JOIN Devices.Identities as B
    ON A.Owner = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df["Type"] = pd.Categorical(
        df["Type"].map(bb_external_event_type_map),
        categories=sorted(bb_external_event_type_map.values()),
        ordered=True,
    )
    df = df.groupby(["ClientType", "Type"], as_index=False, observed=False).value_counts()

    return df


def size_of_relationship_templates(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - RelationshipTemplateId
    - RelationshipTemplateSize
    - CreatedBy
    - ClientType: category (ordered)
    """

    query = """
    SELECT LEN(RT.Content) as RelationshipTemplateSize, I.ClientId, RT.CreatedBy, RT.Id as RelationshipTemplateId
    FROM Relationships.RelationshipTemplates as RT
    INNER JOIN Devices.Identities as I
    ON RT.CreatedBy = I.Address;
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    return df


def num_external_events_per_sync_run(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - ClientType: category (ordered)
    - NumExternalEvents
    - count
    """

    query = """
    SELECT A.Id as SyncRunId,
           B.Id as ExternalEventId,
           C.ClientId
    FROM Synchronization.SyncRuns as A LEFT JOIN Synchronization.ExternalEvents as B
    ON A.Id = B.SyncRunId
    JOIN Devices.Identities as C ON A.CreatedBy = C.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df = (
        df.groupby(["SyncRunId", "ClientType"], as_index=False, observed=True)
        .count()
        .rename(columns={"ExternalEventId": "NumExternalEvents"})
        .drop(columns=["SyncRunId"])
        .groupby(["ClientType", "NumExternalEvents"], as_index=False, observed=True)
        .value_counts()
    )

    return df


# FIXME: Unused fn
def relationship_templates_usage(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - RelationshipTemplateId
    - CreatedBy
    - MaxNumberOfAllocations
    - NumberOfAllocations
    """
    query = """
    SELECT rta.RelationshipTemplateId, rt.MaxNumberOfAllocations, rt.CreatedBy, count(*) as NumberOfAllocations
    FROM Relationships.RelationshipTemplateAllocations rta
    JOIN Relationships.RelationshipTemplates rt
    ON rt.Id = rta.RelationshipTemplateId
    GROUP BY rta.RelationshipTemplateId, rt.MaxNumberOfAllocations, rt.CreatedBy
    """
    df = pd.read_sql_query(query, cnxn)
    df["CreationClientType"] = df["CreatedBy"].map(bb_client_type_from_id).astype("category")
    if hide_test_clients:
        mask = ~df["CreatedBy"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    return df


def size_of_file_contents(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns a dataframe with the following columns:
    - FileSize
    - ClientType: category (ordered)
    """

    query = """
    SELECT A.CipherSize as FileSize,
           B.ClientId
    FROM Files.FileMetadata as A JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    return df


def num_max_rel_templ_allocations(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns dataframe with the following columns:
    - RLTCreatorClientType: category (ordered)
    - MaxAllocs
    - NumAllocs
    - RelRLTAllocs
    """

    query = """
    SELECT A.MaxNumberOfAllocations as MaxAllocs,
           B.ClientId,
           count(C.RelationshipTemplateId) as NumAllocs
    FROM Relationships.RelationshipTemplates as A
    JOIN Devices.Identities as B
    ON A.CreatedBy = B.Address
    LEFT JOIN Relationships.RelationshipTemplateAllocations as C
    ON A.Id = C.RelationshipTemplateId
    GROUP BY A.MaxNumberOfAllocations, B.ClientId, A.Id
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["RLTCreatorClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df["RelRLTAllocs"] = df["NumAllocs"] / df["MaxAllocs"]
    df.loc[df["MaxAllocs"].isna(), "RelRLTAllocs"] = pd.NA
    df = df.drop(columns=["ClientId"])
    df["MaxAllocs"] = df["MaxAllocs"].fillna(0).astype(int)
    return df


def activity_num_created_files(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns dataframe with the following columns:
    - FileId
    - CreatedAt
    - ClientType
    """
    query = """
    SELECT fm.Id as FileId, fm.CreatedAt, i.ClientId
    FROM Files.Filemetadata as fm
    JOIN Devices.Identities i
    ON i.Address = fm.CreatedBy
    """
    # TODO: Remove deleted files from df?
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    return df


def num_files_per_identity(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns dataframe with the following columns:
    - ClientType: category (ordered)
    - NumFiles
    - count
    """

    query = """
    SELECT i.ClientId, count(fm.Id) as NumFiles
    FROM Files.Filemetadata fm
    RIGHT JOIN Devices.Identities i
    ON i.Address = fm.CreatedBy
    GROUP BY i.Address, i.ClientId
    """
    df = pd.read_sql_query(query, cnxn)

    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]
    df["ClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df = df.drop(columns=["ClientId"])
    df = df.groupby(["ClientType", "NumFiles"], as_index=False, observed=True).value_counts()
    return df


def rlt_time_until_first_usage(
    cnxn: Connection,
    hide_test_clients: bool,
) -> pd.DataFrame:
    """
    Returns dataframe with the following columns:
    - TimeUntilFirstUsage: timedelta64[us]
    - RLTCreatorClientType: category (ordered)
    - ExpiredUnallocated: bool
    """

    query = """
    SELECT A.CreatedAt,
           A.ExpiresAt,
           C.ClientId,
           COUNT(B.AllocatedAt) as NumAllocations,
           MIN(B.AllocatedAt) as FirstAllocatedAt
    FROM Relationships.RelationshipTemplates as A
    LEFT JOIN Relationships.RelationshipTemplateAllocations as B
    ON A.Id = B.RelationshipTemplateId
    JOIN Devices.Identities as C
    ON A.CreatedBy = C.Address
    GROUP BY A.Id, A.CreatedAt, A.CreatedBy, A.ExpiresAt, C.ClientId
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        mask = ~df["ClientId"].map(is_test_client)
        if len(mask) > 0:
            df = df[mask]

    # ExpiresAt contains large timestamps (9999-12-31) which overflow
    # datetime64[ns]. We thus use us-precision here.
    df["CreatedAt"] = df["CreatedAt"].astype("datetime64[us]")
    df["ExpiresAt"] = df["ExpiresAt"].astype("datetime64[us]").fillna("9999-12-31")
    df["FirstAllocatedAt"] = df["FirstAllocatedAt"].astype("datetime64[us]")

    df["RLTCreatorClientType"] = pd.Categorical(df["ClientId"].map(bb_client_type_from_id), ordered=True)
    df["TimeUntilFirstUsage"] = df["FirstAllocatedAt"] - df["CreatedAt"]
    df["ExpiredUnallocated"] = (df["ExpiresAt"] <= datetime.now()) & (df["NumAllocations"] == 0)
    df = df.drop(columns=["ClientId", "FirstAllocatedAt", "CreatedAt", "ExpiresAt", "NumAllocations"])

    return df
