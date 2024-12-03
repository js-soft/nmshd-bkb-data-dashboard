import networkx as nx
import pandas as pd
from pyodbc import Connection

from src import bb_client_type_from_id, is_test_client

from .plotly_plots import client_type_colmap


def make_rel_network(
    cnxn: Connection,
    hide_test_clients: bool,
) -> nx.Graph:
    """
    Returns graph of active relationships as well as isolated nodes.
    Nodes have the following metadata keys:
        - 'ClientId'
        - 'ClientType'
    Links have the following metadata keys:
        - 'NumMessages': Total number of messages exchanged between the peers.
    """

    # Set up network nodes including their client type.
    query = """
        SELECT Address,
               ClientId
        FROM Devices.Identities
    """
    df = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        df = df[~df["ClientId"].map(is_test_client)]

    df["ClientType"] = df["ClientId"].map(bb_client_type_from_id).astype("category")
    df = df.set_index("Address", verify_integrity=True)

    nodes = [
        (idx, {"ClientType": ctype, "ClientId": cid})
        for idx, ctype, cid in zip(df.index, df["ClientType"].values, df["ClientId"])
    ]
    net = nx.Graph()
    net.add_nodes_from(nodes)

    # Add edges
    query = """
        SELECT A.[From] AS FromAddress,
            A.[To] AS ToAddress,
            B.ClientId AS FromClientId,
            C.ClientId AS ToClientId,
            D.NumMessages
        FROM Relationships.Relationships AS A
        JOIN Devices.Identities AS B
        ON A.[From] = B.Address
        JOIN Devices.Identities AS C
        ON A.[To] = C.Address
        JOIN (
            SELECT ri.RelationshipId, count(*) as NumMessages
            FROM Messages.RecipientInformation ri
            GROUP BY ri.RelationshipId
        ) as D
        ON A.Id = D.RelationshipId
        WHERE A.Status = 20
    """
    df_active_rels = pd.read_sql_query(query, cnxn)
    if hide_test_clients:
        # If either of the peers is a test client, we hide the relationship
        is_test = df_active_rels["FromClientId"].map(is_test_client) | df_active_rels["ToClientId"].map(is_test_client)
        df_active_rels = df_active_rels[~is_test]

    edges = zip(
        df_active_rels["FromAddress"].values,
        df_active_rels["ToAddress"].values,
        [{"NumMessages": num} for num in df_active_rels["NumMessages"]],
    )
    net.add_edges_from(edges)

    return net


def forcegraph_data(rel_network: nx.Graph) -> dict:
    """
    Exports relationship network data compatible with force-graph.js.
    """
    # Sorting nodes by degree (descending) produces a nice layout where
    # isolated and low-degree nodes are on the outside, surrounding node
    # clusters on the inside.
    sorted_nodes = sorted(
        rel_network.nodes(data=True),
        key=lambda x: rel_network.degree[x[0]],
        reverse=True,
    )
    nodes = [
        {
            "Address": _id,
            "Color": client_type_colmap[data["ClientType"]],
            "NumPeers": rel_network.degree[_id],
            "Peers": list(rel_network.neighbors(_id)),
            **data,
        }
        for _id, data in sorted_nodes
    ]
    links = [
        {
            "source": a,
            "target": b,
            **data,
        }
        for a, b, data in rel_network.edges(data=True)
    ]
    return {"nodes": nodes, "links": links}
