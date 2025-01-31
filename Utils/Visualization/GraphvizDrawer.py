import graphviz
import matplotlib.pyplot as plt
from Utils.Visualization.Drawer import Drawer


class GraphvizDrawer(Drawer):

    GRAPH_OUTPUT = 'Output/graph.gv'

    def draw_graph(self, nodes, edges):

        G = graphviz.Digraph(filename=self.GRAPH_OUTPUT)
        for arr in nodes:
            for node in arr:
                G.node(str(node.id) + '\n' +
                       node.name + '\n' +
                       str(node.start_time) + '\n' +
                       str(node.runtime))
                       # color=node.color)

        for arr in edges:
            for edge in arr:
                G.edge(str(edge.node_from.id) + '\n' +
                       edge.node_from.name + '\n' +
                       str(edge.node_from.start_time) + '\n' +
                       str(edge.node_from.runtime),

                       str(edge.node_to.id) + '\n' +
                       edge.node_to.name + '\n' +
                       str(edge.node_to.start_time) + '\n' +
                       str(edge.node_to.runtime),

                       str(edge.transfer_time))

        G.view()

    def draw_gantt(self, nodes):

        fig, ax = plt.subplots()

        yticks = []
        y_labels = []
        num_nodes = 0
        for arr in nodes:
            num_nodes += len(arr)


        for arr in nodes:
            for node in arr:
                if node.name != "entry" and node.name != "finish":
                    ax.broken_barh([(node.start_time, node.finish_time - node.start_time)], (num_nodes, 0.8), facecolors='tab:blue')
                    num_nodes -= 1

                    yticks.append(num_nodes + 1)
                    y_labels.append(node.id)


        ax.set_ylim(0, num_nodes)
        ax.set_xlim(0, nodes[-1][-2].finish_time)
        ax.set_xlabel('time')
        ax.set_ylabel('tasks')
        ax.set_yticks(yticks, labels=y_labels)
        ax.grid(True)

        plt.show()
        fig.savefig(self.GANTT_OUTPUT, format="pdf")