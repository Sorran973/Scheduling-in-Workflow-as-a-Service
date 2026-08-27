import csv
import random
from copy import deepcopy
from datetime import datetime

import pandas as pd
from fontTools.misc.bezierTools import epsilon

import config
from AllocationModule.AllocationBestFitFTLEPSM import AllocationBestFitFTLEPSM
from AllocationModule.AllocationBestFit import AllocationBestFit
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationASAP import AllocationASAP
from AllocationModule.AllocationBestFitASAP import AllocationBestFitASAP
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.EPSM.AllocationEPSM import AllocationEPSM
from AllocationModule.EPSM.AllocationEPSM_BestFit import AllocationEPSM_BestFit
from AllocationModule.EPSM.AllocationEPSMnew import AllocationEPSMnew
from AllocationModule.EPSM.AllocationNewVM import AllocationNewVM
from AllocationModule.EPSM.AllocationEPSM_VMA import AllocationEPSM_VMA, AllocationEPSM_VMA
from AllocationModule.EPSM.EPSMWorkflow import EPSMWorkflow
from AllocationModule.HEFT.HEFTNode import HEFTNode
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from SchedulingModule.CJM.Model.Criteria import CostCriteria
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from config import *
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer


if __name__ == '__main__':

    # df = pd.DataFrame({'A':list("011122"),
    #                    'B':list("bbbbbb")})
    #
    # s = df.groupby(['A'], as_index=False).size()
    # # s = df.groupby('A').size().reset_index()
    # # s = df.groupby('A').agg('count')
    # # s = df.groupby('A').rename_
    # s.columns = ["A","Count"]

    workflow_samples = config.WORKFLOW_SAMPLES
    vm_types = CSVHandler.read_vms_table(config.VMS_TABLE_FILE_PATH)


    #####################################################
    ################# SCHEDULING MODULE #################
    #####################################################
    n_worfklow = 100
    period = 60
    n_workflow_per_period = 5
    current_time = 0
    # repeat_workflow_set_flag = "new_test"
    repeat_workflow_set_flag = "old_test"
    indexes = []
    starts = []
    task_volume_multiplier_arr = []
    data_volume_multiplier_arr = []
    T_arr = []
    T_arr_new = []
    j = 0
    k = 0

    if repeat_workflow_set_flag == "old_test":
        with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/indexes_arr.csv", newline='') as f:
            reader = csv.reader(f, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                indexes.append(int(row[1]))
                T_arr.append(float(row[2]))
                # T_arr.append(T)
                starts.append(int(row[3]))
                task_volume_multiplier_arr.append(float(row[4]))
                data_volume_multiplier_arr.append(float(row[5]))


    # if T_arr:
    start_time = datetime.now()
    workflow_set = WorkflowSet()
    while n_worfklow > 0:
        if n_worfklow < n_workflow_per_period:
            n_workflow_per_period = n_worfklow
        for i in range(n_workflow_per_period):
            if repeat_workflow_set_flag == "old_test":
                index_workflow_from_samples = indexes[j]
                workflow_type = workflow_samples[index_workflow_from_samples]
                xml_file = config.WORKFLOW_EXAMPLES_DIR + workflow_samples[index_workflow_from_samples].value
                # T = T_arr[j]
                T = config.T
                workflow_start_time = starts[j]
                # task_volume_multiplier = task_volume_multiplier_arr[j]
                # data_volume_multiplier = data_volume_multiplier_arr[j]
                j += 1

            else:
                # index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
                index_workflow_from_samples = i % len(workflow_samples)
                # workflow_start_time = random.randint(current_time, current_time + period)
                workflow_start_time = current_time
                indexes.append(index_workflow_from_samples)
                starts.append(workflow_start_time)
                T = config.T
                workflow_type = workflow_samples[index_workflow_from_samples]
                workflow_type_str = workflow_type.value
                xml_file = config.WORKFLOW_EXAMPLES_DIR + workflow_type_str

            # ------------------------------------------------------------------------------------------------------------------
            if workflow_type in (EnumWorkflow.MONTAGE50, EnumWorkflow.MONTAGE100, EnumWorkflow.MONTAGE200,
                                 EnumWorkflow.MONTAGE300, EnumWorkflow.MONTAGE400, EnumWorkflow.MONTAGE500):
                task_volume_multiplier = 6.5
                data_volume_multiplier = 65
            # ------------------------------------------------------------------------------------------------------------------
            if workflow_type in (EnumWorkflow.CYBERSHAKE50, EnumWorkflow.CYBERSHAKE100, EnumWorkflow.CYBERSHAKE200,
                                 EnumWorkflow.CYBERSHAKE300, EnumWorkflow.CYBERSHAKE400, EnumWorkflow.CYBERSHAKE500):
                task_volume_multiplier = 6
                data_volume_multiplier = 0.8
            # ------------------------------------------------------------------------------------------------------------------
            if workflow_type in (EnumWorkflow.LIGO50, EnumWorkflow.LIGO100, EnumWorkflow.LIGO200,
                                 EnumWorkflow.LIGO300, EnumWorkflow.LIGO400, EnumWorkflow.LIGO500):
                task_volume_multiplier = 1.2
                data_volume_multiplier = 180
            # ------------------------------------------------------------------------------------------------------------------
            if workflow_type in (EnumWorkflow.SIPHT50, EnumWorkflow.SIPHT100, EnumWorkflow.SIPHT200,
                                 EnumWorkflow.SIPHT300, EnumWorkflow.SIPHT400, EnumWorkflow.SIPHT500):
                task_volume_multiplier = 0.16
                data_volume_multiplier = 19
            # ------------------------------------------------------------------------------------------------------------------
            if workflow_type in (EnumWorkflow.GENOME50, EnumWorkflow.GENOME100, EnumWorkflow.GENOME200,
                                 EnumWorkflow.GENOME300, EnumWorkflow.GENOME400, EnumWorkflow.GENOME500):
                task_volume_multiplier = 0.18
                data_volume_multiplier = 7
            # ------------------------------------------------------------------------------------------------------------------


            workflow = EPSMWorkflow(XML_FILE=xml_file,
                                    T=T,
                                    vm_types=vm_types,
                                    criteria=CJM_CRITERIA,
                                    task_volume_multiplier=task_volume_multiplier,
                                    data_volume_multiplier=data_volume_multiplier,
                                    # start_time=random.randint(current_time, current_time + period))
                                    # start_time= period * k)
                                    start_time=workflow_start_time)

            # k += 1
            workflow_set.addEPSMWorkflow(workflow)
            T_arr_new.append(workflow.T)
            task_volume_multiplier_arr.append(task_volume_multiplier)
            data_volume_multiplier_arr.append(data_volume_multiplier)

        current_time += period
        n_worfklow -= n_workflow_per_period

    end_time = datetime.now()
    preprocessing_time_cpc = end_time - start_time

    # if repeat_workflow_set_flag == "new_test":
    # with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/indexes_arr.csv", 'w') as f:
    #     fieldnames = ['workflow_id', 'index_in_sample', 'T', 'start_time', 'task_volume_multiplier', 'data_volume_multiplier']
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #
    #     for i, index in enumerate(indexes):
    #         row = {fieldnames[0]: i,
    #                fieldnames[1]: index,
    #                fieldnames[2]: T_arr_new[i],
    #                fieldnames[3]: starts[i],
    #                fieldnames[4]: task_volume_multiplier_arr[i],
    #                fieldnames[5]: data_volume_multiplier_arr[i]}
    #         writer.writerow(row)


    drawer: Drawer = PyvisDrawer()
    # drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer_graph: Drawer = GraphvizDrawer()
    # drawer_graph.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer.draw_gantt(workflow_set.drawn_nodes)
    # drawer.draw_new_gantt(workflow_set.drawn_nodes)

    #####################################################
    ################# ALLOCATION MODULE #################
    #####################################################
    tasks = CSVHandler.read_task_time_table(config.TASK_TIME_TABLE_FILE)
    workload_start_time = tasks[0].start
    workload_end_time = max(tasks, key=lambda task: task.end).end
    print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    data_transfer = CSVHandler.read_data_transfer_table(config.TRANSFER_SIZE_TABLE_FILE, tasks)

    T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))


    allocations = []
    # allocations.append(AllocationEPSMnew(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationEPSM_BestFit(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationNewVM(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationEPSM_VMA(VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationEPSM(VMA_CRITERIA, vm_types, deepcopy(tasks)))


    batch_time_epsm = 0
    batch_time_new_vm = 0

    vma_time_epsm = 0
    vma_time_new_vm = 0

    for allocation in allocations:
        time = 0
        start_time = datetime.now()
        batches = allocation.formParallelBatches(time)
        end_time = datetime.now()
        allocation.batches_size = len(batches)
        batch_time = end_time - start_time

        if isinstance(allocation, AllocationEPSM):
            # drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_EPSM)
            batch_time_epsm = batch_time
        if isinstance(allocation, AllocationNewVM):
            # drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)
            batch_time_new_vm = batch_time

        start_time = datetime.now()
        allocation.vma(batches)
        end_time = datetime.now()
        vma_time = end_time - start_time


        if isinstance(allocation, AllocationEPSM_BestFit):
            vma_time_epsm = vma_time
        if isinstance(allocation, AllocationNewVM):
            vma_time_new_vm = vma_time


        Analyzer.analyze_allocation(allocation, T_arr)


    Analyzer.print_comparison_table(allocations)

    print('Duration of preprocessing (CPC): {}'.format(preprocessing_time_cpc))

    print('Duration of vma (EPSM): {}'.format(vma_time_epsm))
    print('Duration of vma (NewVM): {}'.format(vma_time_new_vm))

    #####################################################
    ################# DRAWING GANTT PLOTS ###############
    #####################################################
    for allocation in allocations:
        if isinstance(allocation, AllocationEPSM):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            # drawer.draw_big_gantt(log, GANTT_FIGURES_EPSM)
            print("EPSM dif = " + str(allocation.different_workflow_reuse_vm_counter))
        if isinstance(allocation, AllocationNewVM):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            # drawer.draw_big_gantt(log, GANTT_FIGURES_NEW_VM_FOR_EACH)
        # if isinstance(allocation, AllocationNewVM):
        #     log = allocation.log
        #     color = log[["workflow_id"]]
        #     color = color.drop_duplicates()
        #     color["color"] = color.apply(lambda x: rand_color(x), axis=1)
        #     log = pd.merge(log, color, on='workflow_id', how='left')
        #     log = log.sort_values(["vm_id", "vm_start"])
        #     # drawer.draw_big_gantt(log, GANTT_FIGURES_NEW_VM_FOR_EACH)
        #     print("EPSM_VMA dif = " + str(allocation.different_workflow_reuse_vm_counter))


    ftl_workflow_costs = []
    asap_workflow_costs = []

    with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/ftl_workflow_costs.csv", newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        headers = next(reader)
        for row in reader:
            ftl_workflow_costs.append(int(row[1]))

    with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/asap_workflow_costs.csv", newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        headers = next(reader)
        for row in reader:
            asap_workflow_costs.append(int(row[1]))

    ftl_counter = 0
    asap_counter = 0
    for i, cost in enumerate(allocations[0].workflow_costs):
        if ftl_workflow_costs[i] < cost:
            ftl_counter += 1
        if asap_workflow_costs[i] < cost:
            asap_counter += 1

    print("Num of FTL < EPSM: " + str(ftl_counter))
    print("Num of ASAP < EPSM: " + str(asap_counter))



