from Edge import Edge
from File import File
from Node import Node
from Layer import Layer
from Parser import Parser
from Strategy import Strategy

import math
import copy


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def dfs(node):
    node.visited = True
    node_edges = node.edges

    for node_edge in node_edges:
        node_child = node_edge.destination_node
        if not node_child.visited:
            dfs(node_child)

        for critical_path in node_child.critical_paths:
            node.critical_paths.append((node.runtime + node_edge.transfer_time + critical_path[0],
                                        [node, node_edge] + critical_path[1]))


def sort_for_critical_paths(critical_path):
    return critical_path[0]


def mark_whole_path(path):
    for elem in path[1]:
        elem.in_critical_path = True


def common_member(list_a, list_b, first_id):
    result = []
    for node in list_b:
        if list_a[node.id - first_id - 1] != -math.inf:
            result.append(node)

    return result


# volume =
class Workflow:

    def __init__(self, XML_FILE, criteria, start_time=0):
        self.nodes = []
        self.first_id: int
        self.node_dict = {}  # [str(node_name) : obj(node)]
        self.edges = []
        self.entry_edges: [int]  # for setting edges between entry_node and his children
        self.finish_edges = None  # -//- finish_node and his children
        self.drawn_nodes = []
        self.drawn_edges = []
        self.critical_paths = []
        self.strategies = []
        self.num_of_processors = 5
        self.processor_table = []
        self.processor_table_performance = [3.0, 2.5, 2.0, 1.5, 1.0]
        self.T: int
        self.criteria = criteria
        self.global_timer = start_time

        # Steps
        soup_nodes, soup_edges = Parser.parse(XML_FILE)
        self.create_graph(soup_nodes, soup_edges)
        self.find_all_critical_paths()
        self.check_duplicate_critical_paths()
        self.create_processor_table()
        self.criteria.set_parameters(self.num_of_processors, self.T)
        # print(self.T)

    def create_graph(self, soup_nodes, soup_edges):
        # Add entry_node into graph
        #TODO: try to eliminate entry node
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

        self.set_starting_values()

        for edge in soup_edges:  # edge = child and all his parent
            parents = edge.find_all('parent')
            for parent in parents:
                node_from = self.node_dict.get(parent.get('ref'))
                node_to = self.node_dict.get(edge.get('ref'))
                transfer_size = node_from.output_size
                # transfer_time = 10
                self.add_edge(Edge(node_from, node_to, transfer_size))

        # Add entry and finish edges
        self.complete_graph()

    def add_node(self, node):
        self.nodes.append(node)
        self.drawn_nodes.append(node)
        self.node_dict[node.name] = node

    def set_starting_values(self):
        self.num_of_nodes = len(self.nodes)
        self.entry_edges = [0 for i in range(self.num_of_nodes)]
        self.finish_edges = [0 for i in range(self.num_of_nodes)]
        self.first_id = self.nodes[0].id


    def add_edge(self, edge):
        self.edges.append(edge)
        self.drawn_edges.append(edge)
        edge.source_node.add_edge(edge)

        self.entry_edges[edge.destination_node.id - self.first_id] = 1
        self.finish_edges[edge.source_node.id - self.first_id] = 1

    def find_all_critical_paths(self):
        for node in self.nodes:
            if not node.visited:
                dfs(node)

        # sorting of all critical paths based on process time (length) in descending order
        self.nodes[0].critical_paths.sort(key=sort_for_critical_paths, reverse=True)

        # print("All critical paths:")
        # for c_p in self.nodes[0].critical_paths:
        #     print(c_p[0], c_p[1])

        # set T based on the critical path
        self.T = round_up(self.nodes[0].critical_paths[0][0])
        # self.T = random.randint(t, t*2)
        # self.T = 78
        c_p = self.nodes[0].critical_paths[0][1]
        for i in range(0, len(c_p), 2):  # without edges
            c_p[i].color = 'red'

    def complete_graph(self):  # add entry and finish edges
        n = len(self.nodes)
        entry_node = self.nodes[0]
        for i in range(1, n - 1):
            next_node = self.nodes[i]
            if self.entry_edges[i] == 0:
                self.add_edge(Edge(entry_node, next_node, next_node.input_size))

        finish_node = self.nodes[-1]
        for i in range(1, n - 1):
            previous_node = self.nodes[i]
            if self.finish_edges[i] == 0:
                self.add_edge(Edge(previous_node, finish_node, previous_node.output_size))

    def check_duplicate_critical_paths(self):  # check duplications
        critical_paths = self.nodes[0].critical_paths
        for c_p in critical_paths:
            for elem in c_p[1]:
                if not elem.in_critical_path:
                    self.critical_paths.append(c_p)
                    mark_whole_path(c_p)

        # print("\nAll critical paths without duplications:")
        # for c_p in self.critical_paths:
        #     print(c_p[0], c_p[1])

    def create_processor_table(self):
        for i in range(0, self.num_of_processors):
            processor_value = []
            for j in range(1, len(self.nodes) - 1):
                processor_value.append(round(self.nodes[j].runtime / self.processor_table_performance[i], 2))
            self.processor_table.append(processor_value)

    def schedule(self):

        for critical_path in self.critical_paths:
            self.local_strategies = []
            layer = Layer()
            c_p = critical_path[1]
            del c_p[-1:]  # delete finish node and edge
            del c_p[0:1]  # delete entry node and edge

            Z1 = self.T
            for i in range(len(c_p) - 1, -1, -2):  # delete edges
                Z1 -= c_p[i].transfer_time
                del c_p[i]

            if not self.strategies:
                layer = self.next_layer_calc(Z1, c_p, 0)  # direct pass
                self.set_node_times(c_p, c_p, layer)  # reverse pass
            else:
                strategy = self.strategies[0]
                local_c_p = copy.copy(c_p)
                local_Z1 = Z1
                common_nodes = common_member(strategy.time, c_p, self.first_id)

                if common_nodes:
                    for node in common_nodes:
                        local_Z1 -= strategy.time[node.id - self.first_id - 1]
                        local_c_p.remove(node)

                if len(local_c_p) > 0:  # if not all nodes are already calculated
                    layer = self.next_layer_calc(local_Z1, local_c_p, 0)  # direct pass
                    self.set_node_times(c_p, local_c_p, layer)  # reverse pass

            if layer.CF_of_layer is None:  # if all nodes are already calculated
                continue

            l = len(self.nodes) - 2  # without entry and finish nodes
            time = [-math.inf] * l
            criteria = [-math.inf] * l
            self.create_strategy(Strategy(c_p, time, criteria), layer)
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
                        if strategy.time[i] != new_strategy.time[i] and strategy.time[i] != -math.inf and \
                                new_strategy.time[i] != -math.inf:
                            break
                        else:
                            continue
                else:
                    self.strategies.append(new_strategy)

            # print(self.strategies[0].time)

    def create_strategy(self, strategy, layer):
        if not layer.previous_layer:
            strategy.change(layer.node_id - self.first_id, round(layer.option[0], 2), round(layer.option[1], 2))
            self.local_strategies.append(strategy)
        else:
            strategy.change(layer.node_id - self.first_id, round(layer.option[0], 2), round(layer.option[1], 2))
            self.create_strategy(strategy, layer.previous_layer)

    def next_layer_calc(self, reserve, c_p, node_index):

        if node_index == len(c_p) - 1:  # if the layer is the last one
            t_node = reserve
            index = self.find_index(t_node, c_p[node_index].id - self.first_id - 1)
            C_node = self.criteria.main_criteria(self.processor_table[index][c_p[node_index].id - self.first_id - 1])
            CF_node = C_node

            return Layer(c_p[node_index].id, CF_node, [C_node, t_node, None, None], None)

        else:
            Z_next_node = []
            Z_min = 0
            for i in range(len(self.processor_table)):
                z = reserve - self.processor_table[i][c_p[node_index].id - self.first_id - 1]
                # rest reserve on the fastest processors
                for j in range(node_index + 1, len(c_p)):
                    Z_min += self.processor_table[0][c_p[j].id - self.first_id - 1]
                if z >= Z_min:
                    Z_next_node.append(z)
                else:
                    break

            if not Z_next_node:
                return

            t_node = [self.processor_table[i][c_p[node_index].id - self.first_id - 1] for i in range(0, len(Z_next_node))]

            # add Z on the fastest processors
            if len(Z_next_node) == len(self.processor_table):
                Z_next_node.append(Z_min)
                t_node += [reserve - Z_min]

            C_node = []
            for i in range(0, len(t_node)):
                index = self.find_index(t_node[i], c_p[node_index].id - self.first_id - 1)
                C_node.append(self.criteria.main_criteria(self.processor_table[index][c_p[node_index].id - self.first_id - 1]))

            # recursion
            CF_next_node = []
            previous_layers = []
            for z in Z_next_node:
                previous_layer = self.next_layer_calc(z, c_p, node_index + 1)
                if not previous_layer:
                    continue
                else:
                    CF_next_node.append(previous_layer.CF_of_layer)
                    previous_layers.append(previous_layer)

            CF_node = [CF_next_node[i] + C_node[i] for i in range(len(CF_next_node))]

            if not CF_node:
                return
            CF_of_layer = self.criteria.cf_criteria(CF_node)
            index = CF_node.index(CF_of_layer)
            options = [C_node[index], t_node[index], Z_next_node[index]]
            new_previous_layer = previous_layers[index]

            current_layer = Layer(c_p[node_index].id, CF_of_layer, options, new_previous_layer)

            return current_layer

    def set_node_times(self, c_p, local_c_p, layer):
        node = local_c_p[0]
        index = c_p.index(node)
        if index == 0:
            node.start_time = self.global_timer
            node.finish_time = round(node.start_time + layer.option[1], 2)
        else:
            previous_node = c_p[index - 1]
            node.start_time = previous_node.finish_time
            node.finish_time = round(node.start_time + layer.option[1], 2)

        if layer.previous_layer:
            self.set_next_node_times(node, self.nodes[layer.previous_layer.node_id - self.first_id], layer.previous_layer)

    def set_next_node_times(self, previous_node, current_node, layer):
        current_node.start_time = previous_node.finish_time
        current_node.finish_time = round(current_node.start_time + layer.option[1], 2)

        if layer.previous_layer:
            self.set_next_node_times(current_node, self.nodes[layer.previous_layer.node_id - self.first_id], layer.previous_layer)

    def find_index(self, z, node_index):
        lo = 0
        hi = len(self.processor_table)
        while lo < hi:
            mid = (lo + hi) // 2
            if z < self.processor_table[mid][node_index]:
                hi = mid
            else:
                lo = mid + 1
        return lo - 1
