import ctypes
import math
import random
import sys
import time

import pandas as pd
from munkres import Munkres, print_matrix, DISALLOWED, make_cost_matrix

from AllocationModule.Model.PossibleAssignment import PossibleAssignment
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VM import VM
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Workflow import round_up


class AllocationModule:
    def __init__(self, vm_types, tasks):
        self.vm_types = vm_types
        self.tasks = tasks
        self.vms = []
        self.log = pd.DataFrame(columns=['vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
                                         'task_end', 'interval', 'vm_start', 'input_data', 'task_allocation_start',
                                         'task_allocation_end', 'output_data', 'vm_end', 'allocation_cost'])

        self.DATA_TRANSFER_CHANNEL_SPEED = None
        self.OPTIMIZATION_CRITERIA = None
        self.MAX_WAIT_TIME = None

    def setDataTransferSpeed(self, DATA_TRANSFER_SPEED):
        self.DATA_TRANSFER_SPEED = DATA_TRANSFER_SPEED

    def setOptimizationCriteria(self, OPTIMIZATION_CRITERIA):
        self.OPTIMIZATION_CRITERIA = OPTIMIZATION_CRITERIA

    def setMaxWaitTime(self, MAX_WAIT_TIME):
        self.MAX_WAIT_TIME = MAX_WAIT_TIME



    ########## SEPARATING TASKS INTO (FORMING)BATCHES (FTL ALGORITHM) ##########
    def calcTimingsForVM(self, vm_type):
        for task in self.tasks:
            task.calc_time = task.volume / vm_type.perf
            task.latest_start = task.end - task.calc_time
            task.earliest_finish = task.start + task.calc_time

    def assignToLeader(self, tasks, time, batches):
        batch = []
        EFT = sys.maxsize
        for task in tasks:
            task.possible_start = max(task.start, time)
            task.earliest_finish = task.possible_start + task.calc_time
            EFT = task.earliest_finish if task.earliest_finish < EFT else EFT

        for task in tasks:
            if task.earliest_finish == EFT:
                task.status = 'Leader'
                task.batch = len(batches)
                task.finish_time = EFT
                batch.append(task)
                continue
            if task.latest_start < EFT:
                task.status = 'Batch'
                task.batch = len(batches)
                task.finish_time = EFT
                batch.append(task)

        batches.append(batch)

        return EFT

    def formParallelBatches(self, time):
        batches = []
        leader_vm_type = max(self.vm_types, key=lambda vm_type: vm_type.perf)
        self.calcTimingsForVM(leader_vm_type)
        tasks_with_none_status = list(filter(lambda i: i.status is None, self.tasks))

        while tasks_with_none_status:
            time = self.assignToLeader(tasks_with_none_status, time, batches)
            tasks_with_none_status = list(filter(lambda i: i.status is None, tasks_with_none_status))

        return batches



    ########## PREPARE (TASK:VM) MATCHINGS ##########
    def clearTasksFromOff(self, batch):
        return list(filter(lambda task: task.type != 'off', batch))

    def getActiveVms(self):
        return list(filter(lambda vm: vm.status == 'active', self.vms))

    def addOffTasks(self, batch, num, counter=0):
        for i in range(num):
            batch.append(Task(id=Task.task_counter + 1, name='off' + str(i + counter), volume=0, type='off'))

        return batch

    def addNewVmsRandomly(self, num, vm_perf_factor):
        if vm_perf_factor < 10:
            # 1. take more samples then required by factor of vm_perf_factor
            initial_sample_num = num * vm_perf_factor if vm_perf_factor >= 1 else num / vm_perf_factor
            initial_sample_num = math.ceil(initial_sample_num)

            # random_types = self.vm_types.sample(initial_sample_num, replace=True)
            random_types = random.choices(self.vm_types, k=initial_sample_num)

            # 2. if needed - pick first n by perf
            if vm_perf_factor != 1:
                # ???? initial_sample_num vs num ????
                # random_types = random_types.nlargest(num, 'perf') if vm_perf_factor >= 1 else random_types.nsmallest(num, 'perf')
                if vm_perf_factor >= 1:
                    random_types = random_types.sort(key=lambda vm_type: vm_type.perf, reverse=True)[:num]
                else:
                    random_types = random_types.sort(key=lambda vm_type: vm_type.perf)[:num]

        else:
            # take all max perf VMs in case vm_perf_factor is really big
            # ???? initial_sample_num vs num ????
            # maxPerf = vm_types.perf.max()
            # random_types = vm_types[vm_types.perf == maxPerf].sample(num, replace=True)
            max_perf_vm_type = max(self.vm_types, key=lambda vm_type: vm_type.perf)
            random_types = [VMType(max_perf_vm_type.type,
                                   max_perf_vm_type.perf,
                                   max_perf_vm_type.cost) for i in range(num)]

        for vm_type in random_types:
            self.vms.append(VM(vm_type.type,
                               vm_type.perf,
                               vm_type.cost))

    def addActiveVms(self, task):
        for vm in self.vms:
            task.possible_vms.append(vm)

    def addNewVms(self, task):
        for vm_type in self.vm_types:
            task.possible_vms.append(VM(vm_type.type, vm_type.perf, vm_type.cost))

    def prepareVmMatchings(self, batch, additional_vms_num):
        # first remove old temp tasks and not started vms
        if batch:
            batch = self.clearTasksFromOff(batch)
        if self.vms:
            self.vms = self.getActiveVms()

        vms_to_add = 0
        off_tasks_to_add = 0

        if self.vms:
            vms_to_add += additional_vms_num
            off_tasks_to_add += len(self.vms)
            batch = self.addOffTasks(batch, off_tasks_to_add, len(batch) + 1)  # use len(batch) + 1 to avoid name collisions

        for task in batch:
            self.addNewVms(task)

        return batch



    ########## CALCULATING ALLOCATION COST ##########
    def calcVmAllocationCost(self, task, vm):

        if task.name == 'ID00004':
            y = 0

        # init
        current_time = -100
        idle_time = 0  # time vm idle between end of previous task and start of current task (len)
        preparation_time = 0  # time needed to prepare vm to start task (usually start vm + get data) (len)
        runtime = 0  # actual task runtime (len)
        release_time = 0  # time needed to cleanup vm and copy its data before turn off (len)
        max_data_transfer_time = 0  # max time needed to transfer all data from all source tasks (len)

        earliest_data_ready_time = 0  # earliest time all data can be copied from source tasks (moment)
        input_data_transfer = 0
        output_data_transfer = None

        # if new vm
        if (vm.status == 'open'):
            possible_vm_start = current_time  # can start now
        else:
            possible_vm_start = vm.previous_task.allocation_end

        # if turning off
        if task.type == 'off':
            possible_task_start = current_time  # release task can be started any time (no input data/logic restrictions)

            # calculate time needed to transfer data before shut down vm
            release_time = vm.release_time
            previous_task = vm.previous_task

            if previous_task is not None and previous_task.output_size > 0:
                output_data_transfer_time = -sys.maxsize
                for transfer in previous_task.output_transfers:
                    task_to = transfer.task_to
                    transfer_time = math.ceil(transfer.transfer_size / self.DATA_TRANSFER_SPEED)  # maybe speed should be decreased based on number of parallel data transfers
                    transfer_end = previous_task.allocation_end + transfer_time

                    # meaning time between the time vm can be stopped and it finishes the longest data transfer
                    if output_data_transfer_time < transfer_end - possible_vm_start:
                        output_data_transfer_time = transfer_end - possible_vm_start

                if output_data_transfer_time < 0:
                    y = 0
                output_data_transfer_time = max(output_data_transfer_time, 0)  # can't be negative
                release_time = release_time + output_data_transfer_time
                output_data_transfer = output_data_transfer_time

        # if perform calculations
        else:
            # runtime = math.ceil(row.volume / vm_type.perf)
            runtime = task.volume / vm.perf
            if (vm.status == 'open'):
                preparation_time += vm.prep_time  # add vm startup time

            # calculate additional preparation time to copy required input data
            earliest_data_ready_time_max = -sys.maxsize
            data_transfer_time_max = -sys.maxsize

            if task.input_size > 0:
                input_tasks = []

                #TODO: create node_edges and data_center_edges and check their times
                for transfer in task.input_transfers:
                    task_from = transfer.task_from
                    input_tasks.append(task_from)

                    if transfer.task_from.assigned_vm is vm:
                        transfer_time = 0
                    else:
                        transfer_time = math.ceil(transfer.transfer_size / self.DATA_TRANSFER_SPEED)  # maybe speed should be decreased based on number of parallel data transfers

                    if data_transfer_time_max < transfer_time:
                        data_transfer_time_max = transfer_time

                    # when there is input from 'entry' point
                    if task_from.id == 0:
                        task_from_allocation_end = 0
                    else:
                        task_from_allocation_end = task_from.allocation_end

                    try:
                        if earliest_data_ready_time_max < task_from_allocation_end + transfer_time:
                            earliest_data_ready_time_max = task_from_allocation_end + transfer_time
                    except:
                        print("calcVmAllocationCost\ntask_id={}, task_name={}".format(task.id, task.name))

                preparation_time = preparation_time + data_transfer_time_max
                input_data_transfer = data_transfer_time_max

            # possibly check if can start earlier, i.e. remove row.start from max
            if earliest_data_ready_time_max > task.start:
                y = 0
            possible_task_start = max(task.start, earliest_data_ready_time_max)

        full_runtime = preparation_time + runtime + release_time

        expected_vm_start = max(possible_vm_start, possible_task_start - preparation_time)
        expected_vm_end = expected_vm_start + full_runtime
        if (vm.status != 'open'):
            # idle time between previous assignment and new assignment
            idle_time = (expected_vm_start - possible_vm_start)

        expected_task_start = expected_vm_start + preparation_time
        expected_task_end = expected_task_start + runtime

        possible_assignment = PossibleAssignment(vm)

        if expected_task_end > task.end and task.type == 'task':
            allocation_cost = 10000000000  # can't execute task
        else:
            possible_assignment.task_allocation_start = round_up(expected_task_start)
            possible_assignment.task_allocation_end = round_up(expected_task_end)
            possible_assignment.vm_allocation_start = round_up(expected_vm_start)
            possible_assignment.vm_allocation_end = round_up(expected_vm_end)

            allocation_cost = round_up((full_runtime + idle_time) * vm.cost)

        if self.OPTIMIZATION_CRITERIA == "max":
            allocation_cost = -allocation_cost

        # allocation_cost + 1 because zeros are bad for optimization for Munkres function
        allocation_cost += 1
        if possible_assignment.task_allocation_start is not None:
            possible_assignment.allocation_cost = allocation_cost
            task.possible_assignments.append(possible_assignment)
            return True, allocation_cost, possible_assignment
        else:
            return False, allocation_cost, possible_assignment



    ########## CHOOSING THE BEST MATCHES (MUNKRES ALGORITHM) ##########
    def calcMinCostPairings(self, batch):
        vms = self.vms.copy()
        cost_matrix = []
        active_num = len(self.vms)

        for t, task in enumerate(batch):
            if task.type == 'task':
                # if task.id == 49:
                #     y = 0
                possible_vms = [vm for vm in task.possible_vms if self.calcVmAllocationCost(task, vm)[0]]
                task.possible_vms = possible_vms

                try:
                    assignment_with_min_cost = min(task.possible_assignments, key=lambda possible_assignment: possible_assignment.allocation_cost)
                except:
                    print("Task(id={}, name={})".format(task.id, task.name))


                min_cost = assignment_with_min_cost.allocation_cost
                vm = assignment_with_min_cost.assigned_vm
                vms.append(vm)

                vm_costs_for_task = [DISALLOWED] * len(batch)
                for i, vm in enumerate(self.vms):
                    cost = self.calcVmAllocationCost(task, vm)[1]
                    if (self.OPTIMIZATION_CRITERIA == "min" and cost < 1000000000 or
                            self.OPTIMIZATION_CRITERIA == "max" and cost > -1000000000):
                        vm_costs_for_task[i] = cost

                vm_costs_for_task[active_num + t] = min_cost
                cost_matrix.append(vm_costs_for_task)

        # calc costs of off tasks
        off_tasks = list(filter(lambda task: task.type == 'off', batch))
        if off_tasks:
            off_task = off_tasks[0]

            vm_costs_for_task = [DISALLOWED] * len(batch)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(vms):
                bool, cost, assign_info = self.calcVmAllocationCost(off_task, vm)
                if (self.OPTIMIZATION_CRITERIA == "min" and cost < 1000000000 or
                        self.OPTIMIZATION_CRITERIA == "max" and cost > -1000000000):
                    vm_costs_for_task[i] = cost
                    possible_assignments_for_off_tasks.append(assign_info)
            cost_matrix.append(vm_costs_for_task)

            for i in range(1, len(off_tasks)):
                off_tasks[i].possible_assignments = possible_assignments_for_off_tasks
                cost_matrix.append(vm_costs_for_task)

        m = Munkres()
        result = m.compute(cost_matrix)

        pairs = []
        for row, column in result:
            task = batch[row]
            vm = vms[column]
            pairs.append((task, vm))

        return pairs



    ########## PAIRING and LOGGING ##########
    def applyPairings(self, pairs):
        for pair in pairs:
            if pair[0].type == 'off' and pair[1].status == 'open':
                continue
            elif pair[0].type == 'task' and pair[1].status == 'open':
                pair[1].setStatus('active')
                self.vms.append(pair[1])
            elif pair[0].type == 'off' and pair[1].status == 'active':
                pair[1].setStatus('shutdown')

            pair[1].setPreviousTask(pair[0])
            pair[0].setAssignedVm(pair[1])

            self.log = self.log._append({'vm_id': pair[1].id, 'vm_type': pair[1].type, 'task_id': pair[0].id,
                        'task_name': pair[0].name, 'task_batch': pair[0].batch, 'task_start': pair[0].start,
                        'task_end': pair[0].end,
                        'interval': pair[0].interval, 'vm_start': pair[0].vm_allocation_start,
                        'input_data': pair[0].input_time, 'task_allocation_start': pair[0].allocation_start,
                        'task_allocation_end': pair[0].allocation_end, 'output_data': pair[0].output_time,
                        'vm_end': pair[0].vm_allocation_end, 'allocation_cost': pair[0].allocation_cost - 1}, ignore_index=True)



    ########## ALLOCATION BATCHES (VMA ALGORITHM) ##########
    def allocateBatch(self, batch):
        # prepare tasks and vms for matching
        batch = self.prepareVmMatchings(batch, additional_vms_num=len(batch))
        # calc allocation costs for matches (munkres algorithm)
        pairings = self.calcMinCostPairings(batch)
        # pairing and logging
        self.applyPairings(pairings)

    def vma(self, batches):
        for batch in batches:
            self.allocateBatch(batch)

        self.allocateBatch([])

