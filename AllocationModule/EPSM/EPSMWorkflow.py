import csv
import random
import sys
from collections import deque

from networkx.algorithms.shortest_paths.generic import shortest_path
# from urllib3.util import current_time

from SchedulingModule.CJM.Model.Criteria import AverageResourceLoadCriteria, TimeCriteria, CostCriteria
from SchedulingModule.CJM.Model.Edge import Edge
from SchedulingModule.CJM.Model.File import File
from SchedulingModule.CJM.Model.LayerOption import LayerOption
from SchedulingModule.CJM.Model.Node import Node
from SchedulingModule.CJM.Model.Layer import Layer
from config import DATA_TRANSFER_CHANNEL_SPEED
from Utils.XMLParser import XMLParser
from SchedulingModule.CJM.Model.Strategy import Strategy
import config

import math
import copy


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def dfs(node):
    if node.id == 40 or node.id == 41:
        y = 0
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



class EPSMWorkflow:

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
        self.cp_paths_by_vm_type = []
        self.strategies = []
        self.best_strategy = None
        self.vm_types = vm_types
        self.vms_table = []
        self.vms_cost = []
        self.task_volume_multiplier = task_volume_multiplier
        self.data_volume_multiplier = data_volume_multiplier
        self.criteria = criteria
        self.T = T
        self.t = T
        self.global_timer = start_time
        self.xml_file = XML_FILE
        self.preliminary_total_cost = 0
        self.major_vm_type_index = None

        # Steps
        soup_nodes, soup_edges = XMLParser.parse(XML_FILE)
        self.create_graph(soup_nodes, soup_edges)
        self.create_vms_table(vm_types)
        self.find_all_critical_paths()
        self.check_duplicate_critical_paths()
        self.find_cp_paths_by_vm_type()

        if self.t == 1:
            self.T = self.cp_paths_by_vm_type[0]
        elif self.t == 2:
            self.T = self.cp_paths_by_vm_type[-1]
        elif self.t == 3:
            self.T = round_up((self.cp_paths_by_vm_type[2] + self.cp_paths_by_vm_type[3]) / 2)
            # self.T = round_up((self.cp_paths_by_vm_type[1] + self.cp_paths_by_vm_type[2]) / 2)
            # self.T = self.cp_paths_by_vm_type[3]
        elif self.t == 4:
            self.T = random.randint(self.cp_paths_by_vm_type[0], self.cp_paths_by_vm_type[-1])
        else:
            self.T = self.t

        self.criteria.set_parameters(len(self.vms_table), self.T)

        self.check_global_deadline()
        self.add_extra_time()


    def create_graph(self, soup_nodes, soup_edges):
        # Add entry_node into graph
        # ?TODO: try to eliminate entry node ?
        self.add_node(Node('entry', 0.0, 0.0))

        for node in soup_nodes:
            name = node.get('id')
            if round_up(float(node.get('runtime')) * self.task_volume_multiplier) < self.vm_types[0].perf:
                volume = self.vm_types[0].perf
            else:
                volume = round_up(float(node.get('runtime')) * self.task_volume_multiplier)
            # volume = round_up(float(node.get('runtime')) * self.task_volume_multiplier)
            current_node = Node(name, volume, round_up(volume / self.vm_types[0].perf))
            self.add_node(current_node)

            if current_node.id == 42:
                y = 0
            uses = node.find_all('uses')
            for use in uses:
                # TODO:
                if use.get('register') != 'true':
                    xml_size = float(use.get('size'))
                    size = round_up(float(use.get('size')) * self.data_volume_multiplier / 1000000)
                    if size < self.vm_types[0].perf:
                        size = self.vm_types[0].perf
                    else:
                        size = round_up(float(use.get('size')) * self.data_volume_multiplier / 1000000)
                    current_node.add_file(File(use.get('file'),
                                               use.get('link'),
                                               size,
                                               use.get('register')))
                else:
                    xml_size = float(use.get('size'))
                    size = round_up(float(use.get('size')) * self.data_volume_multiplier / 1000000)
                    current_node.add_file(File(use.get('file'),
                                               use.get('link'),
                                               size,
                                               use.get('register')))
            current_node.calculate_transfer_time(self.vm_types[0].perf, DATA_TRANSFER_CHANNEL_SPEED)

        # Add finish_node into graph
        self.add_node(Node('finish', 0.0, 0.0))
        self.nodes[-1].critical_paths.append([0, [self.nodes[-1]]])

        self.set_starting_values()

        for edge in soup_edges:  # edge = child and all his parent
            parents = edge.find_all('parent')
            for parent in parents:
                node_from = self.node_dict.get(parent.get('ref'))
                node_to = self.node_dict.get(edge.get('ref'))
                e = Edge(node_from, node_to, node_from.output, self.vm_types[0].perf, DATA_TRANSFER_CHANNEL_SPEED)
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
                if next_node.input:
                    edge = Edge(entry_node, next_node, next_node.input, self.vm_types[0].perf, DATA_TRANSFER_CHANNEL_SPEED)
                else:
                    edge = Edge(entry_node, next_node, [File('empty_file', 'input', 0, 'false')], self.vm_types[0].perf, DATA_TRANSFER_CHANNEL_SPEED)
                self.add_edge(edge)
                entry_node.add_edge_to(edge)
                next_node.add_edge_from(edge)

        finish_node = self.nodes[-1]
        for i in range(1, n - 1):
            previous_node = self.nodes[i]
            if self.finish_edges[i] == 0:
                edge = Edge(previous_node, finish_node, previous_node.output, self.vm_types[0].perf, DATA_TRANSFER_CHANNEL_SPEED)
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


    def find_cp_paths_by_vm_type(self):
        c_p = self.critical_paths[0][1]

        for vm_type in self.vm_types:
            path = 0
            for elem in c_p:
                if isinstance(elem, Node):
                    path += round_up(elem.volume / vm_type.perf)
                else:
                    # path += elem.transfer_size / vm_type.perf
                    # path += elem.transfer_size
                    path += round_up(elem.transfer_size / DATA_TRANSFER_CHANNEL_SPEED)

            self.cp_paths_by_vm_type.append(path)
            print("path on " + str(vm_type.type) + " = " + str(path))


    def create_vms_table(self, vm_types):
        for i in vm_types:
            vms_value = []
            for j in range(1, len(self.nodes) - 1):
                vms_value.append(round_up(self.nodes[j].volume / i.perf))
            self.vms_table.append(vms_value)
            self.vms_cost.append(i.cost)






    def calc_node_weights(self):
        critical_paths = self.critical_paths
        total_duration = critical_paths[0][0]
        for cp_pair in critical_paths:
            c_p = cp_pair[1]
            del c_p[-1]  # delete finish node
            del c_p[0]  # delete entry node

            reserve = total_duration
            # reserve = cp_pair[0]
            for i in range(len(c_p) - 1, -1, -2):  # delete edges(transfer time)
                # reserve -= round_up(c_p[i].transfer_size / self.vm_types[self.major_vm_type_index].perf)
                # reserve -= round_up(c_p[i].transfer_size)
                reserve -= round_up(c_p[i].transfer_size / DATA_TRANSFER_CHANNEL_SPEED)
                del c_p[i]

            # for i, node in enumerate(c_p):
            #     if node.weight is not None:
            #         del c_p[i]

            for node in c_p:
                if node.weight is not None:
                    continue
                else:
                    node.weight = round(node.runtime / reserve, 2)


    def hare_quota(self, extra_time):
        critical_paths = self.critical_paths
        for cp_pair in critical_paths:
            quotas = {}
            remainders = {}
            already_calculated_extra_time = 0
            c_p = cp_pair[1]
            for i, node in enumerate(c_p):
                if node.extra_time is not None:
                    already_calculated_extra_time += node.extra_time
                    quotas[i] = 0  # Целая часть
                    remainders[i] = 0 # Дробная часть
                else:
                    exact_quota = round(node.weight * extra_time, 2)
                    quotas[i] = int(exact_quota)  # Целая часть
                    remainders[i] = round(exact_quota - quotas[i], 2) # Дробная часть

            distributed_sum = sum(quotas.values())
            leftover = int(extra_time - already_calculated_extra_time - distributed_sum)

            sorted_tasks = sorted(remainders.keys(), key=lambda x: remainders[x], reverse=True)

            for i in range(leftover):
                task = sorted_tasks[i]
                quotas[task] += 1

            for i, node in enumerate(c_p):
                if node.extra_time is not None:
                    continue
                else:
                    node.extra_time = quotas[i]


    def calc_extra_time_by_weights(self, total_extra_time):
        critical_paths = self.critical_paths
        for cp_pair in critical_paths:
            c_p = cp_pair[1]
            sum = 0
            min_weight = sys.maxsize
            node_min_weight_index = -1
            for i, node in enumerate(c_p):
                if node.extra_time is None:
                    node_extra_time = round(node.weight * total_extra_time, 0)
                    node.extra_time = node_extra_time
                    if node.weight < min_weight:
                        node_min_weight_index = i
                sum += node.extra_time
            if sum > total_extra_time:
                sub = sum - total_extra_time
                c_p[node_min_weight_index].extra_time -= sub



        # for node in self.nodes:
        #     if node.name != 'entry' and node.name != 'finish':
        #         a = round(node.weight * extra_time, 0)
        #         node.extra_time = round(node.weight * extra_time, 0)

    def check_global_deadline_with_extra_tim(self):
        vm_type_index = self.find_vm_type(self.T)
        if vm_type_index == -1:
            print("Deadline is too small")
            return
        self.major_vm_type_index = vm_type_index

        for node in self.nodes:
            node.visited = False

        queue = deque([])
        entry_node = self.nodes[0]
        entry_node.start_time = self.global_timer
        entry_node.finish_time = entry_node.start_time + round_up(entry_node.volume / self.vm_types[vm_type_index].perf)
        entry_node.visited = True

        for edge in entry_node.edges_to:
            queue.append(edge.node_to)

        while queue:
            current_node = queue.popleft()
            if current_node.id == 37:
                y = 0

            # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / self.vm_types[vm_type_index].perf))
            # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size))
            max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED))
            # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / self.vm_types[vm_type_index].perf)
            # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size)
            current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED)


            try:
                current_node.finish_time = current_node.start_time + current_node.extra_time + round_up(current_node.volume / self.vm_types[vm_type_index].perf)
            except:
                current_node.finish_time = current_node.start_time + round_up(current_node.volume / self.vm_types[vm_type_index].perf)

            for edge in current_node.edges_to:
                child_node = edge.node_to
                if not child_node.visited:
                    # child_node.visited = True
                    queue.append(child_node)

        if not (self.nodes[-1].finish_time <= self.T):
            y = 0
        print(self.nodes[-1].finish_time <= self.T)
        print("real_path = " + str(self.nodes[-1].finish_time))


    def add_extra_time(self):
        self.calc_node_weights()
        extra_time = self.T - self.cp_paths_by_vm_type[self.major_vm_type_index]
        # self.hare_quota(extra_time)
        self.calc_extra_time_by_weights(extra_time)
        self.check_global_deadline_with_extra_time()


    def find_vm_type(self, deadline):
        for i, path in enumerate(self.cp_paths_by_vm_type):
            if path > deadline:
                return i-1
            elif path == deadline:
                return i

        return len(self.cp_paths_by_vm_type) - 1


    def check_global_deadline(self):
        vm_type_index = self.find_vm_type(self.T)
        if vm_type_index == -1:
            print("Deadline is too small")
            return
        self.major_vm_type_index = vm_type_index

        for node in self.nodes:
            node.visited = False

        queue = deque([])
        entry_node = self.nodes[0]
        entry_node.start_time = self.global_timer
        entry_node.finish_time = entry_node.start_time + round_up(entry_node.volume / self.vm_types[vm_type_index].perf)
        entry_node.visited = True

        for edge in entry_node.edges_to:
            child_node = edge.node_to
            if not child_node.visited:
                # child_node.visited = True
                queue.append(child_node)

        while queue:
            current_node = queue.popleft()
            if current_node.id == 38:
                y = 0
            parent_flag = True

            for edge in current_node.edges_from:
                parent_node = edge.node_from
                if not parent_node.visited:
                    parent_flag = False
                    break

            if parent_flag:
                # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / self.vm_types[vm_type_index].perf))
                # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size))
                max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED))
                # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / self.vm_types[vm_type_index].perf)
                # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size)
                current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED)

                current_node.finish_time = current_node.start_time + round_up(current_node.volume / self.vm_types[vm_type_index].perf)
                current_node.visited = True

                for edge in current_node.edges_to:
                    child_node = edge.node_to
                    if not child_node.visited:
                        queue.append(child_node)

        print(self.nodes[-1].finish_time <= self.T)
        print("real_path = " + str(self.nodes[-1].finish_time))

    def check_global_deadline_with_extra_time(self):
        vm_type_index = self.find_vm_type(self.T)
        if vm_type_index == -1:
            print("Deadline is too small")
            return
        self.major_vm_type_index = vm_type_index

        for node in self.nodes:
            node.visited = False

        queue = deque([])
        entry_node = self.nodes[0]
        entry_node.start_time = self.global_timer
        entry_node.finish_time = entry_node.start_time + round_up(entry_node.volume / self.vm_types[vm_type_index].perf)
        entry_node.visited = True

        for edge in entry_node.edges_to:
            child_node = edge.node_to
            if not child_node.visited:
                # child_node.visited = True
                queue.append(child_node)

        while queue:
            current_node = queue.popleft()
            if current_node.id == 38:
                y = 0
            parent_flag = True

            for edge in current_node.edges_from:
                parent_node = edge.node_from
                if not parent_node.visited:
                    parent_flag = False
                    break

            if parent_flag:
                # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / self.vm_types[vm_type_index].perf))
                # max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size))
                max_edge = max(current_node.edges_from, key=lambda edge: edge.node_from.finish_time + round_up(edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED))
                # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / self.vm_types[vm_type_index].perf)
                # current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size)
                current_node.start_time = max_edge.node_from.finish_time + round_up(max_edge.transfer_size / DATA_TRANSFER_CHANNEL_SPEED)

                # current_node.finish_time = current_node.start_time + round_up(current_node.volume / self.vm_types[vm_type_index].perf)
                try:
                    current_node.finish_time = current_node.start_time + current_node.extra_time + round_up(
                        current_node.volume / self.vm_types[vm_type_index].perf)
                except:
                    current_node.finish_time = current_node.start_time + round_up(
                        current_node.volume / self.vm_types[vm_type_index].perf)

                current_node.visited = True

                for edge in current_node.edges_to:
                    child_node = edge.node_to
                    if not child_node.visited:
                        queue.append(child_node)

        print(self.nodes[-1].finish_time <= self.T)
        print("real_path = " + str(self.nodes[-1].finish_time))