import csv
import random
from copy import deepcopy
from datetime import datetime

import pandas as pd

import config
from AllocationModule.AllocationASAP_O import AllocationASAP_O
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.NewVmForEachTask import NewVmForEachTask
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
    n_worfklow = 30
    period = 60
    n_workflow_per_period = 30
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
                T_arr.append(float(row[2]))
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
                T = config.T
                workflow_start_time = starts[j]
                j += 1
            else:
                index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
                T = config.T
                workflow_start_time = random.randint(current_time, current_time + period)
                indexes.append(index_workflow_from_samples)
                starts.append(workflow_start_time)

            workflow = Workflow(XML_FILE=workflow_samples[index_workflow_from_samples],
                                T=T,
                                vm_types=vm_types,
                                criteria=config.CJM_CRITERIA,
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
    # allocations.append(AllocationASAP(Utils.config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationASAP_O(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(AllocationMixed(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    allocations.append(NewVmForEachTask(config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(RandomAssignment(Utils.config.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(StrictRandomAssignment(Utils.config.VMA_CRITERIA, vm_types, deepcopy(tasks)))

    batch_time_ftl = 0
    batch_time_asap = 0
    batch_time_asap_o = 0
    batch_time_asap_mixed = 0
    batch_time_new_vm = 0

    vma_time_ftl = 0
    vma_time_asap = 0
    vma_time_asap_o = 0
    vma_time_asap_mixed = 0
    vma_time_new_vm = 0

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
                            break
        print("N_pc: " + str(N_pc))

        if isinstance(allocation, AllocationFTL):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_FTL)
            end_time = datetime.now()
            batch_time_ftl = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_ftl = end_time - start_time
        if isinstance(allocation, AllocationASAP):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_ASAP)
            end_time = datetime.now()
            batch_time_asap = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_asap = end_time - start_time
        if isinstance(allocation, AllocationASAP_O):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_ASAP_O)
            end_time = datetime.now()
            batch_time_asap_o = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_asap_o = end_time - start_time
        if isinstance(allocation, AllocationMixed):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_ASAP_MOD)
            end_time = datetime.now()
            batch_time_asap_o = end_time - start_time
            start_time = datetime.now()
            allocation.vma(batches)
            end_time = datetime.now()
            vma_time_asap_o = end_time - start_time
        if isinstance(allocation, NewVmForEachTask):
            start_time = datetime.now()
            drawer.draw_big_batches_gantt(allocation.tasks, config.GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)
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
        # drawer.draw_result_gantt(log, Utils.config.GANTT_FIGURES_VM_SORT)
        # if isinstance(allocation, NewVmForEachTask):
        #     drawer.draw_result_gantt(log, Utils.config.GANTT_FIGURES_NEW_VM_FOR_EACH)

    # CSVHandler.write_allocation_logfile(Utils.config.ALLOCATION_LOG_FILE, log)
    # CSVHandler.write_config_file(Utils.config.config_FILE)

    #####################################################
    ###################### ANALYZING ####################
    #####################################################

    for allocation in allocations:
        Analyzer.analyze_allocation(allocation, T_arr_new)


    Analyzer.print_comparison_table(allocations)

    print('Duration of forming batches (FTL): {}'.format(batch_time_ftl))
    # print('Duration of forming batches (ASAP): {}'.format(batch_time_asap))
    print('Duration of forming batches (ASAP_O): {}'.format(batch_time_asap_o))
    print('Duration of forming batches (ASAP_MIXED): {}'.format(batch_time_asap_mixed))
    print('Duration of forming batches (NewVM): {}'.format(batch_time_new_vm))

    print('Duration of vma (FTL): {}'.format(vma_time_ftl))
    # print('Duration of vma (ASAP): {}'.format(vma_time_asap))
    print('Duration of vma (ASAP_O): {}'.format(vma_time_asap_o))
    print('Duration of vma (ASAP_MIXED): {}'.format(vma_time_asap_mixed))
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
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_FTL)
        if isinstance(allocation, AllocationASAP):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_ASAP)
        if isinstance(allocation, AllocationASAP_O):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_ASAP_O)
        if isinstance(allocation, AllocationMixed):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            log = log.sort_values(["vm_id", "vm_start"])
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_ASAP_MOD)
        if isinstance(allocation, NewVmForEachTask):
            log = allocation.log
            color = log[["workflow_id"]]
            color = color.drop_duplicates()
            color["color"] = color.apply(lambda x: rand_color(x), axis=1)
            log = pd.merge(log, color, on='workflow_id', how='left')
            drawer.draw_big_gantt(log, config.GANTT_FIGURES_NEW_VM_FOR_EACH)


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