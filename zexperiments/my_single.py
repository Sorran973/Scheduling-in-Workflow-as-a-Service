import random
from copy import deepcopy
from datetime import datetime

import pandas as pd

from AllocationModule.AllocationASAP_O import AllocationASAP_O
from AllocationModule.AllocationBestFitASAPEPSM import AllocationBestFitASAPEPSM
from AllocationModule.AllocationBestFitFTLEPSM import AllocationBestFitFTLEPSM
from AllocationModule.AllocationBestFit import AllocationBestFit
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationASAP import AllocationASAP
from AllocationModule.AllocationBestFitASAP import AllocationBestFitASAP
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.EPSM.AllocationEPSM_Batch_BestFit import AllocationEPSM_Batch_BestFit
from AllocationModule.EPSM.EPSMWorkflow import EPSMWorkflow
from AllocationModule.HEFT.HEFTNode import HEFTNode
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from SchedulingModule.CJM.Model.Criteria import CostCriteria
from SchedulingModule.CJM.Model.Node import Node
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from config import *
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer

# T = 839
# Task(id=94, name=ID00093)

if __name__ == '__main__':

    vm_types = CSVHandler.read_vms_table(VMS_TABLE_FILE_PATH)

    task_volume_multiplier = 1
    # transfer_volume_ = 1

    workflow_type = EnumWorkflow.CYBERSHAKE50

    if workflow_type in (EnumWorkflow.GENOME50, EnumWorkflow.GENOME100, EnumWorkflow.GENOME200,
                         EnumWorkflow.GENOME300, EnumWorkflow.GENOME400, EnumWorkflow.GENOME500):
        task_volume_multiplier = 0.1

    # workflow_type_str = workflow_type.value
    workflow_type_str = "MyTestDAXes/test.xml"
    xml_file = WORKFLOW_EXAMPLES_DIR + workflow_type_str

    workflow_set = WorkflowSet()
    workflow = Workflow(XML_FILE=xml_file,
                        T=T,
                        vm_types=vm_types,
                        criteria=CJM_CRITERIA,
                        task_volume_multiplier=task_volume_multiplier,
                        data_volume_multiplier=1,
                        start_time=0)

    # workflow2 = Workflow(XML_FILE=xml_file,
    #                      T=T,
    #                      vm_types=vm_types,
    #                      criteria=CJM_CRITERIA,
    #                      task_volume_multiplier=task_volume_multiplier,
    #                      data_volume_multiplier=1,
    #                      start_time=10)

    start_time = datetime.now()
    workflow_set.addWorkflow(workflow)
    # workflow_set.addWorkflow(workflow2)
    end_time = datetime.now()
    print('Duration of scheduling (CJM): {}'.format(end_time - start_time))

    tasks = CSVHandler.read_task_time_table(TASK_TIME_TABLE_FILE)
    workload_start_time = tasks[0].start
    workload_end_time = max(tasks, key=lambda task: task.end).end
    print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    data_transfer = CSVHandler.read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks)


    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)

    allocations = []
    # allocations.append(AllocationBestFit(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationBestFitASAP(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationBestFitFTLEPSM(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationBestFitASAPEPSM(VMA_CRITERIA, vm_types, deepcopy(tasks)))

    allocations.append(AllocationFTL(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationASAP_O(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(NewVmForEachTask(VMA_CRITERIA, vm_types, deepcopy(tasks)))

    #---------
    # Node.id = 0
    # workflow_set = WorkflowSet()
    # workflow = EPSMWorkflow(XML_FILE=xml_file,
    #                         T=T,
    #                         vm_types=vm_types,
    #                         criteria=CJM_CRITERIA,
    #                         task_volume_multiplier=task_volume_multiplier,
    #                         data_volume_multiplier=1,
    #                         start_time=0)
    #
    # start_time = datetime.now()
    # workflow_set.addEPSMWorkflow(workflow)
    # end_time = datetime.now()
    # print('Duration of scheduling (EPSM): {}'.format(end_time - start_time))
    #
    # tasks = CSVHandler.read_task_time_table(TASK_TIME_TABLE_FILE)
    # workload_start_time = tasks[0].start
    # workload_end_time = max(tasks, key=lambda task: task.end).end
    # print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    # data_transfer = CSVHandler.read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks)
    #
    # allocations.append(AllocationEPSM_Batch_BestFit(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # #---------

    for allocation in allocations:
        time = 0
        batches = allocation.formParallelBatches(time)
        allocation.batches_size = len(batches)

        N_pc = 0
        for b in range(0, len(batches)-1):
            for task in batches[b]:
                for data_transfer in task.output_transfers:
                    for next_task in batches[b+1]:
                        if next_task.id == data_transfer.task_to.id:
                            N_pc += 1
                            # print(str(task.id) + "-->" + str(next_task.id))
                            break
        print("N_pc: " + str(N_pc))


        if isinstance(allocation, AllocationFTL):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_FTL)
        if isinstance(allocation, AllocationASAP_O):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_ASAP_O)
        if isinstance(allocation, NewVmForEachTask):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)

        allocation.vma(batches)





    #####################################################
    ################# DRAWING GANTT PLOTS ###############
    #####################################################
    for allocation in allocations:
        if isinstance(allocation, AllocationBestFit):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, GANTT_FIGURES_BEST_FIT)
        if isinstance(allocation, AllocationBestFitASAP):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, GANTT_FIGURES_FIRST_FIT)
        if isinstance(allocation, AllocationBestFitFTLEPSM):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, GANTT_FIGURES_FIRST_FIT)
        if isinstance(allocation, AllocationBestFitASAPEPSM):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, GANTT_FIGURES_FIRST_FIT)

        if isinstance(allocation, AllocationFTL):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationASAP_O):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP_O)
        if isinstance(allocation, NewVmForEachTask):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            drawer.draw_result_gantt(log, GANTT_FIGURES_NEW_VM_FOR_EACH)

    #####################################################
    ###################### ANALYZING ####################
    #####################################################
    T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    for allocation in allocations:
        Analyzer.analyze_allocation(allocation, T_arr)


    Analyzer.print_comparison_table(allocations)

    a = 0