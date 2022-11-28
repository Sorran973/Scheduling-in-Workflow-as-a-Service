import graphviz

def graphviz_run(nodes, edges):
    G = graphviz.Digraph(filename='../Output/result_graph.gv')
    for node in nodes:
        G.node(node.name + '\n(' + node.volume + ')')

    for edge in edges:
        G.edge(edge.source, edge.destination, edge.transfer_time)
    G.view()

#----------------------------------------------------#
    # with d.subgraph() as s:
    #     s.attr(rank='same')
    #     s.node('A')
    #     s.node('X')
    # d.edges(['AB', 'AC', 'CD', 'XY'])
    # G.edges(edges)


