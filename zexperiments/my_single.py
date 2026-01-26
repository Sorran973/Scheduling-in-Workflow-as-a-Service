import csv
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

    workflow_type = EnumWorkflow.MONTAGE50

    workflow_type_str = workflow_type.value
    # workflow_type = None
    # workflow_type_str = "MyTestDAXes/test.xml"
    # task_volume_multiplier = 1
    # data_volume_multiplier = 10
    xml_file = WORKFLOW_EXAMPLES_DIR + workflow_type_str

    # ------------------------------------------------------------------------------------------------------------------
    if workflow_type in (EnumWorkflow.MONTAGE50, EnumWorkflow.MONTAGE100, EnumWorkflow.MONTAGE200,
                         EnumWorkflow.MONTAGE300, EnumWorkflow.MONTAGE400, EnumWorkflow.MONTAGE500):
        task_volume_multiplier = 12
        data_volume_multiplier = 150
    # ------------------------------------------------------------------------------------------------------------------
    if workflow_type in (EnumWorkflow.CYBERSHAKE50, EnumWorkflow.CYBERSHAKE100, EnumWorkflow.CYBERSHAKE200,
                         EnumWorkflow.CYBERSHAKE300, EnumWorkflow.CYBERSHAKE400, EnumWorkflow.CYBERSHAKE500):
        task_volume_multiplier = 16
        data_volume_multiplier = 0.4
    # ------------------------------------------------------------------------------------------------------------------
    if workflow_type in (EnumWorkflow.LIGO50, EnumWorkflow.LIGO100, EnumWorkflow.LIGO200,
                         EnumWorkflow.LIGO300, EnumWorkflow.LIGO400, EnumWorkflow.LIGO500):
        task_volume_multiplier = 3
        data_volume_multiplier = 70
    # ------------------------------------------------------------------------------------------------------------------
    if workflow_type in (EnumWorkflow.SIPHT50, EnumWorkflow.SIPHT100, EnumWorkflow.SIPHT200,
                         EnumWorkflow.SIPHT300, EnumWorkflow.SIPHT400, EnumWorkflow.SIPHT500):
        task_volume_multiplier = 0.16
        data_volume_multiplier = 10
    # ------------------------------------------------------------------------------------------------------------------
    if workflow_type in (EnumWorkflow.GENOME50, EnumWorkflow.GENOME100, EnumWorkflow.GENOME200,
                         EnumWorkflow.GENOME300, EnumWorkflow.GENOME400, EnumWorkflow.GENOME500):
        task_volume_multiplier = 0.014
        data_volume_multiplier = 1.5
    # ------------------------------------------------------------------------------------------------------------------

    workflow_set = WorkflowSet()
    workflow = Workflow(XML_FILE=xml_file,
                        T=T,
                        vm_types=vm_types,
                        criteria=CJM_CRITERIA,
                        task_volume_multiplier=task_volume_multiplier,
                        data_volume_multiplier=data_volume_multiplier,
                        start_time=0)

    # workflow2 = Workflow(XML_FILE=xml_file,
    #                      T=T,
    #                      vm_types=vm_types,
    #                      criteria=CJM_CRITERIA,
    #                      task_volume_multiplier=task_volume_multiplier,
    #                      data_volume_multiplier=data_volume_multiplier,
    #                      start_time=700)

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
    allocations.append(AllocationASAP(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    #
    # allocations.append(AllocationASAP_O(VMA_CRITERIA, vm_types, deepcopy(tasks)))



    for allocation in allocations:
        time = 0
        batches = allocation.formParallelBatches(time)
        allocation.batches_size = len(batches)


        if isinstance(allocation, AllocationFTL):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_FTL)
        if isinstance(allocation, AllocationASAP_O):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_ASAP_O)
        if isinstance(allocation, AllocationASAP):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_ASAP)
        if isinstance(allocation, NewVmForEachTask):
            drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)

        allocation.vma(batches)


    #####################################################
    ###################### ANALYZING ####################
    #####################################################
    T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    for allocation in allocations:
        Analyzer.analyze_allocation(allocation, T_arr)

    Analyzer.print_comparison_table(allocations)


    #####################################################
    workflow_costs = allocations[0].workflow_costs
    with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/ftl_workflow_costs.csv", 'w') as f:
        fieldnames = ['workflow_id', 'allocation_cost']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, cost in enumerate(workflow_costs):
            row = {fieldnames[0]: i,
                   fieldnames[1]: cost}
            writer.writerow(row)

    a = 0

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
            # drawer.draw_big_gantt(log, GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationASAP_O):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            # drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP_O)
            drawer.draw_big_gantt(log, GANTT_FIGURES_ASAP_O)
        if isinstance(allocation, AllocationASAP):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP)
            # drawer.draw_big_gantt(log, GANTT_FIGURES_ASAP)
