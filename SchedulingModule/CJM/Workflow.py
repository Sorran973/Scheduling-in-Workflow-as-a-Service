from SchedulingModule.CJM.Model.Criteria import AverageResourceLoadCriteria, TimeCriteria, CostCriteria
from SchedulingModule.CJM.Model.Edge import Edge
from SchedulingModule.CJM.Model.File import File
from SchedulingModule.CJM.Model.LayerOption import LayerOption
from SchedulingModule.CJM.Model.Node import Node
from SchedulingModule.CJM.Model.Layer import Layer
from Utils.Configuration import DATA_TRANSFER_CHANNEL_SPEED, MULTIPLE_STRATEGIES
from Utils.XMLParser import XMLParser
from SchedulingModule.CJM.Model.Strategy import Strategy

import math
import copy


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def dfs(node):
    node.visited = True
    node_edges = node.edges_to

    for node_edge in node_edges:
        node_child = node_edge.node_to
        if not node_child.visited:
            dfs(node_child)

        for critical_path in node_child.critical_paths:
            node.critical_paths.append((round(node.runtime + node_edge.transfer_time + critical_path[0], 2),
                                        [node, node_edge] + critical_path[1]))


def sort_for_critical_paths(critical_path):
    return critical_path[0]


def mark_whole_path(path):
    for elem in path[1]:
        elem.in_critical_path = True


def common_member(list_a, list_b, first_id):
    result = []
    for node in list_b:
        if list_a[node.id - first_id] != -math.inf:
            result.append(node)

    return result


class Workflow:

    def __init__(self, XML_FILE, T, vm_types, criteria,
                 task_volume_multiplier, data_volume_multiplier, start_time=0):
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
        self.best_strategy = None
        self.vm_types = vm_types
        self.vms_table = []
        self.vms_cost = []
        self.volume_multiplier = task_volume_multiplier
        self.data_volume_multiplier = data_volume_multiplier
        self.criteria = criteria
        self.T = T
        self.global_timer = start_time

        # Steps
        soup_nodes, soup_edges = XMLParser.parse(XML_FILE)
        self.create_graph(soup_nodes, soup_edges)
        self.create_vms_table(vm_types)
        self.find_all_critical_paths()
        self.check_duplicate_critical_paths()

        if self.T is None:
            self.T = self.critical_paths[0][0]
        self.criteria.set_parameters(len(self.vms_table), self.T)

    def create_graph(self, soup_nodes, soup_edges):
        # Add entry_node into graph
        # ?TODO: try to eliminate entry node ?
        self.add_node(Node('entry', 0.0, 0.0))

        for node in soup_nodes:
            name = node.get('id')
            volume = round(float(node.get('runtime')) * self.volume_multiplier)
            current_node = Node(name, volume, round_up(volume / self.vm_types[0].perf))
            self.add_node(current_node)

            if current_node.id == 49:
                y = 0
            uses = node.find_all('uses')
            for use in uses:
                current_node.add_file(File(use.get('file'),
                                           use.get('link'),
                                           round_up(float(use.get('size')) * self.data_volume_multiplier / 1000000),
                                           use.get('register')))
            current_node.calculate_transfer_time(DATA_TRANSFER_CHANNEL_SPEED)

        # Add finish_node into graph
        self.add_node(Node('finish', 0.0, 0.0))
        self.nodes[-1].critical_paths.append([0, [self.nodes[-1]]])

        self.set_starting_values()

        for edge in soup_edges:  # edge = child and all his parent
            parents = edge.find_all('parent')
            for parent in parents:
                node_from = self.node_dict.get(parent.get('ref'))
                node_to = self.node_dict.get(edge.get('ref'))
                e = Edge(node_from, node_to, node_from.output, DATA_TRANSFER_CHANNEL_SPEED)
                self.add_edge(e)
                node_from.add_edge_to(e)
                node_to.add_edge_from(e)


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

        self.entry_edges[edge.node_to.id - self.first_id] = 1
        self.finish_edges[edge.node_from.id - self.first_id] = 1

    def find_all_critical_paths(self):
        for node in self.nodes:
            if not node.visited:
                dfs(node)

        # sorting of all critical paths based on process time (length) in descending order
        self.nodes[0].critical_paths.sort(key=sort_for_critical_paths, reverse=True)

        # set T based on the critical path
        # self.T = round_up(self.nodes[0].critical_paths[0][0])
        c_p = self.nodes[0].critical_paths[0][1]
        for i in range(0, len(c_p), 2):  # without edges
            c_p[i].color = 'red'

    def complete_graph(self):  # add entry and finish edges
        n = len(self.nodes)
        entry_node = self.nodes[0]
        for i in range(1, n - 1):
            next_node = self.nodes[i]
            if self.entry_edges[i] == 0:
                edge = Edge(entry_node, next_node, next_node.input, DATA_TRANSFER_CHANNEL_SPEED)
                self.add_edge(edge)
                entry_node.add_edge_to(edge)
                next_node.add_edge_from(edge)

        finish_node = self.nodes[-1]
        for i in range(1, n - 1):
            previous_node = self.nodes[i]
            if self.finish_edges[i] == 0:
                edge = Edge(previous_node, finish_node, previous_node.output, DATA_TRANSFER_CHANNEL_SPEED)
                self.add_edge(edge)
                previous_node.add_edge_to(edge)
                finish_node.add_edge_from(edge)


    def check_duplicate_critical_paths(self):
        critical_paths = self.nodes[0].critical_paths
        for c_p in critical_paths:
            for elem in c_p[1]:
                if not elem.in_critical_path:
                    self.critical_paths.append(c_p)
                    mark_whole_path(c_p)


    def create_vms_table(self, vm_types):
        for i in vm_types:
            vms_value = []
            for j in range(1, len(self.nodes) - 1):
                vms_value.append(round_up(self.nodes[j].volume / i.perf))
            self.vms_table.append(vms_value)
            self.vms_cost.append(i.cost)


    def calc_c_node(self, index, c_p, node_index):
        if isinstance(self.criteria, AverageResourceLoadCriteria):
            return self.criteria.main_criteria(self.vms_table[index][c_p[node_index].id - self.first_id - 1])
        elif isinstance(self.criteria, TimeCriteria):
            return self.criteria.main_criteria(self.vms_table[index][c_p[node_index].id - self.first_id - 1])
        elif isinstance(self.criteria, CostCriteria):
            return self.criteria.main_criteria([self.vms_table[index][c_p[node_index].id - self.first_id - 1],
                                                  self.vms_cost[index]])


    def schedule(self):

        for critical_path in self.critical_paths:
            self.local_strategies = []
            layer = Layer()
            c_p = critical_path[1]
            del c_p[-1]  # delete finish node and edge
            del c_p[0]  # delete entry node and edge

            Z1 = self.T # Z1 = reserve time
            for i in range(len(c_p) - 1, -1, -2):  # delete edges(transfer time)
                Z1 -= c_p[i].transfer_time
                del c_p[i]

            if not self.strategies:
                layer = self.next_layer_calc(Z1, c_p, 0)  # direct pass
                # self.strategies = self.create_strategies_recursion(layer)
                strategy = Strategy(len(self.nodes), self.T)
                self.strategies.append(strategy)
                self.set_strategy_times(c_p, c_p, layer)  # reverse pass
            else:
                for strategy in self.strategies:
                    local_c_p = copy.copy(c_p)
                    local_Z1 = Z1
                    common_nodes = common_member(strategy.time, c_p, self.first_id)

                    if common_nodes:
                        for node in common_nodes:
                            local_Z1 -= strategy.time[node.id - self.first_id]
                            local_c_p.remove(node)

                    if local_Z1 < 0:
                        break

                    if local_c_p:  # if not all nodes are already calculated
                        layer = self.next_layer_calc(local_Z1, local_c_p, 0)  # direct pass
                        # new_strategies = self.create_strategies_recursion(layer, strategy)
                        self.set_strategy_times(c_p, local_c_p, layer)  # reverse pass

                    # self.local_strategies.extend(new_strategies)

                if self.local_strategies:
                    self.strategies = self.local_strategies
                    self.local_strategies = []

        res = []
        for strategy in self.strategies:
            del strategy.time[0]
            del strategy.time[-1]
            del strategy.criteria[0]
            del strategy.criteria[-1]

            res.append(sum(strategy.criteria))

        best_res = self.criteria.cf_criteria(res)
        index = res.index(best_res)
        self.best_strategy = self.strategies[index]

        # self.set_node_times(self.best_strategy.dict)
        self.nodes[0].start_time = 0
        self.nodes[0].finish_time = 0
        self.nodes[-1].start_time = self.T
        self.nodes[-1].finish_time = self.T
        print()

    def set_strategy_times(self, c_p, local_c_p, layer):
        node = local_c_p[0]
        index = c_p.index(node)
        strategy = self.strategies[0]
        if index == 0:
            # node.start_time = float(self.global_timer + node.input_time)
            node.start_time = float(self.global_timer)
            # node.finish_time = round(node.start_time + node.output_time + round_up(layer.layer_options[0].t_current_node), 2)
            node.finish_time = round(node.start_time + node.input_time + round_up(layer.layer_options[0].t_current_node), 2)

            strategy.change(node.id,
                                layer.layer_options[0].t_current_node,
                                layer.layer_options[0].C_current_node)
        else:
            previous_node = c_p[index - 1]
            node.start_time = previous_node.finish_time
            node.finish_time = round(node.start_time + previous_node.output_time +
                                     round_up(layer.layer_options[0].t_current_node), 2)

            strategy.change(node.id,
                                layer.layer_options[0].t_current_node,
                                layer.layer_options[0].C_current_node)

        if layer.previous_layers:
            self.set_next_node_strategy_times(node,
                                              self.nodes[layer.previous_layers[0].node.id - self.first_id],
                                              layer.previous_layers[0])


    def set_next_node_strategy_times(self, previous_node, current_node, layer):
        strategy = self.strategies[0]
        current_node.start_time = previous_node.finish_time
        current_node.finish_time = round(current_node.start_time + previous_node.output_time +
                                         round_up(layer.layer_options[0].t_current_node), 2)

        strategy.change(current_node.id,
                        layer.layer_options[0].t_current_node,
                        layer.layer_options[0].C_current_node)

        if layer.previous_layers:
            self.set_next_node_strategy_times(current_node, self.nodes[layer.previous_layers[0].node.id - self.first_id],
                                     layer.previous_layers[0])

    def create_strategies_recursion(self, layer, strategy=None, previous_node=None):
        if layer.previous_layers is None:
            if strategy is None:
                new_strategy = Strategy(len(self.nodes), self.T)
            else:
                new_strategy = Strategy(len(self.nodes), self.T, strategy)

            current_node = layer.node
            if current_node.name == "p13":
                y = 0
            possible_time_for_perform = new_strategy.change(current_node.id,
                            layer.layer_options[0].t_current_node,
                            layer.layer_options[0].C_current_node) # (perform time) + (time left from reserve)

            dest_times = []
            transfer_times = []
            #TODO: make up with something to handle input_time
            for edge in current_node.edges_from:
                if edge.node_from.id == previous_node.id:
                    transfer_times.append(edge.transfer_time)
            input_time = max(transfer_times)

            for edge in current_node.edges_to:
                if edge.node_to.id in new_strategy.dict:
                    if edge.node_to.id == self.nodes[-1].id:
                        dest_start_time = new_strategy.dict[edge.node_to.id][0] - current_node.output_time
                    else:
                        dest_start_time = new_strategy.dict[edge.node_to.id][0]
                    dest_times.append(dest_start_time)
            dest_start_time = max(dest_times)

            # start_time = round(dest_start_time - current_node.output_time - possible_time_for_perform - input_time, 2)
            start_time = round(dest_start_time - possible_time_for_perform - input_time, 2)
            # finish_time = dest_start_time - current_node.output_time
            finish_time = dest_start_time
            new_strategy.dict[layer.node.id] = [start_time, finish_time]

            return [new_strategy]
        else:
            new_strategies = []
            for i, l in enumerate(layer.previous_layers):
                strategies = self.create_strategies_recursion(l, strategy, layer.node)
                for new_strategy in strategies:
                    perform_time = new_strategy.change(layer.node.id,
                                    layer.layer_options[i].t_current_node,
                                    layer.layer_options[i].C_current_node)

                    current_node = layer.node
                    transfer_times = []
                    for edge in current_node.edges_from:
                        if edge.node_from.id == self.nodes[0].id:
                            transfer_times.append(edge.transfer_time)
                    input_time = max(transfer_times)

                    dest_time = new_strategy.dict[l.node.id][0]
                    start_time = round(dest_time - perform_time - input_time, 2)
                    # start_time = round(dest_time - current_node.output_time - perform_time - input_time, 2)
                    finish_time = new_strategy.dict[l.node.id][0]
                    # finish_time = new_strategy.dict[l.node.id][0] - current_node.output_time
                    new_strategy.dict[current_node.id] = [start_time, finish_time]

                    new_strategies.append(new_strategy)

            return new_strategies


    def next_layer_calc(self, reserve, c_p, node_index):

        if node_index == len(c_p) - 1:  # if the layer is the last one
            t_node = reserve
            index = self.find_index(t_node, c_p[node_index].id - self.first_id - 1)
            C_node = self.calc_c_node(index, c_p, node_index)
            CF_node = C_node

            return Layer(c_p[node_index], CF_node, [LayerOption(t_node, None, None, C_node, CF_node)], None)

        else:
            Z_next_node = []
            Z_min = 0
            for i in range(len(self.vms_table)):
                z = reserve - self.vms_table[i][c_p[node_index].id - self.first_id - 1]
                Z_min = 0
                # rest reserve on the fastest vms
                for j in range(node_index + 1, len(c_p)):
                    Z_min += self.vms_table[0][c_p[j].id - self.first_id - 1]
                if z >= Z_min:
                    Z_next_node.append(z)
                else:
                    break

            if not Z_next_node:
                return

            t_node = [self.vms_table[i][c_p[node_index].id - self.first_id - 1] for i in range(0, len(Z_next_node))]

            # add Z on the fastest vms
            if Z_next_node[-1] > Z_min:
                Z_next_node.append(Z_min)
                t_node += [reserve - Z_min]

            C_node = []
            for i in range(0, len(t_node)):
                index = self.find_index(t_node[i], c_p[node_index].id - self.first_id - 1)
                c_node = self.calc_c_node(index, c_p, node_index)
                C_node.append(c_node)

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

            CF_node = [round(CF_next_node[i] + C_node[i], 2) for i in range(len(CF_next_node))]

            if not CF_node:
                return
            CF_of_layer = self.criteria.cf_criteria(CF_node)

            if MULTIPLE_STRATEGIES:
                indices = [i for i, x in enumerate(CF_node) if x == CF_of_layer]
            else:
                indices = [CF_node.index(CF_of_layer)]

            layerOptions = []
            new_previous_layers = []
            for i in indices:
                layerOptions.append(LayerOption(t_node[i], Z_next_node[i], CF_next_node[i], C_node[i], CF_of_layer))
                new_previous_layers.append(previous_layers[i])

            return Layer(c_p[node_index], CF_of_layer, layerOptions, new_previous_layers)

    def set_node_times(self, dict_times):
        for node in self.nodes:
            node.start_time = dict_times[node.id][0]
            node.finish_time = dict_times[node.id][1]


    def find_index(self, z, node_index):
        lo = 0
        hi = len(self.vms_table)
        while lo < hi:
            mid = (lo + hi) // 2
            if z < self.vms_table[mid][node_index]:
                hi = mid
            else:
                lo = mid + 1
        return lo - 1
