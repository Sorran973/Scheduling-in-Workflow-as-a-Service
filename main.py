import csv
import random
from copy import deepcopy, copy
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.RandomAssignment import RandomAssignment
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from AllocationModule.StrictRandomAssignment import StrictRandomAssignment
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from AllocationModule.AllocationModule import AllocationModule
import Utils.Configuration
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

    workflow_samples = Utils.Configuration.WORKFLOW_SAMPLES
    vm_types = CSVHandler.read_vms_table(Utils.Configuration.VMS_TABLE_FILE)
    #####################################################
    ################# SCHEDULING MODULE #################
    #####################################################
    n_worfklow = 100
    period = 60
    n_workflow_per_period = 100
    current_time = 0
    repeat_workflow_set_flag = "new_test"
    # repeat_workflow_set_flag = "old_test"
    indexes = []
    starts = []
    T_arr = []
    T_arr_new = []
    j = 0
    k = 0

    if repeat_workflow_set_flag == "old_test":
        with open("/Users/artembulkhak/PycharmProjects/Dissertation/Output/indexes_arr.csv", newline='') as f:
            reader = csv.reader(f, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                indexes.append(int(row[1]))
                # T_arr.append(int(row[2]))
                starts.append(int(row[3]))


    # if T_arr:
    workflow_set = WorkflowSet()
    while n_worfklow > 0:
        if n_worfklow < n_workflow_per_period:
            n_workflow_per_period = n_worfklow
        for i in range(n_workflow_per_period):
            if repeat_workflow_set_flag == "old_test":
                index_workflow_from_samples = indexes[j]
                # T = T_arr[j]
                T = None
                workflow_start_time = starts[j]
                j += 1
            else:
                index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
                T = None
                # T = 2000
                workflow_start_time = random.randint(current_time, current_time + period)
                indexes.append(index_workflow_from_samples)
                starts.append(workflow_start_time)

            workflow = Workflow(XML_FILE=workflow_samples[index_workflow_from_samples],
                                              T=T,
                                              vm_types=vm_types,
                                              criteria=Utils.Configuration.CJM_CRITERIA,
                                              task_volume_multiplier=1,
                                              data_volume_multiplier=1,
                                              # start_time=random.randint(current_time, current_time + period))
                                              # start_time= period * k)
                                              start_time= current_time)
            # k += 1
            workflow_set.addWorkflow(workflow)
            T_arr_new.append(workflow.T)

        current_time += period
        n_worfklow -= n_workflow_per_period

    # if repeat_workflow_set_flag == "new_test":
    with open("/Users/artembulkhak/PycharmProjects/Dissertation/Output/indexes_arr.csv", 'w') as f:
        fieldnames = ['workflow_id', 'index_in_sample', 'T', 'start_time']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, index in enumerate(indexes):
            row = {fieldnames[0]: i,
                   fieldnames[1]: index,
                   fieldnames[2]: T_arr_new[i],
                   fieldnames[3]: starts[i]}
            writer.writerow(row)

    # workflow_set = WorkflowSet()
    # workflow_set.addWorkflow(Workflow(XML_FILE=Utils.Configuration.XML_FILE,
    #                                   T=None,
    #                                   vm_types=vm_types,
    #                                   criteria=Utils.Configuration.CJM_CRITERIA,
    #                                   task_volume_multiplier=1,
    #                                   data_volume_multiplier=1,
    #                                   start_time=0))
    # T_arr_new.append(workflow_set.workflows[0].T)
    # #
    # workflow_set.addWorkflow(Workflow(XML_FILE='JobExamples/CYBERSHAKE.n.50.0.dax',
    #                                   T=None,
    #                                   vm_types=vm_types,
    #                                   criteria=Utils.Configuration.CJM_CRITERIA,
    #                                   task_volume_multiplier=1,
    #                                   data_volume_multiplier=1,
    #                                   start_time=0))
    # T_arr_new.append(workflow_set.workflows[1].T)

    drawer: Drawer = PyvisDrawer()
    # drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer_graph: Drawer = GraphvizDrawer()
    # drawer_graph.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer.draw_gantt(workflow_set.drawn_nodes)
    # drawer.draw_new_gantt(workflow_set.drawn_nodes)

    #####################################################
    ################# ALLOCATION MODULE #################
    #####################################################
    tasks = CSVHandler.read_task_time_table(Utils.Configuration.TASK_TIME_TABLE_FILE)
    workload_start_time = tasks[0].start
    workload_end_time = max(tasks, key=lambda task: task.end).end
    print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")


    data_transfer = CSVHandler.read_data_transfer_table(Utils.Configuration.TRANSFER_SIZE_TABLE_FILE, tasks)

    allocations = []
    allocations.append(AllocationFTL(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationModule(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationMixed(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(NewVmForEachTask(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(RandomAssignment(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(StrictRandomAssignment(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))

    batch_time_ftl = 0
    batch_time_asap = 0
    batch_time_asap_mod = 0
    batch_time_new_vm = 0

    vma_time_ftl = 0
    vma_time_asap = 0
    vma_time_asap_mod = 0
    vma_time_new_vm = 0

    for allocation in allocations:
        time = 0
        batches = allocation.formParallelBatches(time)
        if isinstance(allocation, AllocationFTL):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, Utils.Configuration.GANTT_FIGURES_BATCHES_FTL)
            end_time = datetime.now()
            batch_time_ftl = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_ftl = end_time - start_time
        if isinstance(allocation, AllocationModule):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, Utils.Configuration.GANTT_FIGURES_BATCHES_ASAP)
            end_time = datetime.now()
            batch_time_asap = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_asap = end_time - start_time
        if isinstance(allocation, AllocationMixed):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, Utils.Configuration.GANTT_FIGURES_BATCHES_ASAP_MOD)
            end_time = datetime.now()
            batch_time_asap_mod = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_asap_mod = end_time - start_time
        if isinstance(allocation, NewVmForEachTask):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, Utils.Configuration.GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)
            end_time = datetime.now()
            batch_time_new_vm = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_new_vm = end_time - start_time
        # drawer.draw_batches_gantt(allocation.tasks)

        log = allocation.log
        color = log[["vm_id"]]
        color = color.drop_duplicates()
        color["color"] = color.apply(lambda x: rand_color(x), axis=1)
        log = pd.merge(log, color, on='vm_id', how='left')
        log = log.sort_values(["vm_id", "vm_end"])
        # if isinstance(allocation, AllocationModule):
        # drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_VM_SORT)
        # if isinstance(allocation, NewVmForEachTask):
        #     drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_NEW_VM_FOR_EACH)

    # CSVHandler.write_allocation_logfile(Utils.Configuration.ALLOCATION_LOG_FILE, log)
    # CSVHandler.write_configuration_file(Utils.Configuration.CONFIGURATION_FILE)

    #####################################################
    ###################### ANALYZING ####################
    #####################################################

    for allocation in allocations:
        Analyzer.analyze_allocation(allocation, T_arr_new)


    Analyzer.print_comparison_table(allocations)

    print('Duration of forming batches (FTL): {}'.format(batch_time_ftl))
    print('Duration of forming batches (ASAP): {}'.format(batch_time_asap))
    print('Duration of forming batches (ASAP_MOD): {}'.format(batch_time_asap_mod))
    print('Duration of forming batches (NewVM): {}'.format(batch_time_new_vm))

    print('Duration of vma (FTL): {}'.format(vma_time_ftl))
    print('Duration of vma (ASAP): {}'.format(vma_time_asap))
    print('Duration of vma (ASAP_MOD): {}'.format(vma_time_asap_mod))
    print('Duration of vma (NewVM): {}'.format(vma_time_new_vm))



    # Analyzer.print_workload_statistics(allocations)

    # drawer.draw_cost_charts(allocations)

        # vm_idle_time

        # workflow_set = log.loc[[0]]
        # workflow_set1 = log.loc[0:10]
        # workflow_set2 = log.iloc[[0]]
        # workflow_set3 = log.iloc[0:10]
        # z = log[(log.workflow_id == 0) & (log.vm_end == log[log.workflow_id == 0].vm_end.max())]
        # z = log.loc[(log.workflow_id == 0) & (log['task_name'].str.startswith('p')), ['workflow_id', 'task_name']]
        # var = log[(log.workflow_id == 0) & (log.task_id == 1)]



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
            drawer.draw_big_gantt(log, Utils.Configuration.GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationModule):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, Utils.Configuration.GANTT_FIGURES_ASAP)
        if isinstance(allocation, AllocationMixed):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, Utils.Configuration.GANTT_FIGURES_ASAP_MOD)
        if isinstance(allocation, NewVmForEachTask):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            drawer.draw_big_gantt(log, Utils.Configuration.GANTT_FIGURES_NEW_VM_FOR_EACH)


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
    # drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_BASIC)
    # log = log.sort_values(["vm_id", "vm_end"])
    # drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_VM_SORT)