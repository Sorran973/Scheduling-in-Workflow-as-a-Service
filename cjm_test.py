import csv
import random
from copy import deepcopy
from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.AllocationModule import AllocationModule
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from SchedulingModule.CJM.Model.Criteria import TimeCriteria, CostCriteria
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from SchedulingModule.CJM.WorkflowTest import WorkflowTest

import Utils.Configuration
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer



if __name__ == '__main__':
    # vm_types = CSVHandler.read_vms_table(Utils.Configuration.VMS_TABLE_FILE)
    vm_types = CSVHandler.read_vms_table('/Users/artembulkhak/PycharmProjects/Dissertation/Output/test/processor_table.csv')
    workflow_samples = Utils.Configuration.WORKFLOW_SAMPLES


    workflow_set = WorkflowSet()
    # T = None
    T = 38
    index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)

    # workflow = Workflow(XML_FILE=workflow_samples[index_workflow_from_samples],
    workflow = Workflow(XML_FILE=Utils.Configuration.TEST,
                        T=T,
                        vm_types=vm_types,
                        criteria=CostCriteria(min),
                        task_volume_multiplier=1,
                        data_volume_multiplier=1,
                        start_time=0)

    # workflow2 = Workflow(XML_FILE=Utils.Configuration.LIGO50,
    #                     T=T,
    #                     vm_types=vm_types,
    #                     criteria=CostCriteria(min),
    #                     task_volume_multiplier=1,
    #                     data_volume_multiplier=1,
    #                     start_time=1000)

    start_time = datetime.now()
    workflow_set.addWorkflow(workflow)
    end_time = datetime.now()
    print('Duration of scheduling (CJM): {}'.format(end_time - start_time))
    # workflow_set.addWorkflow(workflow2)

    tasks = CSVHandler.read_task_time_table(Utils.Configuration.TASK_TIME_TABLE_FILE)
    workload_start_time = tasks[0].start
    workload_end_time = max(tasks, key=lambda task: task.end).end
    print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    data_transfer = CSVHandler.read_data_transfer_table(Utils.Configuration.TRANSFER_SIZE_TABLE_FILE, tasks)


    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)

    allocations = []
    allocations.append(AllocationFTL(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationModule(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationMixed(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(NewVmForEachTask(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))

    for allocation in allocations:
        time = 0
        batches = allocation.formParallelBatches(time)

        # N_pc = 0
        # for b in range(0, len(batches)-1):
        #     for task in batches[b]:
        #         for data_transfer in task.output_transfers:
        #             for next_task in batches[b+1]:
        #                 if next_task.id == data_transfer.task_to.id:
        #                     N_pc += 1
        #                     print(str(task.id) + "-->" + str(next_task.id))
        #                     break



        if isinstance(allocation, AllocationModule) or isinstance(allocation, AllocationFTL):
            drawer.draw_batches_gantt(allocation.tasks)
        else:
            drawer.draw_batches_gantt_for_mixed(allocation.tasks)


        allocation.vma(batches)


    #####################################################
    ###################### ANALYZING ####################
    #####################################################
    T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    for allocation in allocations:
        Analyzer.analyze_allocation(allocation, T_arr)


    Analyzer.print_comparison_table(allocations)


    #####################################################
    ################# DRAWING GANTT PLOTS ###############
    #####################################################
    for allocation in allocations:
        if isinstance(allocation, AllocationFTL):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationModule):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_ASAP)
        if isinstance(allocation, AllocationMixed):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_ASAP_MOD)
        if isinstance(allocation, NewVmForEachTask):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_NEW_VM_FOR_EACH)