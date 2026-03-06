import math
import random
import sys
from datetime import datetime
from logging import critical
import numpy as np
from scipy.optimize import linear_sum_assignment

import pandas as pd
from munkres import Munkres, print_matrix, DISALLOWED, make_cost_matrix

import config
from AllocationModule.Model.PossibleAssignment import PossibleAssignment
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VM import VM
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Model.Criteria import CostCriteria, TimeCriteria, AverageResourceLoadCriteria
from SchedulingModule.CJM.Workflow import round_up
from config import DATA_TRANSFER_CHANNEL_SPEED


class AllocationASAP:
    def __init__(self, criteria, vm_types, tasks):
        self.vm_types = vm_types
        self.tasks = tasks
        self.num_workflows = self.tasks[-1].workflow_id + 1
        self.cost_of_workflow = [0 for workflow_id in range(self.num_workflows)]
        self.vms = []
        self.criteria = criteria
        self.log = pd.DataFrame(columns=['workflow_id', 'vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
                                         'task_end', 'interval', 'vm_start', 'vm_input_time', 'vm_input_size', 'vm_output_size',
                                         'task_allocation_start',
                                         'task_allocation_end', 'vm_output_time', 'vm_end', 'allocation_cost', 'idle_time', 'vm_status'])
        self.num_workflow_deadline_met = None
        self.percentage_workflow_deadline_met = None
        self.batches_size = None
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
        self.different_workflow_reuse_vm_counter = 0

        self.map_vm_perf_for_transfer = None
        self.create_vm_for_transfer()


    ########## SEPARATING TASKS INTO (FORMING)BATCHES (FTL ALGORITHM) ##########
    def calcTimingsForVM(self, vm_type):
        for task in self.tasks:
            task.calc_time = math.ceil(task.volume / vm_type.perf)
            task.earliest_start = task.start
            task.earliest_finish = task.earliest_start + task.calc_time
            task.latest_finish = task.end
            task.latest_start = task.latest_finish - task.calc_time
            task.earliest_finish = task.earliest_start + task.calc_time


    def assignToLeader(self, tasks, time, batches):
        batch = []
        EFT = sys.maxsize
        for task in tasks:
            task.possible_start = max(task.start, time)
            task.earliest_finish = task.possible_start + task.calc_time
            EFT = task.earliest_finish if task.earliest_finish < EFT else EFT

        for task in tasks:
            if task.id == 53:
                y = 0
            # if (list(filter(lambda transfer: transfer.task_from.status is None, task.input_transfers)) or task.possible_start >= EFT):
            if list(filter(lambda transfer: transfer.task_from.status is None, task.input_transfers)):
                continue
            else:
                task.batch = len(batches)
                batch.append(task)

        for task in batch:
            task.status = 'Batch'

        batches.append(batch)

        return EFT

    def formParallelBatches(self, time):
        batches = []
        leader_vm_type = max(self.vm_types, key=lambda vm_type: vm_type.perf)
        self.calcTimingsForVM(leader_vm_type)
        tasks_with_none_status = list(filter(lambda i: i.status is None, self.tasks))

        while tasks_with_none_status:
            time = self.assignToLeader(tasks_with_none_status, time, batches)
            # TODO
            tasks_with_none_status = list(filter(lambda i: i.status is None, tasks_with_none_status))

        return batches



    ########## PREPARE (TASK:VM) MATCHINGS ##########
    def clearTasksFromOff(self, batch):
        return list(filter(lambda task: task.type != 'off', batch))

    def getActiveVms(self):
        return list(filter(lambda vm: vm.status == 'active', self.vms))

    def addOffTasks(self, batch, num, counter=0):
        for i in range(num):
            batch.append(Task(id=Task.task_counter + 1, name='off' + str(i + counter), volume=0, workflow_id=-1, type='off'))

        return batch

    def addNewVms(self, task):
            for vm_type in self.vm_types:
                task.possible_vms.append(
                    VM(vm_type.type, vm_type.perf, vm_type.cost, vm_type.bandwidth, vm_type.prep_time, vm_type.shutdown_time))

    def prepareVmMatchings(self, batch, additional_vms_num):
        # first remove old temp tasks and not started vms
        if batch:
            batch = self.clearTasksFromOff(batch)
        if self.vms:
            self.vms = self.getActiveVms()

        off_tasks_to_add = 0

        if self.vms:
            off_tasks_to_add += len(self.vms)
            batch = self.addOffTasks(batch, off_tasks_to_add, len(batch) + 1)  # use len(batch) + 1 to avoid name collisions

        for task in batch:
            self.addNewVms(task)

        return batch



    ########## CALCULATING ALLOCATION COST ##########
    def calcVmAllocationCost(self, task, vm):
        # if task.id == 0 or task.id == 45 or task.id == 48:
        if task.id == 47:
            y = 0
        # init
        # current_time = -100
        current_time = -sys.maxsize
        idle_time = 0  # time vm idle between end of previous task and start of current task (len)
        preparation_time = 0  # time needed to prepare vm to start task (usually start vm + get data) (len)
        task_runtime = 0  # actual task runtime (len)
        shutdown_time = 0  # time needed to cleanup vm and copy its data before turn off (len)
        max_data_transfer_time = 0  # max time needed to transfer all data from all source tasks (len)

        earliest_data_ready_time = 0  # earliest time all data can be copied from source tasks (moment)
        input_data_transfer_time = 0
        output_data_transfer_time = 0
        input_data_transfer_size = 0
        output_data_transfer_size = 0

        transfer_time_into_storage = 0
        transfer_time_from_storage = 0
        task_from_output_transfer_time = 0

        # if new vm
        if (vm.status == 'open'):
            possible_vm_start = current_time  # can start now
        else:
            possible_vm_start = vm.previous_task.allocation_end

        # if turning off
        if task.type == 'off':
            possible_task_start = current_time  # release task can be started any time (no input data/logic restrictions)

            # calculate time needed to transfer data before shut down vm
            shutdown_time = vm.shutdown_time
            previous_task = vm.previous_task

            if previous_task is not None and previous_task.output_size > 0:
                output_data_transfer_time_max = -sys.maxsize
                output_data_transfer_size_max = -sys.maxsize
                for transfer in previous_task.output_transfers:
                    transfer_time = math.ceil(transfer.transfer_size / min(DATA_TRANSFER_CHANNEL_SPEED, vm.bandwidth))
                    transfer_size = transfer.transfer_size

                    transfer_end = previous_task.allocation_end + transfer_time

                    # meaning time between the time vm can be stopped and it finishes the longest data transfer
                    if output_data_transfer_time_max < (transfer_end - possible_vm_start):
                        output_data_transfer_time_max = transfer_end - possible_vm_start
                        output_data_transfer_size_max = transfer_size

                if output_data_transfer_time_max < 0:
                    y = 0
                output_data_transfer_time_max = max(output_data_transfer_time_max, 0)  # can't be negative
                shutdown_time = shutdown_time + output_data_transfer_time_max
                output_data_transfer_time = output_data_transfer_time_max
                output_data_transfer_size = output_data_transfer_size_max

        # if perform calculations
        else:
            task_runtime = math.ceil(task.volume / vm.perf)
            # runtime = task.volume / vm.perf
            if (vm.status == 'open'):
                preparation_time += vm.prep_time  # add vm startup time

            # calculate additional preparation time to copy required input data
            earliest_data_ready_time_max = -sys.maxsize
            data_transfer_time_max = -sys.maxsize
            data_transfer_size_max = -sys.maxsize

            if task.input_transfers:
                #TODO: ? create node_edges and data_center_edges and check their times
                for transfer in task.input_transfers:
                    task_from = transfer.task_from

                    if transfer.task_from.assigned_vm is vm:
                        if len(task_from.output_transfers) > 1:
                            task_from_output_transfer_size_max = max(task_from.output_transfers, key=lambda
                                output_transfer: output_transfer.transfer_size).transfer_size

                            task_from_output_transfer_time = math.ceil(
                                task_from_output_transfer_size_max / min(DATA_TRANSFER_CHANNEL_SPEED, vm.bandwidth))
                            transfer_time = 0
                            transfer_size = task_from_output_transfer_size_max
                        else:
                            transfer_time = 0
                            transfer_size = 0
                    else:
                        if task_from.name == "entry":
                            transfer_time_into_storage = 0
                            transfer_time_from_storage = math.ceil(
                                transfer.transfer_size / min(DATA_TRANSFER_CHANNEL_SPEED, vm.bandwidth))
                            transfer_size = transfer.transfer_size
                        else:
                            transfer_time_into_storage = math.ceil(
                                transfer.transfer_size / min(DATA_TRANSFER_CHANNEL_SPEED,
                                                             task_from.assigned_vm.bandwidth))
                            transfer_time_from_storage = math.ceil(
                                transfer.transfer_size / min(DATA_TRANSFER_CHANNEL_SPEED, vm.bandwidth))
                            transfer_size = transfer.transfer_size * 2

                            # if transfer_time_into_storage < transfer_time_from_storage and config.T == 1:
                            #     return False, 1000000000, None

                        transfer_time = transfer_time_into_storage + transfer_time_from_storage

                    if data_transfer_time_max < transfer_time:
                        data_transfer_time_max = transfer_time
                        data_transfer_size_max = transfer_size

                    if task_from.name == "entry":
                        task_from_allocation_time_end = task_from.end
                    else:
                        task_from_allocation_time_end = task_from.allocation_end

                    try:
                        if earliest_data_ready_time_max < task_from_allocation_time_end + transfer_time + preparation_time:
                            earliest_data_ready_time_max = task_from_allocation_time_end + transfer_time + preparation_time
                    except:
                        print("calcVmAllocationCost\ntask_id={}, task_name={}".format(task.id, task.name))

                preparation_time = preparation_time + data_transfer_time_max
                input_data_transfer_time = data_transfer_time_max
                input_data_transfer_size = data_transfer_size_max

            # possibly check if can start earlier, i.e. remove row.start from max
            # possible_task_start = min(task.start, earliest_data_ready_time_max)
            possible_task_start = earliest_data_ready_time_max

        vm_runtime = preparation_time + task_runtime + shutdown_time + task_from_output_transfer_time

        expected_vm_start = max(possible_vm_start, possible_task_start - preparation_time)
        expected_vm_end = expected_vm_start + vm_runtime
        if (vm.status != 'open'):
            # idle time between previous assignment and new assignment
            idle_time = (expected_vm_start - possible_vm_start)

        expected_task_start = expected_vm_start + preparation_time + task_from_output_transfer_time
        expected_task_end = expected_task_start + task_runtime

        possible_assignment = PossibleAssignment(vm)

        possible_transfer_time = 0
        actual_transfer_time = 0
        if task.type == 'task':
            max_transfer = max(task.output_transfers, key=lambda transfer: transfer.transfer_time)
            possible_transfer_time = task.end + max_transfer.transfer_time
            actual_transfer_time = expected_task_end + round_up(max_transfer.transfer_size / vm.bandwidth)
            # if expected_task_end > task.end and task.type == 'task' or actual_transfer_time > possible_transfer_time:
            #     y = 0

        if expected_task_end > task.end and task.type == 'task' or actual_transfer_time > possible_transfer_time:
            allocation_cost = 10000000000  # can't execute task
        else:
            possible_assignment.task_allocation_start = expected_task_start
            possible_assignment.task_allocation_end = expected_task_end
            possible_assignment.vm_allocation_start = expected_vm_start
            possible_assignment.vm_allocation_end = expected_vm_end
            possible_assignment.idle_time = idle_time
            possible_assignment.input_data_transfer_time = input_data_transfer_time
            possible_assignment.output_data_transfer_time = output_data_transfer_time
            possible_assignment.input_data_transfer_size = input_data_transfer_size
            possible_assignment.output_data_transfer_size = output_data_transfer_size

            allocation_cost = math.ceil((vm_runtime + idle_time) * vm.cost)

            if (task_from_output_transfer_time == 0) and (vm.status == 'open'):
                possible_assignment.vm_allocation_start = expected_vm_start + transfer_time_into_storage
                possible_assignment.input_data_transfer_time = input_data_transfer_time - transfer_time_into_storage
                possible_assignment.input_data_transfer_size = input_data_transfer_size/2
                allocation_cost = math.ceil((vm_runtime + idle_time - transfer_time_into_storage) * vm.cost)

        if self.criteria.optimization_criteria == "max":
            allocation_cost = -allocation_cost

        # allocation_cost + 1 because zeros are bad for optimization for Munkres function
        allocation_cost += 1
        if possible_assignment.task_allocation_start is not None:
            possible_assignment.allocation_cost = allocation_cost
            task.new_possible_assignments.append(possible_assignment)
            return True, allocation_cost, possible_assignment
        else:
            return False, allocation_cost, possible_assignment


    ########## CHOOSING THE BEST MATCHES (MUNKRES ALGORITHM) ##########
    def calcMinCostPairings(self, batch):
        vms = self.vms.copy()
        cost_matrix = []
        active_num = len(self.vms)

        for t, task in enumerate(batch):
            assignment_with_desired_cost = None
            if task.type == 'task':
                if task.id == 2:
                    y = 0
                possible_vms = [vm for vm in task.possible_vms if self.calcVmAllocationCost(task, vm)[0]]
                task.possible_vms = possible_vms

                try:
                    if (self.criteria.optimization_criteria == "min"):
                        # assignment_with_desired_cost = min(task.possible_assignments, key=lambda possible_assignment: possible_assignment.allocation_cost)
                        min_cost = sys.maxsize
                        for assignment in task.new_possible_assignments:
                            cost = assignment.allocation_cost
                            if cost <= min_cost:
                                assignment_with_desired_cost = assignment
                                min_cost = cost
                    else:
                        assignment_with_desired_cost = max(task.new_possible_assignments, key=lambda possible_assignment: possible_assignment.allocation_cost)
                except:
                    print("Task(id={}, name={})".format(task.id, task.name))
                    # return

                best_cost = assignment_with_desired_cost.allocation_cost
                vm = assignment_with_desired_cost.assigned_vm
                vms.append(vm)


                vm_costs_for_task = [np.inf] * len(batch)
                for i, vm in enumerate(self.vms):
                    cost = self.calcVmAllocationCost(task, vm)[1]
                    if (self.criteria.optimization_criteria == "min" and cost < 1000000000 or
                            self.criteria.optimization_criteria == "max" and cost > -1000000000):
                        vm_costs_for_task[i] = cost

                vm_costs_for_task[active_num + t] = best_cost
                cost_matrix.append(vm_costs_for_task)
                cost_matrix_np = np.array([
                    [4, 1, 3],
                    [2, 0, 5],
                    [3, 2, 2]
                ])


        # calc costs of off tasks
        off_tasks = list(filter(lambda task: task.type == 'off', batch))
        if off_tasks:
            off_task = off_tasks[0]

            vm_costs_for_task = [np.inf] * len(batch)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(vms):
                bool, cost, assign_info = self.calcVmAllocationCost(off_task, vm)
                if (self.criteria.optimization_criteria == "min" and cost < 1000000000 or
                        self.criteria.optimization_criteria == "max" and cost > -1000000000):
                    vm_costs_for_task[i] = cost
                    possible_assignments_for_off_tasks.append(assign_info)
            cost_matrix.append(vm_costs_for_task)

            for i in range(1, len(off_tasks)):
                off_tasks[i].new_possible_assignments = possible_assignments_for_off_tasks
                cost_matrix.append(vm_costs_for_task)

        # m = Munkres()
        # result = m.compute(cost_matrix)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)


        pairs = []
        # print("Оптимальные назначения (индексы):")
        for r, c in zip(row_ind, col_ind):
            # print(f"Работник {r} -> Задача {c} (стоимость: {cost_matrix[r, c]})")
        # for row, column in result:
            task = batch[r]
            vm = vms[c]
            pairs.append((task, vm))

        return pairs


    def calcMinTimePairings(self, batch):
        vms = self.vms.copy()
        time_matrix = []
        active_num = len(self.vms)

        for t, task in enumerate(batch):
            if task.type == 'task':
                if task.id >= 27 and task.id <= 37:
                    y = 0
                possible_vms = [vm for vm in task.possible_vms if self.calcVmAllocationCost(task, vm)[0]]
                task.possible_vms = possible_vms

                try:
                    if (self.criteria.optimization_criteria == "min"):
                        assignment_with_min_time = min(task.new_possible_assignments, key=lambda possible_assignment: possible_assignment.task_allocation_end)
                except:
                    print("Task(id={}, name={})".format(task.id, task.name))

                best_time = assignment_with_min_time.task_allocation_end
                vm = assignment_with_min_time.assigned_vm
                vms.append(vm)

                vm_times_for_task = [np.inf] * len(batch)
                for i, vm in enumerate(self.vms):
                    res = self.calcVmAllocationCost(task, vm)
                    if res[0]:
                        vm_times_for_task[i] = res[2].task_allocation_end

                vm_times_for_task[active_num + t] = best_time
                time_matrix.append(vm_times_for_task)

        # calc costs of off tasks
        off_tasks = list(filter(lambda task: task.type == 'off', batch))
        if off_tasks:
            off_task = off_tasks[0]

            vm_times_for_task = [np.inf] * len(batch)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(vms):
                res = self.calcVmAllocationCost(off_task, vm)
                if res[0]:
                    vm_times_for_task[i] = res[2].task_allocation_end
                    possible_assignments_for_off_tasks.append(res[2])
            time_matrix.append(vm_times_for_task)

            for i in range(1, len(off_tasks)):
                off_tasks[i].new_possible_assignments = possible_assignments_for_off_tasks
                time_matrix.append(vm_times_for_task)

        # m = Munkres()
        # result = m.compute(cost_matrix)

        row_ind, col_ind = linear_sum_assignment(time_matrix)


        pairs = []
        # print("Оптимальные назначения (индексы):")
        for r, c in zip(row_ind, col_ind):
            # print(f"Работник {r} -> Задача {c} (стоимость: {cost_matrix[r, c]})")
        # for row, column in result:
            task = batch[r]
            vm = vms[c]
            pairs.append((task, vm))

        return pairs



    ########## PAIRING and LOGGING ##########
    def applyPairings(self, pairs):
        for pair in pairs:
            vm_status = 'active'
            if pair[0].type == 'task' and pair[1].status == 'active':
                if pair[1].previous_task.workflow_id != pair[0].workflow_id:
                    self.different_workflow_reuse_vm_counter += 1
            if pair[0].type == 'off' and pair[1].status == 'open':
                continue
            elif pair[0].type == 'task' and pair[1].status == 'open':
                vm_status = 'new'
                pair[1].setStatus('active')
                self.vms.append(pair[1])
            elif pair[0].type == 'off' and pair[1].status == 'active':
                pair[1].setStatus('shutdown')
                pair[0].workflow_id = pair[1].previous_task.workflow_id

            pair[1].setPreviousTask(pair[0])
            pair[0].setAssignedVm(pair[1])
            cost = pair[0].allocation_cost - 1
            self.cost_of_workflow[pair[0].workflow_id] = self.cost_of_workflow[pair[0].workflow_id] + pair[0].allocation_cost - 1

            self.log = self.log._append({'workflow_id': pair[0].workflow_id, 'vm_id': pair[1].id, 'vm_type': pair[1].type,
                                         'task_id': pair[0].id, 'task_name': pair[0].name, 'task_batch': pair[0].batch,
                                         'task_start': pair[0].start, 'task_end': pair[0].end, 'interval': pair[0].interval,
                                         'vm_start': pair[0].vm_allocation_start, 'vm_input_time': pair[0].vm_input_time,
                                         'vm_input_size': pair[0].vm_input_size, 'vm_output_size': pair[0].vm_output_size,
                                         'task_allocation_start': pair[0].allocation_start, 'task_allocation_end': pair[0].allocation_end,
                                         'vm_output_time': pair[0].vm_output_time, 'vm_end': pair[0].vm_allocation_end,
                                         'allocation_cost': pair[0].allocation_cost - 1, 'idle_time': pair[0].idle_time, 'vm_status': vm_status},
                                        ignore_index=True)



    ########## ALLOCATION BATCHES (VMA ALGORITHM) ##########
    def allocateBatch(self, batch):
        # prepare tasks and vms for matching
        batch = self.prepareVmMatchings(batch, additional_vms_num=len(batch))
        # calc allocation costs for matches (munkres algorithm)
        if isinstance(self.criteria, CostCriteria):
            pairings = self.calcMinCostPairings(batch)
            if pairings is None:
                return 0
        elif isinstance(self.criteria, TimeCriteria):
            pairings = self.calcMinTimePairings(batch)
        # pairing and logging
        self.applyPairings(pairings)

    def vma(self, batches):
        n = len(batches)
        for i, batch in enumerate(batches):
            a = self.allocateBatch(batch)
            if a is 0:
                return 0
            print(f"Batch #{i} out of {n}")
            print(f"{len(batch)} in the batch #{i}")

        self.allocateBatch([])


    def create_vm_for_transfer(self):
        n = len(self.vm_types)
        vm_for_transfer = list(reversed(self.vm_types))
        self.map_vm_perf_for_transfer = {}
        for i, vm in enumerate(self.vm_types):
            self.map_vm_perf_for_transfer[vm.perf] = vm_for_transfer[i].perf

