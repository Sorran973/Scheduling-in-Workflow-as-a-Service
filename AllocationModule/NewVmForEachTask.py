import math
import random
import sys
from datetime import datetime

import pandas as pd
from munkres import Munkres, print_matrix, DISALLOWED, make_cost_matrix

from AllocationModule.Model.PossibleAssignment import PossibleAssignment
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VM import VM
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Model.Criteria import CostCriteria, TimeCriteria
from SchedulingModule.CJM.Workflow import round_up


class NewVmForEachTask:
    def __init__(self, criteria, vm_types, tasks):
        self.vm_types = vm_types
        self.tasks = tasks
        self.num_workflows = self.tasks[-1].workflow_id + 1
        self.cost_of_workflow = [0 for workflow_id in range(self.num_workflows)]
        self.vms = []
        self.criteria = criteria
        self.log = pd.DataFrame(columns=['workflow_id', 'vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
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

        self.map_vm_perf_for_transfer = None
        self.create_vm_for_transfer()



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

    def assignToLeaderNew(self, tasks, time, batches):
        batch = []
        EFT = sys.maxsize
        for task in tasks:
            task.possible_start = max(task.start, time)
            task.earliest_finish = task.possible_start + task.calc_time
            a = task.earliest_finish
            EFT = task.earliest_finish if task.earliest_finish < EFT else EFT

        for task in tasks:
            if (list(filter(lambda transfer: transfer.task_from.status is None, task.input_transfers))
                    or task.possible_start >= EFT):
                continue
            else:
                task.batch = len(batches)
                batch.append(task)

        for task in batch:
            task.status = 'Batch'

        batches.append(batch)

        return EFT

    def formParallelBatches(self, time):
        # batches = []
        # leader_vm_type = max(self.vm_types, key=lambda vm_type: vm_type.perf)
        # self.calcTimingsForVM(leader_vm_type)
        # tasks_with_none_status = list(filter(lambda i: i.status is None, self.tasks))

        ## while tasks_with_none_status:
        ##     time = self.assignToLeader(tasks_with_none_status, time, batches)
        ##     tasks_with_none_status = list(filter(lambda i: i.status is None, tasks_with_none_status))

        # while tasks_with_none_status:
        #     time = self.assignToLeaderNew(tasks_with_none_status, time, batches)
        #     tasks_with_none_status = list(filter(lambda i: i.status is None, tasks_with_none_status))

        batches = []
        leader_vm_type = max(self.vm_types, key=lambda vm_type: vm_type.perf)
        self.calcTimingsForVM(leader_vm_type)

        workflows = list(map(
            lambda i: list(filter(lambda task: task.workflow_id == i, self.tasks)),
            range(self.num_workflows)
        ))

        for workflow in workflows:
            tasks_with_none_status = list(filter(lambda i: i.status is None, workflow))
            while tasks_with_none_status:
                time = self.assignToLeaderNew(tasks_with_none_status, time, batches)
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
                               vm_type.cost,
                               vm_type.prep_time,
                               vm_type.shutdown_time))

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
        if task.id == 99:
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
                for transfer in previous_task.output_transfers:
                    task_to = transfer.task_to
                    # transfer_time = transfer.transfer_time
                    transfer_time = round(transfer.transfer_time * self.map_vm_perf_for_transfer[vm.perf])
                    transfer_end = previous_task.allocation_end + transfer_time

                    # meaning time between the time vm can be stopped and it finishes the longest data transfer
                    if output_data_transfer_time_max < (transfer_end - possible_vm_start):
                        output_data_transfer_time_max = transfer_end - possible_vm_start

                if output_data_transfer_time_max < 0:
                    y = 0
                output_data_transfer_time_max = max(output_data_transfer_time_max, 0)  # can't be negative
                shutdown_time = shutdown_time + output_data_transfer_time_max
                output_data_transfer_time = output_data_transfer_time_max

        # if perform calculations
        else:
            task_runtime = math.ceil(task.volume / vm.perf)
            preparation_time += vm.prep_time  # add vm startup time

            # calculate additional preparation time to copy required input data
            earliest_data_ready_time_max = -sys.maxsize
            data_transfer_time_max = -sys.maxsize

            if task.input_transfers:
                #TODO: ? create node_edges and data_center_edges and check their times
                for transfer in task.input_transfers:
                    task_from = transfer.task_from
                    transfer_time = round(transfer.transfer_time * self.map_vm_perf_for_transfer[vm.perf])
                    transfer_time1 = round(transfer.transfer_size / vm.perf)

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
            # possible_task_start = min(task.start, earliest_data_ready_time_max)
            possible_task_start = earliest_data_ready_time_max

        vm_runtime = preparation_time + task_runtime + shutdown_time

        expected_vm_start = max(possible_vm_start, possible_task_start - preparation_time)
        expected_vm_end = expected_vm_start + vm_runtime
        if (vm.status != 'open'):
            # idle time between previous assignment and new assignment
            idle_time = (expected_vm_start - possible_vm_start)

        expected_task_start = expected_vm_start + preparation_time
        expected_task_end = expected_task_start + task_runtime

        possible_assignment = PossibleAssignment(vm)

        if expected_task_end > task.end and task.type == 'task':
            allocation_cost = 10000000000  # can't execute task
        else:
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
        off_vms = self.vms.copy()
        new_vms = []
        pairs = []
        off_tasks = list(filter(lambda task: task.type == 'off', batch))

        cost_matrix = []
        for i, task in enumerate(batch):
            if task.type == 'task':
                if task.id == 1:
                    y = 0
                possible_vms = [vm for vm in task.possible_vms if self.calcVmAllocationCost(task, vm)[0]]
                task.possible_vms = possible_vms

                try:
                    if (self.criteria.optimization_criteria == "min"):
                        assignment_with_min_cost = min(task.possible_assignments, key=lambda possible_assignment: possible_assignment.allocation_cost)
                    else:
                        assignment_with_min_cost = max(task.possible_assignments, key=lambda possible_assignment: possible_assignment.allocation_cost)
                except:
                    print("Task(id={}, name={})".format(task.id, task.name))

                # min_cost = assignment_with_min_cost.allocation_cost
                vm = assignment_with_min_cost.assigned_vm
                pairs.append((task, vm))
        #         new_vms.append(vm)
        #
        #         vm_costs_for_task = [DISALLOWED] * (len(batch) - len(off_tasks))
        #         vm_costs_for_task[i] = min_cost
        #         cost_matrix.append(vm_costs_for_task)
        #
        # m = Munkres()
        # result = m.compute(cost_matrix)
        #
        # for row, column in result:
        #     task = batch[row]
        #     vm = new_vms[column]
        #     pairs.append((task, vm))


        # calc costs of off tasks
        cost_matrix = []
        if off_tasks:
            off_task = off_tasks[0]

            vm_costs_for_task = [DISALLOWED] * len(off_tasks)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(off_vms):
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

            for row, column in result:
                task = off_tasks[row]
                vm = off_vms[column]
                pairs.append((task, vm))

        return pairs

    def calcMinTimePairings(self, batch):
        off_vms = self.vms.copy()
        new_vms = []
        pairs = []
        off_tasks = list(filter(lambda task: task.type == 'off', batch))

        time_matrix = []
        for i, task in enumerate(batch):
            if task.type == 'task':
                if task.id == 1:
                    y = 0
                possible_vms = [vm for vm in task.possible_vms if self.calcVmAllocationCost(task, vm)[0]]
                task.possible_vms = possible_vms

                try:
                    if (self.criteria.optimization_criteria == "min"):
                        assignment_with_min_time = min(task.possible_assignments, key=lambda possible_assignment: possible_assignment.task_allocation_end)
                    else:
                        assignment_with_min_time = max(task.possible_assignments, key=lambda possible_assignment: possible_assignment.task_allocation_end)
                except:
                    print("Task(id={}, name={})".format(task.id, task.name))

                # min_cost = assignment_with_min_cost.allocation_cost
                vm = assignment_with_min_time.assigned_vm
                pairs.append((task, vm))
        #         new_vms.append(vm)
        #
        #         vm_costs_for_task = [DISALLOWED] * (len(batch) - len(off_tasks))
        #         vm_costs_for_task[i] = min_cost
        #         cost_matrix.append(vm_costs_for_task)
        #
        # m = Munkres()
        # result = m.compute(cost_matrix)
        #
        # for row, column in result:
        #     task = batch[row]
        #     vm = new_vms[column]
        #     pairs.append((task, vm))

        # calc costs of off tasks
        time_matrix = []
        if off_tasks:
            off_task = off_tasks[0]

            vm_times_for_task = [DISALLOWED] * len(off_tasks)
            possible_assignments_for_off_tasks = []
            for i, vm in enumerate(off_vms):
                res = self.calcVmAllocationCost(off_task, vm)
                if res[0]:
                    vm_times_for_task[i] = res[2].task_allocation_end
                    possible_assignments_for_off_tasks.append(res[2])
            time_matrix.append(vm_times_for_task)

            for i in range(1, len(off_tasks)):
                off_tasks[i].possible_assignments = possible_assignments_for_off_tasks
                time_matrix.append(vm_times_for_task)

            m = Munkres()
            result = m.compute(time_matrix)

            for row, column in result:
                task = off_tasks[row]
                vm = off_vms[column]
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
                                         'allocation_cost': pair[0].allocation_cost - 1, 'idle_time': pair[0].idle_time, 'vm_status': pair[1].status},
                                        ignore_index=True)



    ########## ALLOCATION BATCHES (VMA ALGORITHM) ##########
    def allocateBatch(self, batch):
        # prepare tasks and vms for matching
        batch = self.prepareVmMatchings(batch, additional_vms_num=len(batch))
        # calc allocation costs for matches (munkres algorithm)
        if isinstance(self.criteria, CostCriteria):
            pairings = self.calcMinCostPairings(batch)
        elif isinstance(self.criteria, TimeCriteria):
            pairings = self.calcMinTimePairings(batch)
        # pairing and logging
        self.applyPairings(pairings)

    def vma(self, batches):
        n = len(batches)
        for i, batch in enumerate(batches):
            self.allocateBatch(batch)
            print(f"Batch #{i} out of {n}")

        self.allocateBatch([])


    def create_vm_for_transfer(self):
        n = len(self.vm_types)
        vm_for_transfer = list(reversed(self.vm_types))
        self.map_vm_perf_for_transfer = {}
        for i, vm in enumerate(self.vm_types):
            self.map_vm_perf_for_transfer[vm.perf] = vm_for_transfer[i].perf

