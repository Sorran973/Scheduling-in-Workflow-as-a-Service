import graphviz

def graphviz_run(job):
    nodes = job.draw_nodes
    edges = job.draw_edges
    G = graphviz.Digraph(filename='Output/graph_picture.gv')
    for node in nodes:
        G.node(node.name + '\n(' + str(node.runtime) + ')', color=node.color)

    for edge in edges:
        G.edge(edge.source_node.name + '\n(' + str(edge.source_node.runtime) + ')',
               edge.destination_node.name + '\n(' + str(edge.destination_node.runtime) + ')',
               str(edge.transfer_time))

    G.view()


