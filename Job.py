import random

from Edge import Edge
from File import File
from Node import Node
from Layer import Layer
from Strategy import Strategy

import math
import copy


class Job:  # JobFlow

    global_timer = 0

    def __init__(self, soup_nodes, soup_edges):
        self.nodes = []
        self.node_dict = {} # [str(node_name) : obj(node)]
        self.edges = []
        self.entry_edges = None # for setting edges between entry_node and his children
        self.finish_edges = None # -//- finish_node and his children
        self.dp = []        # dynamic programming table
        self.graphviz_nodes = []
        self.graphviz_edges = []
        self.critical_paths = []
        self.strategies = []
        self.local_strategies = []
        # self.T = 300
        self.processor_number = 5
        self.processor_table = []
        # self.T = 300            # p0    p1    p2    p3    p4    p5    p6    p7    p8    p9    p10
        # self.processor_table = [[72.0, 57.0, 73.0, 54.0, 60.0, 72.0, 60.0, 54.0, 67.0, 60.0, 62.0],
        #                         [78.0, 58.0, 85.0, 68.0, 75.0, 79.0, 75.0, 54.0, 74.0, 67.0, 67.0],
        #                         [82.0, 78.0, 90.0, 73.0, 84.0, 88.0, 84.0, 75.0, 80.0, 69.0, 68.0],
        #                         [88.0, 87.0, 93.0, 82.0, 86.0, 90.0, 89.0, 86.0, 87.0, 69.0, 80.0],
        #                         [90.0, 89.0, 94.0, 83.0, 92.0, 91.0, 93.0, 92.0, 89.0, 83.0, 84.0],
        #                         [94.0, 89.0, 94.0, 88.0, 92.0, 92.0, 93.0, 92.0, 89.0, 85.0, 87.0]]

        # self.T = 15             # p1    p2    p3    p4   p5    p6
        # self.processor_table = [[ 2.0,  3.0, 1.0,  2.0, 1.0,  2.0],
        #                         [ 4.0,  6.0, 2.0,  4.0, 2.0,  4.0],
        #                         [ 6.0,  9.0, 3.0,  6.0, 3.0,  6.0],
        #                         [ 8.0, 12.0, 4.0,  8.0, 4.0,  8.0],
        #                         [10.0, 15.0, 5.0, 10.0, 5.0, 10.0]]


        # Steps
        self.create_graph(soup_nodes, soup_edges)
        self.find_all_critical_paths()
        self.check_duplicate_critical_paths()
        self.create_processor_table()
        self.schedule()
        print(self.T)


    def create_graph(self, soup_nodes, soup_edges):
        # Add entry_node into graph
        self.add_node(Node('entry', 0.0))

        for node in soup_nodes:
            name = node.get('id')
            runtime = node.get('runtime')
            current_node = Node(name, float(runtime))
            self.add_node(current_node)

            uses = node.find_all('uses')
            for use in uses:
                current_node.add_file(File(use.get('file'), use.get('link'), float(use.get('size'))))

        # Add finish_node into graph
        self.add_node(Node('finish', 0.0))
        self.nodes[-1].critical_paths.append([0, [self.nodes[-1]]])

        # Create dp_table
        self.set_dp()

        for edge in soup_edges: # edge = child and all his parent
            parents = edge.find_all('parent')
            for parent in parents:
                node_from = self.node_dict.get(parent.get('ref'))
                node_to = self.node_dict.get(edge.get('ref'))
                transfer_time = float(parent.get('transfertime'))
                transfer_size = node_from.output_size
                self.add_edge(Edge(node_from, node_to, transfer_time, transfer_size))

        # Add entry and finish edges
        self.complete_graph()

    def add_node(self, node):
        self.nodes.append(node)
        self.graphviz_nodes.append(node)
        self.node_dict[node.name] = node
    def set_dp(self):
        n = len(self.nodes)
        self.dp = [[0.0] * (n) for i in range(n)]
        self.entry_edges = [0 for i in range(n)]
        self.finish_edges = [0 for i in range(n)]
    def add_edge(self, edge):
        self.edges.append(edge)
        self.graphviz_edges.append(edge)
        edge.source_node.add_edge(edge)
        self.dp[edge.source_node.id][edge.destination_node.id] = edge.transfer_time

        self.entry_edges[edge.destination_node.id] = 1
        self.finish_edges[edge.source_node.id] = 1

    def find_all_critical_paths(self):
        for node in self.nodes:
            if not node.visited:
                self.dfs(node, self.dp)

        # sorting of all critical paths based on process time (length) in descending order
        self.nodes[0].critical_paths.sort(key=self.sort_for_critical_paths, reverse=True)
        for c_p in self.nodes[0].critical_paths:
            print(c_p[0], c_p[1])

        # set T from the critical path
        t = self.round_up(self.nodes[0].critical_paths[0][0])
        self.T = random.randint(t, t*2)
        # self.T = 1000
        c_p = self.nodes[0].critical_paths[0][1]
        for i in range(0, len(c_p), 2): # because critical_path consists of nodes and edges
            c_p[i].color = 'red'

    def complete_graph(self): # add entry and finish edges
        n = len(self.nodes)
        for i in range(1, n-1):
            if self.entry_edges[i] == 0:
                self.add_edge(Edge(self.nodes[0], self.nodes[i], 0.0, 0.0))

        for i in range(1, n-1):
            if self.finish_edges[i] == 0:
                self.add_edge(Edge(self.nodes[i], self.nodes[-1], 0.0, 0.0))

    def dfs(self, node, dp):
        node.visited = True
        node_edges = node.edges

        for node_edge in node_edges:
            node_child = node_edge.destination_node
            if not node_child.visited:
                self.dfs(node_child, dp)

            for critical_path in node_child.critical_paths:
                node.critical_paths.append((node.runtime + node_edge.transfer_time + critical_path[0],
                                            [node, node_edge] + critical_path[1]))

    def sort_for_critical_paths(self, critical_path):
        return critical_path[0]

    def round_up(self, n, decimals=0):
        multiplier = 10 ** decimals
        return math.ceil(n * multiplier) / multiplier

    def check_duplicate_critical_paths(self): # check duplications
        critical_paths = self.nodes[0].critical_paths
        for c_p in critical_paths:
            for elem in c_p[1]:
                if not elem.in_critical_path:
                    self.critical_paths.append(c_p)
                    self.mark_whole_path(c_p)

        print("\nAll critical paths without duplications:")
        for c_p in self.critical_paths:
            print(c_p[0], c_p[1])

    def mark_whole_path(self, path):
        for elem in path[1]:
            elem.in_critical_path = True

    def common_member(self, list_a, list_b):
        result = []
        for node in list_b:
            if list_a[node.id-1] != -math.inf:
                result.append(node)

        return result

    def create_processor_table(self):
        for i in range(1, self.processor_number + 1):
            processor_value = []
            for j in range(1, len(self.nodes)-1):
                processor_value.append(round(self.nodes[j].runtime * i, 2))
            self.processor_table.append(processor_value)

    def schedule(self):

        for critical_path in self.critical_paths:
            flag = False
            self.local_strategies = []
            layer = Layer()

            c_p = critical_path[1]
            del c_p[-2:] # delete entry node and edge
            del c_p[0:2] # delete finish node and edge

            Z1 = self.T
            for i in range(len(c_p)-2, 0, -2): # delete edges
                Z1 -= c_p[i].transfer_time
                del c_p[i]

            if not self.strategies:
                layer = self.next_layer_calc(Z1, c_p, 0) # direct pass
                self.set_node_times(c_p, c_p, layer)  # reverse pass
            else:
                strategy = self.strategies[0]
                local_c_p = copy.copy(c_p)
                local_Z1 = Z1
                common_nodes = self.common_member(strategy.time, c_p)
                if not common_nodes:
                    flag = True
                else:
                    for node in common_nodes:
                        local_Z1 -= strategy.time[node.id-1]
                        local_c_p.remove(node)

                if local_Z1 < 0:
                    r = 5
                if len(local_c_p) > 0: # if all nodes are already calculated
                    layer = self.next_layer_calc(local_Z1, local_c_p, 0) # direct pass
                    self.set_node_times(c_p, local_c_p, layer) # reverse pass



            if not layer.CF_layer: # if all nodes are already calculated
                continue

            l = len(self.nodes) - 2 # - entry and finish nodes
            time = [-math.inf] * l
            criteria = [-math.inf] * l

            strategy = Strategy(c_p, time, criteria)
            self.create_strategy(strategy, layer)

            new_strategy = self.local_strategies[0]

            if not self.local_strategies:
                continue
            else:
                if self.strategies:
                    strategy = self.strategies[0]
                    for i in range(l):
                        if strategy.time[i] != new_strategy.time[i] and strategy.time[i] == -math.inf:
                            strategy.criteria[i] = new_strategy.criteria[i]
                            strategy.time[i] = new_strategy.time[i]
                        if strategy.time[i] != new_strategy.time[i] and strategy.time[i] != -math.inf and new_strategy.time[i] != -math.inf:
                            break
                        else:
                            continue
                else:
                    self.strategies.append(new_strategy)

            # if not flag:
            #     for strategy in self.local_strategies:
            #         self.strategies.append(strategy)

            print(self.strategies[0].time)


    def create_strategy(self, strategy, layer):
        if not layer.previous_layers:
            for i in range(len(layer.options)):
                new_strategy = Strategy(strategy.c_p, strategy.time, strategy.criteria)
                new_strategy.change(layer.node_id, self.round_up(layer.options[i][0], 2), self.round_up(layer.options[i][1], 2))
                self.local_strategies.append(new_strategy)
        else:
            for i in range(len(layer.options)):
                new_strategy = Strategy(strategy.c_p, strategy.time, strategy.criteria)
                new_strategy.change(layer.node_id, self.round_up(layer.options[i][0], 2), self.round_up(layer.options[i][1], 2))
                self.create_strategy(new_strategy, layer.previous_layers[i])

    def next_layer_calc(self, reserve, c_p, node_index):

        if node_index == len(c_p)-1: # if the layer is the last one
            t_node = reserve
            if t_node < 0:
                r = 5
            # C_node = self.criteria_func(c_p[node_index].id - 1, t_node)
            index = self.find_index(t_node, c_p[node_index].id - 1)
            C_node = self.criteria_func(self.processor_table[index][c_p[node_index].id - 1])
            CF_node = C_node

            return Layer(c_p[node_index].id, CF_node, [[C_node, t_node, None, None]], [])

        else:
            # Z_next_node = [reserve - self.processor_table[i][c_p[node_index].id - 1]
            #                for i in range(len(self.processor_table))
            #                if (reserve - self.processor_table[i][c_p[node_index].id - 1]) >=
            #                self.processor_table[0][c_p[node_index+1].id - 1]]
            Z_next_node = []
            for i in range(len(self.processor_table)):
                a = reserve - self.processor_table[i][c_p[node_index].id - 1]
                b = 0
                for j in range(node_index + 1, len(c_p)): # rest reserve on the fastest processors
                    b += self.processor_table[0][c_p[j].id - 1]
                if a >= b:
                    Z_next_node.append(a)
                else:
                    break

            if not Z_next_node:
                return []

            t_node = [self.processor_table[i][c_p[node_index].id - 1] for i in range(0, len(Z_next_node))]

            if len(Z_next_node) == len(self.processor_table):
                Z_min = 0
                # Z_next_node.pop()
                # t_node.pop()
                for i in range(node_index + 1, len(c_p)):
                    Z_min += self.processor_table[0][c_p[i].id - 1]
                Z_next_node.append(Z_min)
                t_node += [reserve - Z_min]

            C_node = []
            for i in range(0, len(t_node)):
                index = self.find_index(t_node[i], c_p[node_index].id - 1)
                C_node.append(self.criteria_func(self.processor_table[index][c_p[node_index].id-1]))
                # C_node.append(self.criteria_func(c_p[node_index].id - 1, t_node[i]))

            # recursion
            CF_next_node = []
            previous_layers = []
            for z in Z_next_node:
                previous_layer = self.next_layer_calc(z, c_p, node_index+1)
                if not previous_layer:
                    continue
                else:
                    CF_next_node.append(previous_layer.CF_layer)
                    previous_layers.append(previous_layer)


            CF_node = [CF_next_node[i] + C_node[i] for i in range(len(CF_next_node))]

            # min_value = min(CF_node)
            if not CF_node:
                return []
            min_value = max(CF_node)
            indices = [index for index, value in enumerate(CF_node) if value == min_value]

            options = []
            new_previous_layers = []
            for index in indices:
                options.append([C_node[index], t_node[index],
                    Z_next_node[index]])
                new_previous_layers.append(previous_layers[index])

            current_layer = Layer(c_p[node_index].id, min_value, options, new_previous_layers)

            return current_layer

    def criteria_func(self, perform_time):
        J = 6
        L = self.T
        return round(perform_time / (J * L), 4)

    def find_index(self, z, node_index):
        lo = 0
        hi = len(self.processor_table)
        while lo < hi:
            mid = (lo + hi) // 2
            if z < self.processor_table[mid][node_index]:
                hi = mid
            else:
                lo = mid + 1
        return lo-1

    # for test0_6.xml
    # def criteria_func(self, task_index, perform_time):
    #     if task_index == 0 or task_index == 3 or task_index == 5:
    #         float = 20/perform_time
    #         return math.ceil(20/perform_time)
    #     if task_index == 1:
    #         return math.ceil(30/perform_time)
    #     if task_index == 2 or task_index == 4:
    #         return math.ceil(10/perform_time)

    def set_node_times(self, c_p, local_c_p, layer):
        node = local_c_p[0]
        index = c_p.index(node)
        if index == 0:
            node.start_time = self.global_timer
            # TODO: fix layer.options[][] --> layer.options[]
            node.finish_time = self.round_up(node.start_time + layer.options[0][1], 2)
        else:
            previous_node = c_p[index-1]
            node.start_time = previous_node.finish_time
            # TODO: fix layer.options[][] --> layer.options[]
            node.finish_time = self.round_up(node.start_time + layer.options[0][1], 2)

        if layer.previous_layers:
            # TODO: fix layer.previous_layers[0].node_id --> layer.previous_layers.node_id
            self.set_next_node_times(node, self.nodes[layer.previous_layers[0].node_id], layer.previous_layers[0])

    def set_next_node_times(self, previous_node, current_node, layer):
        current_node.start_time = previous_node.finish_time
        # TODO: fix layer.options[][] --> layer.options[]
        current_node.finish_time = self.round_up(current_node.start_time + layer.options[0][1], 2)

        if layer.previous_layers:
            # TODO: fix layer.previous_layers[0].node_id --> layer.previous_layers.node_id
            self.set_next_node_times(current_node, self.nodes[layer.previous_layers[0].node_id], layer.previous_layers[0])


