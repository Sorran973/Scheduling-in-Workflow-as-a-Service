from pyvis.network import Network
import matplotlib.pyplot as plt
import networkx as nx

from Drawer import Drawer


class PyvisDrawer(Drawer):

    GRAPH_OUTPUT = 'Output/pyvis_graph.html'

    def draw_graph(self, nodes, edges):
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



        network = Network(height="750px", width="100%", directed=True,
                          bgcolor="white", font_color="black", layout=True)
        # network.show_buttons(filter_=['layout', 'interaction', 'manipulation', 'physics'])

        network.set_options('var options = { "layout": { "hierarchical": { "enabled" : true, '
                            '"levelSeparation" : 150, "nodeSpacing" : 100, "treeSpacing" : 200, '
                            '"blockShifting" : true, "edgeMinimization" : true, "parentCentralization": true, '
                            '"direction" : "UD", "sortMethod" : "directed", "shakeTowards" : "roots"} } }')

        network.from_nx(G)
        network.show(self.GRAPH_OUTPUT)


    def draw_gantt(self, nodes):

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

                    yticks.append(num_nodes + 2)
                    y_labels.append(node.id - 1)
            i += 1


        ax.set_ylim(0, num_nodes)
        ax.set_xlim(0, nodes[-1][-2].finish_time)
        ax.set_xlabel('time')
        ax.set_ylabel('tasks')
        ax.set_yticks(yticks, labels=y_labels)
        ax.grid(False)

        plt.show()
        fig.savefig(self.GANTT_OUTPUT, format="pdf")