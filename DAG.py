from multipledispatch import dispatch

"""
TODO:
	1) Ввести таблицу производительности процессоров для каждой из подзадач
	2) Добавить в критический путь вермя выполнения задания 
	3) Сделать выдачу упорядоченного (по априорному времени выполнения) 
	массива всех критических путей
	4) Объединить с модулем визуализации
	5) Раскрашивать критический путь на графе (посмотреть вохможности Graphviz,
	 если нет то NetworkX из гитхаба)
"""

class Node:  # Job

    def __init__(self, id, name, runtime):
        self.id = id
        self.name = name
        self.runtime = runtime
        self.visited = False
        self.children = []
        self.cp = [id]
        self.cp_length = -1


    def add_children(self, node):
        self.children.append(node)


    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", name = " + self.name + \
               ", runtime = " + str(self.runtime)

class DAG:  # JobFlow

    def __init__(self):
        self.nodes = []
        self.node_dict = {}
        self.edges = []
        self.start_edges = None
        self.finish_edges = None
        self.dp = []        # dynamic programming table
        self.add_node(0, 'entry', 0.0)


    def set_dp(self):
        # n = len(self.nodes)
        n = len(self.node_dict)
        self.dp = [[0] * (n+1) for i in range(n+1)] # n+1 = + finish_node
        self.start_edges = [0 for i in range(n+1)]
        self.finish_edges = [0 for i in range(n+1)]

    @dispatch(int, str, float)
    def add_node(self, id, name, runtime):
        node = Node(id, name, runtime)
        self.nodes.append(node)
        self.node_dict[node.id] = node

    @dispatch(Node)
    def add_node(self, node):
        self.nodes.append(node)
        self.node_dict[node.id] = node


    def add_edge(self, edge):
        self.edges.append(edge)
        edge.source_node.add_children(edge.destination_node)
        self.dp[edge.source_node.id][edge.destination_node.id] = edge.transfer_time

        self.start_edges[edge.destination_node.id] = 1
        self.finish_edges[edge.source_node.id] = 1

    def complete_graph(self):
        n = len(self.nodes)
        for i in range(1, n):
            if self.start_edges[i] == 0:
                self.add_edge(Edge(self.nodes[0], self.nodes[i], 0.0))

        self.add_node(Node(len(self.nodes), 'finish', 0.0))

        for i in range(1, n):
            if self.finish_edges[i] == 0:
                self.add_edge(Edge(self.nodes[i], self.nodes[-1], 0.0))

    def findLongestPath(self):
        self.complete_graph()

        for node in self.nodes:
            if not node.visited:
                self.dfs(node, self.dp)

        for node in self.nodes:
            print(node.id, node.cp_length, node.cp)

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






class Edge:  # Data transfer

    def __init__(self, source_node, destination_node, transfer_time):
        self.source_node = source_node
        self.destination_node = destination_node
        self.transfer_time = transfer_time


    def __str__(self):
        return str(self.source_node.id) + \
               " --> " + str(self.destination_node.id) + \
               ", transfer_time = " + str(self.transfer_time)




if __name__ == "__main__":

    g = DAG()
    g.add_node(0, 1)
    g.add_node(1, 2)
    g.add_node(2, 3)
    g.add_node(3, 4)

    g.set_dp()

    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 5)
    g.add_edge(2, 1, 6)
    g.add_edge(1, 3, 7)
    g.add_edge(2, 3, 2)

    for i in g.nodes:
        print(i)

    for i in g.edges:
        print(i)

    print(g.findLongestPath())