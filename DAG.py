from multipledispatch import dispatch

from Visualization import GraphvizModule

"""
TODO:
	1) Ввести таблицу производительности процессоров для каждой из подзадач
	2) Сравнить возможности Graphviz и NetworkX (из github)
"""

class DAG:  # JobFlow

    def __init__(self):
        self.nodes = []
        self.node_dict = {}
        self.edges = []
        self.start_edges = None
        self.finish_edges = None
        self.dp = []        # dynamic programming table
        self.graphviz_nodes = []
        self.graphviz_edges = []


    def set_dp(self):
        n = len(self.nodes)
        self.dp = [[0] * (n) for i in range(n)]
        self.start_edges = [0 for i in range(n)]
        self.finish_edges = [0 for i in range(n)]


    def add_node(self, node):
        self.nodes.append(node)
        self.graphviz_nodes.append(node)
        self.node_dict[node.name] = node


    def add_edge(self, edge):
        self.edges.append(edge)
        self.graphviz_edges.append(edge)
        edge.source_node.add_children(edge.destination_node)
        self.dp[edge.source_node.id][edge.destination_node.id] = edge.transfer_time

        self.start_edges[edge.destination_node.id] = 1
        self.finish_edges[edge.source_node.id] = 1

    def design_graph(self, soup_nodes, soup_edges):

        # Add entry_node into graph
        self.add_node(Node(0, 'entry', 0.0))

        i = 1
        for node in soup_nodes:
            name = node.get('id')
            runtime = node.get('runtime')
            self.add_node(Node(i, name, runtime))
            i += 1

        # Add finish_node into graph
        self.add_node(Node(len(self.nodes), 'finish', 0.0))
        self.set_dp()

        for edge in soup_edges:
            parents = edge.find_all('parent')
            for parent in parents:
                node_from = self.node_dict.get(parent.get('ref'))
                node_to = self.node_dict.get(edge.get('ref'))
                transfer_time = float(parent.get('transfertime'))
                self.add_edge(Edge(node_from, node_to, transfer_time))


        print(self.findLongestPath())

        GraphvizModule.graphviz_run(self.graphviz_nodes, self.graphviz_edges)

    def complete_graph(self):
        n = len(self.nodes)
        for i in range(1, n-1):
            if self.start_edges[i] == 0:
                self.add_edge(Edge(self.nodes[0], self.nodes[i], 0.0))

        for i in range(1, n-1):
            if self.finish_edges[i] == 0:
                self.add_edge(Edge(self.nodes[i], self.nodes[-1], 0.0))

    def findLongestPath(self):
        self.complete_graph()

        for node in self.nodes:
            if not node.visited:
                self.dfs(node, self.dp)

        for node in self.nodes:
            print(node.id, node.cp_length, node.cp)

        for i in self.nodes[0].cp:
            self.nodes[i].color = 'red'

        return self.nodes[0].cp_length, self.nodes[0].cp


    def dfs(self, node, dp):
        node.visited = True
        children = node.children

        for child in children:
            if not child.visited:
                self.dfs(child, dp)

            if bool(child.children):
                add_weight = max(dp[child.id])
            else:
                add_weight = 0

            if dp[node.id][child.id] <= dp[node.id][child.id] + add_weight:
                dp[node.id][child.id] += add_weight
                if node.cp_length < dp[node.id][child.id]:
                    node.cp = [node.id] + child.cp
                    node.cp_length = dp[node.id][child.id]


class Node:  # Job
    def __init__(self, id, name, runtime):
        self.id = id
        self.name = name
        self.runtime = runtime
        self.visited = False
        self.children = []
        self.cp = [id]
        self.cp_length = -1
        self.color = 'black'


    def add_children(self, node):
        self.children.append(node)


    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", name = " + self.name + \
               ", runtime = " + str(self.runtime)



class Edge:  # Data transfer

    def __init__(self, source_node, destination_node, transfer_time):
        self.source_node = source_node
        self.destination_node = destination_node
        self.transfer_time = transfer_time


    def __str__(self):
        return str(self.source_node.id) + \
               " --> " + str(self.destination_node.id) + \
               ", transfer_time = " + str(self.transfer_time)