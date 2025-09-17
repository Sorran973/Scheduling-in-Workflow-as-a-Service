import math
import random
import sys
from datetime import datetime

import pandas as pd
from munkres import Munkres, print_matrix, DISALLOWED, make_cost_matrix

from AllocationModule.HEFT.HEFTVM import HEFTVM
from AllocationModule.Model.PossibleAssignment import PossibleAssignment
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VM import VM
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Model.Criteria import CostCriteria, TimeCriteria
from SchedulingModule.CJM.Workflow import round_up


class HEFT:
    def __init__(self, vms, workflow_set):
        # self.vm_types = vm_types
        self.workflows = workflow_set.workflows
        self.nodes = []
        self.num_workflows = len(self.workflows)
        self.cost_of_workflow = [0 for workflow_id in range(self.num_workflows)]
        self.vms = vms
        self.log = pd.DataFrame(
            columns=['workflow_id', 'vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
                     'task_end', 'interval', 'vm_start', 'vm_input_time', 'task_allocation_start',
                     'task_allocation_end', 'vm_output_time', 'vm_end', 'allocation_cost', 'idle_time', 'vm_status'])
        self.num_workflow_deadline_met = None
        self.percentage_workflow_deadline_met = None
        self.total_cost = None
        self.total_num_leased_vm = None
        self.total_idle_time = None
        self.total_data_input_time = None
        self.total_data_output_time = None
        self.workload_time = None
        self.workload_time_without_first_and_last_vm = None
        self.sum_of_workflows_time_total = None
        self.sum_of_workflows_time_without_first_and_last_vm = None
        self.only_vm_time_total = None
        self.only_task_time_total = None

        # self.create_vms_table(vm_types)
        self.merge_worflows()
        self.processor_selection_phase()
        self.count_cost()


    # def create_vms_table(self, vm_types):
    #     for i in vm_types:
    #         self.vms.append(HEFTVM(i.type, i.perf, i.cost, i.prep_time, i.shutdown_time))


    def merge_worflows(self):
        for workflow in self.workflows:
            self.nodes.extend(workflow.sorted_nodes_by_rank)

        self.nodes.sort(key=lambda node: node.rank, reverse=True)


    def processor_selection_phase(self):
        for node in self.nodes:
            prev_nodes = []
            for edge in node.edges_from:
                prev_node = edge.node_from
                eft = prev_node.eft
                transfer_size = edge.transfer_size
                if prev_node.name is 'entry':
                    prev_nodes.append([prev_node, eft, transfer_size, eft + transfer_size])
                    continue
                else:
                    prev_nodes.append([prev_node, eft, transfer_size, eft + transfer_size])

            prev_nodes_sorted = sorted(prev_nodes, key=lambda item: item[3], reverse=True)
            max_est_arr = []
            avail_est = 0
            another_est = 0
            for i, vm in enumerate(self.vms):
                avail_est = vm.current_time
                if len(prev_nodes_sorted) == 1:
                    if prev_nodes_sorted[0][0].vm is vm:
                        another_est = prev_nodes_sorted[0][1]
                    else:
                        another_est = prev_nodes_sorted[0][3]
                else:
                    for j, prev_node_arr in enumerate(prev_nodes_sorted):
                        if prev_node_arr[0].vm is vm:
                            continue
                        else:
                            another_est = prev_node_arr[3]
                            break

                max_est_arr.append([avail_est, another_est])

            min_eft = sys.maxsize
            max_est = None
            assigned_vm = None
            for i, vm in enumerate(self.vms):
                est = max(max_est_arr[i])
                eft = est + node.exec_times_by_vm[i]
                if eft < min_eft:
                    min_eft = eft
                    max_est = est
                    assigned_vm = vm

            node.est = max_est
            node.eft = min_eft
            node.vm = assigned_vm
            assigned_vm.previous_task = node
            assigned_vm.previous_tasks.append(node)
            assigned_vm.current_time = node.eft

            self.log = self.log._append({'workflow_id': node.workflow_id, 'vm_id': node.vm.id, 'vm_type': node.vm.type,
                                         'task_id': node.id, 'task_name': node.name, 'task_batch': 0,
                                         'task_start': node.est, 'task_end': node.eft, 'interval': 0,
                                         'vm_start': node.est, 'vm_input_time': 0,
                                         'task_allocation_start': 0, 'task_allocation_end': 0,
                                         'vm_output_time': 0, 'vm_end': node.eft,
                                         'allocation_cost': 0, 'idle_time': 0, 'vm_status': 0},
                                        ignore_index=True)

    def count_cost(self):
        total_cost = 0
        for vm in self.vms:
            total_cost += vm.current_time * vm.cost
        self.total_cost = total_cost