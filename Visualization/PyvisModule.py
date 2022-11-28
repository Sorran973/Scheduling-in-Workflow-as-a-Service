from pyvis.network import Network
import networkx as nx

def pyvis_run(nodes, edges):

    G = Network(directed=True)
    # G.add_nodes(ids, value=values, title=titles)
    # G.add_edges(edges)
    for node in nodes:
        G.add_node(node.name, size=10, label=node.name, title=node.volume)

    for edge in edges:
        G.add_edge(edge.source, edge.destination, title=edge.transfer_time)
    # G.add_edge(7, 5, weight=100, label=10, title='2 / 0')

    G.show_buttons(filter_=['physics'])
    G.show('Output/network.html')

#--------------------------------------------------------#
    # G = nx.DiGraph()

    # G.add_nodes_from([
    #     (0, {"size": 50}),
    #     (1, {"label": "Fuck", "title": "10"}),
    #     (2, {"weight": 5, "utility": 10}),
    #     (3, {"weight": 5, "utility": 10}),
    #     (4, {"weight": 5, "utility": 10}),
    #     (5, {"weight": 5, "utility": 10})
    # ])


    # G.add_node(0, size=25, label='test', title='name1', group=1)
    # G.add_node(1, size=15, label='test2', title='name2', group=2)

    # for node in nodes:
    #     G.add_node(node.index, label=node.name, title=node.volume)

    # g.add_nodes([1, 2, 3], value=[10, 100, 400],
    #             title=['I am node 1', 'node 2 here', 'and im node 3'],
    #             x=[21.4, 54.2, 11.2],
    #             y=[100.2, 23.54, 32.1],
    #             label=['NODE 1', 'NODE 2', 'NODE 3'],
    #             color=['#00ff1e', '#162347', '#dd4b39'])


    # G.add_edges_from([
    #     (0, 1, {"label": "1", "title": "2/0"})
    # ])
    # G.add_edge(0, 1, weight=100, label=10, title='2 / 0')

    # network = Network('500px', '500px')
    # network.from_nx(G)
