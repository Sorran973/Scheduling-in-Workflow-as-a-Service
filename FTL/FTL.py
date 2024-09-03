import sys

import numpy as np


class FTL:

    def __init__(self, vm_types, tasks):
        self.vm_type = vm_types
        self.tasks = tasks

        vm_counter = 0
        time = 0
        self.batches = self.formParallelBatches(time)

        batches = list(tasks.batch.unique())

        for batch_num in batches:
            self.scheduleBatch(batch_num)

        print(vms_log.allocation_cost.sum())



    def clearTasksFromOff(self, batch):
        return list(filter(lambda task: task.type is not 'Off', batch))

    def getActiveVms(self, vms):
        return list(filter(lambda vm: vm. not in self.tasks, vms))
        return vms[vms.vm_status == 'active']

    def prepareVmMatchings(self, batch, additional_vms_num=0, vm_perf_factor=1):
        # first remove old temp tasks and not started vms
        if not batch.empty:
            batch = clearTasksFromOff(batch)
        if not vms.empty:
            vms = getActiveVms(vms)

        vms_to_add = 0

        # add vms or off-tasks to match each other
        diff = len(batch) - len(vms)
        if diff > 0:
            vms_to_add = vms_to_add + diff
        elif diff < 0:
            batch = addOffTasks(batch, -diff)

        # add additional vms and tasks for more optimization options
        if additional_vms_num > 0:
            vms_to_add = vms_to_add + additional_vms_num
            batch = addOffTasks(batch, additional_vms_num, len(batch) + 1)  # use len(batch) + 1 to avoid name collisions

        if vms_to_add > 0:
            vms = addNewVmsRandomly(vms, vm_types, vms_to_add, vm_perf_factor)

        # pair all
        vms['key'] = 1
        batch['key'] = 1
        matching = pd.merge(batch, vms, on='key', suffixes=("_task", "_vm"))

        return matching

    def scheduleBatch(self, batch_num):
        global INCREASE_IN_PERF_NUMBER

        batch = list(filter(lambda task: task.batch == batch_num, self.tasks))

        # schedule one batch with increasing vms perf each retry
        retry_counts = 10
        vm_perf_factor = 1
        pairings = {}
        while retry_counts > 1:
            try:
                additional_vms_num = 5 if vm_perf_factor <= 100 else len(batch)
                matchings = prepareVmMatchings(batch, additional_vms_num, vm_perf_factor)
                print("Global Time: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                print("Matchings Size: {} VMs Size: {}".format(len(matchings), len(vms)))
                calcAllocationCosts(matchings)
                pairings = calculateMinCostPairingsThreaded(matchings)
                break
            except Exception:
                # print(matchings[["task", 'volume', "vm_id", 'perf', "allocation_cost", 'start', 'end,' 'task_start', 'task_end']])
                retry_counts = retry_counts - 1
                vm_perf_factor += 1
                if vm_perf_factor == 4:
                    vm_perf_factor = 100
                print("New vm_perf_factor: {}".format(vm_perf_factor))
                INCREASE_IN_PERF_NUMBER = INCREASE_IN_PERF_NUMBER + 1

        # print(pairings[["task", 'volume', "vm_id", "allocation_cost", 'vm_start', 'task_start', 'task_end', 'vm_end', "pairing"]])
        tasks, vms = applyPairings(pairings, tasks, vms)


    def formParallelBatches(self, time):
        batch_num = 0
        leader_vm_type = max(self.vm_type, key=lambda vm_type: vm_type.perf)
        self.calcTimingsForVM(leader_vm_type)

        while len(list(filter(lambda i: i.status is None, self.tasks))) != 0:
            time = self.assignToLeader(time, batch_num)
            batch_num += 1

        return batch_num


    def calcTimingsForVM(self, vm_type):
        for task in self.tasks:
            task.calc_time = task.volume / vm_type.perf
            task.latest_start = task.end - task.calc_time
            task.earliest_finish = task.start + task.calc_time

    def assignToLeader(self, time, batch_num):
        ttasks = list(filter(lambda i: i.status is None, self.tasks))

        EFT = sys.maxsize
        for task in ttasks:
            if task.status is None:
                task.possible_start = np.maximum(task.start, time)
                task.earliest_finish = task.possible_start + task.calc_time
                EFT = task.earliest_finish if task.earliest_finish < EFT else EFT


        for task in ttasks:
            if task.status is None:
                if task.earliest_finish == EFT:
                    task.status = "Leader"
                    task.batch = batch_num
                    task.finish_time = EFT
                    continue
                if task.latest_start < EFT:
                    task.status = "Batch"
                    task.batch = batch_num
                    task.finish_time = EFT

        return EFT