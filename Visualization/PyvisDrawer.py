from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx

from Drawer import Drawer


class PyvisDrawer(Drawer):

    GRAPH_OUTPUT = 'Output/pyvis_graph.html'

    def drawGraph(self, nodes, edges):
        # G = Network(directed=True)
        G = nx.DiGraph()

        group_id = 0
        # level = 0
        for arr_nodes in nodes:
            for node in arr_nodes:
                G.add_node(node.id, size=10, label=str(node.id), title=node.name, group=group_id)
            #     level=
            group_id += 1
            # level += 1

        for arr_edges in edges:
            for edge in arr_edges:
                G.add_edge(edge.source_node.id, edge.destination_node.id, title=str(edge.transfer_time), label=str(edge.id))



        network = Network(height="750px", width="100%", directed = True,
                          bgcolor="#222222", font_color="white", layout = True)
        network.show_buttons(filter_=['layout', 'interaction', 'manipulation', 'physics'])
        network.from_nx(G)
        network.show(self.GRAPH_OUTPUT)


    def drawTimes(self, nodes):

        arr_color = ['tab:blue', 'tab:orange', 'tab:red', 'tab:green', 'tab:purple', 'tab:brown', 'tab:pink',
                     'tab:gray', 'tab:olive', 'tab:cyan']
        fig, ax = plt.subplots()

        yticks = []
        y_labels = []
        num_nodes = 0
        for arr in nodes:
            num_nodes += len(arr)

        i = 0
        for arr in nodes:
            for node in arr:
                if node.name != "entry" and node.name != "finish":
                    ax.broken_barh([(node.start_time, node.finish_time - node.start_time)], (num_nodes, 0.8), facecolors=arr_color[i])
                    num_nodes -= 1

                    yticks.append(num_nodes + 1)
                    y_labels.append(node.id)
            i += 1


        ax.set_ylim(0, num_nodes)
        ax.set_xlim(0, nodes[-1][-2].finish_time)
        ax.set_xlabel('time')
        ax.set_ylabel('tasks')
        ax.set_yticks(yticks, labels=y_labels)
        ax.grid(False)

        plt.show()
        fig.savefig(self.GANTT_OUTPUT, format="pdf")

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
