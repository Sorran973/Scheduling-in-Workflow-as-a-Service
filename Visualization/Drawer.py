from abc import ABC, abstractmethod

import graphviz


class Drawer(ABC):
    @abstractmethod
    def draw(self):
        pass


class GraphvizDrawer(Drawer):
    def draw(self, arr_nodes, arr_edges):

        G = graphviz.Digraph(filename='Output/graph_picture.gv')
        for arr in arr_nodes:
            for node in arr:
                G.node(str(node.id) + '\n' +
                       node.name + '\n' +
                       str(node.start_time) + '\n' +
                       str(node.runtime),
                       color=node.color)

        for arr in arr_edges:
            for edge in arr:
                G.edge(str(edge.source_node.id) + '\n' +
                       edge.source_node.name + '\n' +
                       str(edge.source_node.start_time) + '\n' +
                       str(edge.source_node.runtime),

                       str(edge.destination_node.id) + '\n' +
                       edge.destination_node.name + '\n' +
                       str(edge.destination_node.start_time) + '\n' +
                       str(edge.destination_node.runtime),

                       str(edge.transfer_time))

        G.view()




