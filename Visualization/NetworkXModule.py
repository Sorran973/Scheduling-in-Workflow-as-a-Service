import matplotlib.pyplot as plt
import networkx as nx

def networkx_run(nodes, edges):
    # G = nx.DiGraph()
    #
    # for node in nodes:
    #     G.add_node(node.name + '\n(' + node.volume + ')')
    #
    # for edge in edges:
    #     G.add_edge(edge.source, edge.destination, weight=int(edge.transfer_time))

    # ----------------------------------------------------------------------------------

    G = nx.DiGraph()
    G.add_nodes_from([
        ("1", {"Age": 4}),
        ("2", {"Age": 146}),
        ("3", {"Age": 88}),
        ("4", {"Age": 338}),
        ("5", {"Age": 78}),
        ("6", {"Age": 4570})
    ])

    G.add_edges_from([
        ("3", "5", {"weight": 10}),
        ("2", "5", {"weight": 20}),
        ("4", "5", {"weight": 30}),
        ("5", "6", {"weight": 50}),
        ("1", "2", {"weight": 10}),
        ("1", "3", {"weight": 15})
    ])

    pos = {
        "1": (1, 5),
        "2": (4.5, 6.6),
        "3": (3.6, 1.4),
        "4": (3.6, -1.4),
        "5": (6.9, 3.6),
        "6": (10.1, 3.6)
    }

    pos_node_attributes = {
        "1": (-0.2, 5),
        "2": (4.5, 7.9),
        "3": (2.4, 1.4),
        "4": (2.2, -1.4),
        "5": (5.6, 3.6),
        "6": (10.1, 5.0)
    }
    node_labels = {n: (d["Age"]) for n, d in G.nodes(data=True)}

    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}

    nx.draw(G, pos=pos, with_labels=True,
            node_color="blue", node_size=3000,
            font_color="white", font_size=20, font_family="Times New Roman", font_weight="bold",
            edge_color="lightgray",
            width=5)
    nx.draw_networkx_labels(G, pos=pos_node_attributes, labels=node_labels, font_color="black", font_size=12,
                            font_family="Times New Roman", font_weight="bold")

    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, label_pos=0.5)
    nx.draw(G, node_size=300, width=3)
    plt.margins(0.2)
    plt.show()


