import math
import random
import sys

import pandas as pd
from munkres import Munkres, print_matrix, DISALLOWED, make_cost_matrix

from AllocationModule.Model.PossibleAssignment import PossibleAssignment
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VM import VM
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Workflow import round_up


class RandomAssignment:
    def __init__(self, criteria, vm_types, tasks):
        self.vm_types = vm_types
        self.tasks = tasks
        self.num_workflows = self.tasks[-1].workflow_id + 1
        self.cost_of_workflow = [0 for workflow_id in range(self.num_workflows)]
        self.vms = []
        self.criteria = criteria
        self.log = pd.DataFrame(columns=['workflow_id', 'vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
                                         'task_end', 'interval', 'vm_start', 'vm_input_time', 'task_allocation_start',
                                         'task_allocation_end', 'vm_output_time', 'vm_end', 'allocation_cost', 'idle_time'])
        self.num_workflow_deadline_met = None
        self.percentage_workflow_deadline_met = None
        self.total_cost = None
        self.total_time = None
        self.total_num_leased_vm = None
        self.total_idle_time = None


    ########## SEPARATING TASKS INTO (FORMING)BATCHES (FTL ALGORITHM) ##########
    def calcTimingsForVM(self, vm_type):
        for task in self.tasks:
            task.calc_time = math.ceil(task.volume / vm_type.perf)
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
            batch.append(Task(id=Task.task_counter + 1, name='off' + str(i + counter), volume=0, workflow_id=-1, type='off'))

        return batch

    def addNewVmsRandomly(self, num):
        initial_sample_num = num
        random_types = random.choices(self.vm_types, k=initial_sample_num)

        for vm_type in random_types:
            self.vms.append(VM(vm_type.type,
                               vm_type.perf,
                               vm_type.cost,
                               vm_type.prep_time,
                               vm_type.shutdown_time))

    def addActiveVms(self, task):
        for vm in self.vms:
            task.possible_vms.append(vm)

    def addNewVms(self, task):
        for vm_type in self.vm_types:
            task.possible_vms.append(VM(vm_type.type, vm_type.perf, vm_type.cost, vm_type.prep_time, vm_type.shutdown_time))

    def prepareVmMatchings(self, batch, additional_vms_num):
        # first remove old temp tasks and not started vms
        if batch:
            batch = self.clearTasksFromOff(batch)
        if self.vms:
            self.vms = self.getActiveVms()

        vms_to_add = 0
        # off_tasks_to_add = 0

        diff = len(batch) - len(self.vms)
        if diff > 0:
            vms_to_add = vms_to_add + diff
        elif diff < 0:
            batch = self.addOffTasks(batch, -diff, len(batch) + 1) # use len(batch) + 1 to avoid name collisions

        # if self.vms:
        #     vms_to_add += additional_vms_num
        #     off_tasks_to_add += len(self.vms)
        #     batch = self.addOffTasks(batch, off_tasks_to_add, len(batch) + 1)  # use len(batch) + 1 to avoid name collisions

        self.addNewVmsRandomly(vms_to_add)

        return batch



    ########## CALCULATING ALLOCATION COST ##########
    def calcVmAllocationCost(self, task, vm):
        # init
        # current_time = -100
        current_time = -sys.maxsize
        idle_time = 0  # time vm idle between end of previous task and start of current task (len)
        preparation_time = 0  # time needed to prepare vm to start task (usually start vm + get data) (len)
        task_runtime = 0  # actual task runtime (len)
        release_time = 0  # time needed to cleanup vm and copy its data before turn off (len)
        max_data_transfer_time = 0  # max time needed to transfer all data from all source tasks (len)

        earliest_data_ready_time = 0  # earliest time all data can be copied from source tasks (moment)
        input_data_transfer_time = 0
        output_data_transfer_time = 0

        # if new vm
        if (vm.status == 'open'):
            possible_vm_start = current_time  # can start now
        else:
            possible_vm_start = vm.previous_task.allocation_end

        # if turning off
        if task.type == 'off':
            possible_task_start = current_time  # release task can be started any time (no input data/logic restrictions)

            # calculate time needed to transfer data before shut down vm
            release_time = vm.shutdown_time
            previous_task = vm.previous_task

            if previous_task is not None and previous_task.output_size > 0:
                output_data_transfer_time_max = -sys.maxsize
                for transfer in previous_task.output_transfers:
                    task_to = transfer.task_to
                    transfer_time = transfer.transfer_time
                    transfer_end = previous_task.allocation_end + transfer_time

                    # meaning time between the time vm can be stopped and it finishes the longest data transfer
                    if output_data_transfer_time_max < (transfer_end - possible_vm_start):
                        output_data_transfer_time_max = transfer_end - possible_vm_start

                if output_data_transfer_time_max < 0:
                    y = 0
                output_data_transfer_time_max = max(output_data_transfer_time_max, 0)  # can't be negative
                release_time = release_time + output_data_transfer_time_max
                output_data_transfer_time = output_data_transfer_time_max

        # if perform calculations
        else:
            task_runtime = math.ceil(task.volume / vm.perf)
            # runtime = task.volume / vm.perf
            if (vm.status == 'open'):
                preparation_time += vm.prep_time  # add vm startup time

            # calculate additional preparation time to copy required input data
            earliest_data_ready_time_max = -sys.maxsize
            data_transfer_time_max = -sys.maxsize

            if task.input_transfers:
                #TODO: ? create node_edges and data_center_edges and check their times
                for transfer in task.input_transfers:
                    task_from = transfer.task_from

                    if transfer.task_from.assigned_vm is vm:
                        transfer_time = 0
                    else:
                        transfer_time = transfer.transfer_time

                    if data_transfer_time_max < transfer_time:
                        data_transfer_time_max = transfer_time

                    if task_from.name == "entry":
                        task_from_allocation_time_end = task.start
                    else:
                        task_from_allocation_time_end = task_from.allocation_end

                    try:
                        if earliest_data_ready_time_max < task_from_allocation_time_end + transfer_time:
                            earliest_data_ready_time_max = task_from_allocation_time_end + transfer_time
                    except:
                        print("calcVmAllocationCost\ntask_id={}, task_name={}".format(task.id, task.name))

                preparation_time = preparation_time + data_transfer_time_max
                input_data_transfer_time = data_transfer_time_max

            # possibly check if can start earlier, i.e. remove row.start from max
            possible_task_start = min(task.start, earliest_data_ready_time_max)

        vm_runtime = preparation_time + task_runtime + release_time

        expected_vm_start = max(possible_vm_start, possible_task_start - preparation_time)
        expected_vm_end = expected_vm_start + vm_runtime
        if (vm.status != 'open'):
            # idle time between previous assignment and new assignment
            idle_time = (expected_vm_start - possible_vm_start)

        expected_task_start = expected_vm_start + preparation_time
        expected_task_end = expected_task_start + task_runtime

        possible_assignment = PossibleAssignment(vm)

        # if expected_task_end > task.end and task.type == 'task':
        #     allocation_cost = 10000000000  # can't execute task
        # else:
        possible_assignment.task_allocation_start = expected_task_start
        possible_assignment.task_allocation_end = expected_task_end
        possible_assignment.vm_allocation_start = expected_vm_start
        possible_assignment.vm_allocation_end = expected_vm_end
        possible_assignment.idle_time = idle_time
        possible_assignment.input_data_transfer_time = input_data_transfer_time
        possible_assignment.output_data_transfer_time = output_data_transfer_time

        allocation_cost = math.ceil((vm_runtime + idle_time) * vm.cost)

        if self.criteria.optimization_criteria == "max":
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
        cost_matrix = []

        for t, task in enumerate(batch):
            if task.type == 'task':
                if task.id == 1:
                    y = 0

                vm_costs_for_task = [DISALLOWED] * len(batch)
                for i, vm in enumerate(self.vms):
                    cost = self.calcVmAllocationCost(task, vm)[1]
                    if (self.criteria.optimization_criteria == "min" and cost < 1000000000 or
                            self.criteria.optimization_criteria == "max" and cost > -1000000000):
                        vm_costs_for_task[i] = cost

                cost_matrix.append(vm_costs_for_task)

        # calc costs of off tasks
        off_tasks = list(filter(lambda task: task.type == 'off', batch))
        if off_tasks:
            off_task = off_tasks[0]

            vm_costs_for_task = [DISALLOWED] * len(batch)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(self.vms):
                bool, cost, assign_info = self.calcVmAllocationCost(off_task, vm)
                if (self.criteria.optimization_criteria == "min" and cost < 1000000000 or
                        self.criteria.optimization_criteria == "max" and cost > -1000000000):
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
            vm = self.vms[column]
            pairs.append((task, vm))

        return pairs



    ########## PAIRING and LOGGING ##########
    def applyPairings(self, pairs):
        for pair in pairs:
            if pair[0].type == 'off' and pair[1].status == 'open':
                continue
            elif pair[0].type == 'task' and pair[1].status == 'open':
                pair[1].setStatus('active')
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
                                         'task_allocation_start': pair[0].allocation_start, 'task_allocation_end': pair[0].allocation_end,
                                         'vm_output_time': pair[0].vm_output_time, 'vm_end': pair[0].vm_allocation_end,
                                         'allocation_cost': pair[0].allocation_cost - 1, 'idle_time': pair[0].idle_time},
                                        ignore_index=True)



    ########## ALLOCATION BATCHES (VMA ALGORITHM) ##########
    def allocateBatch(self, batch):
        # prepare tasks and vms for matching
        batch = self.prepareVmMatchings(batch, additional_vms_num=len(batch))
        # calc allocation costs for matches (munkres algorithm)
        pairings = self.calcMinCostPairings(batch)
        # pairing and logging
        self.applyPairings(pairings)

    def vma(self, batches):
        n = len(batches)
        for i, batch in enumerate(batches):
            self.allocateBatch(batch)
            print(f"Batch #{i} out of {n}")

        self.allocateBatch([])

