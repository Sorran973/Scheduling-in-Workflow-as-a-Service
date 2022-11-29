
class Graph:  # JobFlow
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.dp = []        # dynamic programming table
        # self.add_node(-1, 0)

    def set_dp(self):
        n = len(self.nodes)
        self.dp = [[0] * (n) for i in range(n)]

    def add_node(self, id, runtime, name='_'):
        node = Node(id, runtime, name)
        self.nodes.append(node)
        return node

    def add_edge(self, source, destination, transfer_time):
        src = self.nodes[source]
        dst = self.nodes[destination]
        edge = Edge(src, dst, transfer_time)
        self.edges.append(edge)
        src.add_children(dst)
        self.dp[source][destination] = transfer_time

    def findLongestPath(self):

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



class Node:  # Job
    def __init__(self, id, runtime, name='_'):
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


class Edge:  # Data transfer
    def __init__(self, source, destination, transfer_time):
        self.source = source
        self.destination = destination
        self.transfer_time = transfer_time

    def __str__(self):
        return str(self.source.id) + \
               " --> " + str(self.destination.id) + \
               ", transfer_time = " + str(self.transfer_time)




if __name__ == "__main__":

    g = Graph()
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