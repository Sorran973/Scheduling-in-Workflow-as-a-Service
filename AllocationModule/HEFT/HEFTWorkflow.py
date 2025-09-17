import random
import sys

from AllocationModule.HEFT.HEFTNode import HEFTNode
from AllocationModule.HEFT.HEFTVM import HEFTVM
from AllocationModule.Model.VM import VM
from SchedulingModule.CJM.Model.Criteria import AverageResourceLoadCriteria, TimeCriteria, CostCriteria
from SchedulingModule.CJM.Model.Edge import Edge
from SchedulingModule.CJM.Model.File import File
from SchedulingModule.CJM.Model.LayerOption import LayerOption
from SchedulingModule.CJM.Model.Layer import Layer
from Utils.Configuration import DATA_TRANSFER_CHANNEL_SPEED
from Utils.XMLParser import XMLParser
from SchedulingModule.CJM.Model.Strategy import Strategy
import Utils.Configuration

import math
import copy


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def dfs(node, first_id):
    node.visited = True
    w = 0
    if node.name is 'entry':
        a = 1
    elif node.name is 'finish':
        a = 1
    else:
        w = sum(node.exec_times_by_vm) / len(node.exec_times_by_vm)


    node_edges = node.edges_to

    child_rank_max = 0
    for node_edge in node_edges:
        node_child = node_edge.node_to
        if not node_child.visited:
            dfs(node_child, first_id)

        if node_child.rank + node_edge.transfer_size >= child_rank_max:
            child_rank_max = node_child.rank + node_edge.transfer_size

    node.rank = w + child_rank_max


class HEFTWorkflow:

    def __init__(self, XML_FILE, T, vm_types, vms, criteria,
                 task_volume_multiplier, data_volume_multiplier, start_time=0):
        self.global_timer = start_time
        self.nodes = []
        self.sorted_nodes_by_rank = []
        self.first_id: int
        self.node_dict = {}  # [str(node_name) : obj(node)]
        self.edges = []
        self.entry_edges: [int]  # for setting edges between entry_node and his children
        self.finish_edges = None  # -//- finish_node and his children
        self.drawn_nodes = []
        self.drawn_edges = []
        self.vm_types = vm_types
        self.vms = []
        self.vms_table = []
        self.vms_cost = []
        self.task_volume_multiplier = task_volume_multiplier
        self.data_volume_multiplier = data_volume_multiplier
        self.criteria = criteria
        self.T = T
        self.global_timer = start_time
        self.xml_file = XML_FILE

        # Steps
        soup_nodes, soup_edges = XMLParser.parse(XML_FILE)
        self.create_graph(soup_nodes, soup_edges)
        self.create_vms_table(vms)
        self.task_prioritizing_phase()
        # self.processor_selection_phase()


        # if self.T is None:
            # self.T = random.randint(self.critical_paths[0][0], self.longest_path)

        # self.criteria.set_parameters(len(self.vms_table), self.T)

    def create_graph(self, soup_nodes, soup_edges):
        # Add entry_node into graph
        # ?TODO: try to eliminate entry node ?
        self.add_node(HEFTNode('entry', 0.0, 0.0))

        for node in soup_nodes:
            name = node.get('id')
            if round_up(float(node.get('runtime')) * self.task_volume_multiplier) < 5:
                volume = 5
            else:
                volume = round_up(float(node.get('runtime')) * self.task_volume_multiplier)
            # volume = round_up(float(node.get('runtime')) * self.task_volume_multiplier)
            current_node = HEFTNode(name, volume, round_up(volume / self.vm_types[0].perf))
            self.add_node(current_node)

            uses = node.find_all('uses')
            for use in uses:
                # TODO:
                if use.get('register') != 'true':
                # if use.get('link') != 'input':
                    current_node.add_file(File(use.get('file'),
                                               use.get('link'),
                                               round_up(float(use.get('size')) * self.data_volume_multiplier / 1000000),
                                               use.get('register')))
            current_node.calculate_transfer_time(DATA_TRANSFER_CHANNEL_SPEED)

        # Add finish_node into graph
        self.add_node(HEFTNode('finish', 0.0, 0.0))
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

    def complete_graph(self):  # add entry and finish edges
        n = len(self.nodes)
        entry_node = self.nodes[0]
        for i in range(1, n - 1):
            next_node = self.nodes[i]
            if self.entry_edges[i] == 0:
                if next_node.input:
                    edge = Edge(entry_node, next_node, next_node.input, DATA_TRANSFER_CHANNEL_SPEED)
                else:
                    edge = Edge(entry_node, next_node, [File('empty_file', 'input', 0, 'false')], DATA_TRANSFER_CHANNEL_SPEED)
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

    def set_workflow_id(self, workflow_id):
        for node in self.sorted_nodes_by_rank:
            node.workflow_id = workflow_id

    def create_vms_table(self, vms):
        for vm in vms:
            for j in range(1, len(self.nodes) - 1):
                exec_time = round_up(self.nodes[j].volume / vm.perf)
                self.nodes[j].exec_times_by_vm.append(exec_time)


    def task_prioritizing_phase(self):
        for node in self.nodes:
            if not node.visited:
                dfs(node, self.first_id)

        self.sorted_nodes_by_rank = sorted(self.nodes, key=lambda node: node.rank, reverse=True)
        self.sorted_nodes_by_rank[0].eft = self.global_timer
        del self.sorted_nodes_by_rank[-1]  # delete finish node
        del self.sorted_nodes_by_rank[0]  # delete entry node
        for node in self.sorted_nodes_by_rank:
            node.rank -= self.global_timer