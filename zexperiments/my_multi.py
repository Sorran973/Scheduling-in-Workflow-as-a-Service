import csv
import random
from copy import deepcopy
from datetime import datetime

import pandas as pd

import config
from AllocationModule.AllocationASAP_O import AllocationASAP_O
from AllocationModule.AllocationBestFit import AllocationBestFit
from AllocationModule.AllocationBestFitASAPEPSM import AllocationBestFitASAPEPSM
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationBestFitASAP import AllocationBestFitASAP
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.AllocationBestFitFTLEPSM import AllocationBestFitFTLEPSM
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from SchedulingModule.CJM.Model.EnumWorkflow import EnumWorkflow
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from AllocationModule.AllocationASAP import AllocationASAP
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
    n_worfklow = 500
    period = 900
    n_workflow_per_period = 50
    current_time = 0
    task_volume_multiplier = 1
    data_volume_multiplier = 1
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
                # T_arr.append(float(row[2]))
                T_arr.append(config.T)
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
                index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
                # index_workflow_from_samples = i
                # workflow_start_time = random.randint(current_time, current_time + period)
                workflow_start_time = current_time
                indexes.append(index_workflow_from_samples)
                starts.append(workflow_start_time)
                T = config.T
                workflow_type = workflow_samples[index_workflow_from_samples]
                workflow_type_str = workflow_type.value
                xml_file = config.WORKFLOW_EXAMPLES_DIR + workflow_type_str

            # 50, 100, 500 норм
            if workflow_type in (EnumWorkflow.MONTAGE50, EnumWorkflow.MONTAGE100, EnumWorkflow.MONTAGE200,
                                 EnumWorkflow.MONTAGE300, EnumWorkflow.MONTAGE400, EnumWorkflow.MONTAGE500):
                # task_volume_multiplier = 44
                # data_volume_multiplier = 7
                task_volume_multiplier = 12
                data_volume_multiplier = 5

            # 50, 100, 500 норм, в других выигрыш либо нулевой, либо вообще отрицательный
            if workflow_type in (EnumWorkflow.CYBERSHAKE50, EnumWorkflow.CYBERSHAKE100, EnumWorkflow.CYBERSHAKE500):
                # task_volume_multiplier = 20
                # data_volume_multiplier = 0.05
                task_volume_multiplier = 17
                data_volume_multiplier = 0.04
            if workflow_type in (EnumWorkflow.CYBERSHAKE200, EnumWorkflow.CYBERSHAKE300, EnumWorkflow.CYBERSHAKE400,
                                 EnumWorkflow.CYBERSHAKE500):
                task_volume_multiplier = 80
                data_volume_multiplier = 1.5
            # ------------------------------------------------------------------------------------------------------------------
            # все норм
            if workflow_type in (EnumWorkflow.LIGO50, EnumWorkflow.LIGO100, EnumWorkflow.LIGO200,
                                 EnumWorkflow.LIGO300, EnumWorkflow.LIGO500):
                task_volume_multiplier = 3
                data_volume_multiplier = 7
                # task_volume_multiplier = 3
                # data_volume_multiplier = 7
            if workflow_type is EnumWorkflow.LIGO400:
                task_volume_multiplier = 8
                data_volume_multiplier = 75
            # ------------------------------------------------------------------------------------------------------------------
            # все хорошо
            if workflow_type in (EnumWorkflow.SIPHT50, EnumWorkflow.SIPHT100):
                # task_volume_multiplier = 1
                # data_volume_multiplier = 5
                task_volume_multiplier = 0.25
                data_volume_multiplier = 0.1
            if workflow_type in (EnumWorkflow.SIPHT200, EnumWorkflow.SIPHT300, EnumWorkflow.SIPHT400,
                                 EnumWorkflow.SIPHT500):
                task_volume_multiplier = 3
                data_volume_multiplier = 50
            # ------------------------------------------------------------------------------------------------------------------
            # все норм
            if workflow_type in (EnumWorkflow.GENOME50, EnumWorkflow.GENOME100):
                # task_volume_multiplier = 0.25
                # data_volume_multiplier = 1
                task_volume_multiplier = 0.013
                data_volume_multiplier = 0.15
            if workflow_type in (EnumWorkflow.GENOME200, EnumWorkflow.GENOME300):
                task_volume_multiplier = 0.4
                data_volume_multiplier = 9
            if workflow_type is EnumWorkflow.GENOME400:
                task_volume_multiplier = 0.8
                data_volume_multiplier = 8
            if workflow_type is EnumWorkflow.GENOME500:
                task_volume_multiplier = 0.2
                data_volume_multiplier = 8


            workflow = Workflow(XML_FILE=xml_file,
                                T=T,
                                vm_types=vm_types,
                                criteria=config.CJM_CRITERIA,
                                task_volume_multiplier=task_volume_multiplier,
                                data_volume_multiplier=data_volume_multiplier,
                                # start_time=random.randint(current_time, current_time + period))
                                # start_time= period * k)
                                start_time= current_time)
            # k += 1
            workflow_set.addWorkflow(workflow)
            T_arr_new.append(workflow.T)
            task_volume_multiplier_arr.append(task_volume_multiplier)
            data_volume_multiplier_arr.append(data_volume_multiplier)

        current_time += period
        n_worfklow -= n_workflow_per_period

    end_time = datetime.now()
    preprocessing_time_cjm = end_time - start_time

    # if repeat_workflow_set_flag == "new_test":
    with open("/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/indexes_arr.csv", 'w') as f:
        fieldnames = ['workflow_id', 'index_in_sample', 'T', 'start_time', 'task_volume_multiplier', 'data_volume_multiplier']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, index in enumerate(indexes):
            row = {fieldnames[0]: i,
                   fieldnames[1]: index,
                   fieldnames[2]: T_arr_new[i],
                   fieldnames[3]: starts[i],
                   fieldnames[4]: task_volume_multiplier_arr[i],
                   fieldnames[5]: data_volume_multiplier_arr[i]}
            writer.writerow(row)


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

    allocations = []
    allocations.append(AllocationFTL(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationASAP(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(AllocationASAP_O(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))

    batch_time_ftl = 0
    batch_time_asap = 0
    batch_time_asap_o = 0

    vma_time_ftl = 0
    vma_time_asap = 0
    vma_time_asap_o = 0

    for allocation in allocations:
        time = 0
        start_time = datetime.now()
        batches = allocation.formParallelBatches(time)
        end_time = datetime.now()
        allocation.batches_size = len(batches)
        batch_time = end_time - start_time

        if isinstance(allocation, AllocationFTL):
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_FTL)
            batch_time_ftl = batch_time
        if isinstance(allocation, AllocationASAP):
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_ASAP)
            batch_time_asap = batch_time
        if isinstance(allocation, AllocationASAP_O):
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_ASAP_O)
            batch_time_asap_o = batch_time


        start_time = datetime.now()
        allocation.vma(batches)
        end_time = datetime.now()
        vma_time = end_time - start_time

        log = allocation.log
        color = log[["workflow_id"]]
        color = color.drop_duplicates()
        color["color"] = color.apply(lambda x: rand_color(x), axis=1)
        log = pd.merge(log, color, on='workflow_id', how='left')
        log = log.sort_values(["vm_id", "vm_start"])


        if isinstance(allocation, AllocationFTL):
            vma_time_ftl = vma_time

            workflow_costs = allocation.workflow_costs
            with open(
                    "/Users/artembulkhak/PycharmProjects/Scheduling-in-Workflow-as-a-Service/Output/ftl_workflow_costs.csv",
                    'w') as f:
                fieldnames = ['workflow_id', 'allocation_cost']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for i, cost in enumerate(workflow_costs):
                    row = {fieldnames[0]: i,
                           fieldnames[1]: cost}
                    writer.writerow(row)

            drawer.draw_big_gantt(log, config.GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationASAP):
            vma_time_asap = vma_time
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_ASAP)
        if isinstance(allocation, AllocationASAP_O):
            vma_time_asap_o = vma_time
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_ASAP_O)


        Analyzer.analyze_allocation(allocation, T_arr_new)


        # log = allocation.log
        # color = log[["vm_id"]]
        # color = color.drop_duplicates()
        # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
        # log = pd.merge(log, color, on='vm_id', how='left')
        # log = log.sort_values(["vm_id", "vm_end"])
    # CSVHandler.write_allocation_logfile(Utils.config.ALLOCATION_LOG_FILE, log)
    # CSVHandler.write_config_file(Utils.config.config_FILE)


    Analyzer.print_comparison_table(allocations)

    print('Duration of preprocessing (CJM): {}'.format(preprocessing_time_cjm))

    print('Duration of forming batches (FTL): {}'.format(batch_time_ftl))
    print('Duration of forming batches (ASAP): {}'.format(batch_time_asap))
    print('Duration of forming batches (ASAP_O): {}'.format(batch_time_asap_o))

    print('Duration of vma (FTL): {}'.format(vma_time_ftl))
    print('Duration of vma (ASAP): {}'.format(vma_time_asap))
    print('Duration of vma (ASAP_O): {}'.format(vma_time_asap_o))


    # ------------ vm_id = color ------------
    # log = allocation.log
    # color = log[["vm_id"]]
    # color = color.drop_duplicates()
    # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    # log = pd.merge(log, color, on='vm_id', how='left')
    # log = log.sort_values(["vm_id", "vm_end"])

    # ------------ workflow_id = color ------------
    # log = allocation.log
    # color = log[["workflow_id"]]
    # color = color.drop_duplicates()
    # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    # log = pd.merge(log, color, on='workflow_id', how='left')
    # log = log.sort_values(["vm_id", "vm_start"])
    # drawer.draw_result_gantt(log, Utils.config.GANTT_FIGURES_BASIC)
    # log = log.sort_values(["vm_id", "vm_end"])
    # drawer.draw_result_gantt(log, Utils.config.GANTT_FIGURES_VM_SORT)