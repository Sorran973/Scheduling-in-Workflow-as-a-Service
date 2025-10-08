import csv
import random
from copy import deepcopy
from datetime import datetime

import pandas as pd

from AllocationModule.AllocationASAP_O import AllocationASAP_O
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationASAP import AllocationASAP
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.HEFT.HEFTNode import HEFTNode
from AllocationModule.NewVmForEachTask import NewVmForEachTask
from SchedulingModule.CJM.Model.Criteria import CostCriteria
from SchedulingModule.CJM.Model.Edge import Edge
from SchedulingModule.CJM.Model.Node import Node
from Utils.Analyzer import Analyzer
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from config import *
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer


if __name__ == '__main__':

    vm_types = CSVHandler.read_vms_table(VMS_TABLE_FILE_PATH)

    with open(LOG_FILE, 'w') as f:
        fieldnames = ['workflow_T', 'cjm_status', 'vma_status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()


    for t in range(704, 1396):
        workflow_set = WorkflowSet()
        start_time = datetime.now()
        Node.id = 0
        Edge.id = 0
        workflow = Workflow(XML_FILE=LIGO200,
                            T=t,
                            vm_types=vm_types,
                            criteria=CostCriteria(min),
                            task_volume_multiplier=1,
                            data_volume_multiplier=1,
                            start_time=0)

        workflow_set.addWorkflow(workflow)
        end_time = datetime.now()
        if len(workflow_set.success_scheduled_workflow) > 0:

            print('Duration of scheduling (CJM): {}'.format(end_time - start_time))
            print(len(workflow_set.success_scheduled_workflow))
            print()
            cjm_status = 'SUCCESS'

            for i in workflow_set.success_scheduled_workflow:
                print(i)

            tasks = CSVHandler.read_task_time_table(TASK_TIME_TABLE_FILE)
            workload_start_time = tasks[0].start
            workload_end_time = max(tasks, key=lambda task: task.end).end
            print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
            data_transfer = CSVHandler.read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks)


            drawer: Drawer = PyvisDrawer()
        # drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)

            allocations = []
            # allocations.append(AllocationFTL(VMA_CRITERIA, vm_types, deepcopy(tasks)))
        # allocations.append(AllocationASAP(VMA_CRITERIA, vm_types, deepcopy(tasks)))
            allocations.append(AllocationASAP_O(VMA_CRITERIA, vm_types, deepcopy(tasks)))
        # allocations.append(AllocationMixed(VMA_CRITERIA, vm_types, deepcopy(tasks)))
        # allocations.append(NewVmForEachTask(VMA_CRITERIA, vm_types, deepcopy(tasks)))

            for allocation in allocations:
                time = 0
                batches = allocation.formParallelBatches(time)
                allocation.batches_size = len(batches)

        # N_pc = 0
        # for b in range(0, len(batches)-1):
        #     for task in batches[b]:
        #         for data_transfer in task.output_transfers:
        #             for next_task in batches[b+1]:
        #                 if next_task.id == data_transfer.task_to.id:
        #                     N_pc += 1
        #                     # print(str(task.id) + "-->" + str(next_task.id))
        #                     break
        # print("N_pc: " + str(N_pc))
    #
    #
    #     if isinstance(allocation, AllocationFTL):
    #         drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_FTL)
    #     if isinstance(allocation, AllocationASAP):
    #         drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_ASAP)
    #     if isinstance(allocation, AllocationASAP_O):
    #         drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_ASAP_O)
    #     if isinstance(allocation, AllocationMixed):
    #         drawer.draw_batches_gantt_for_mixed(allocation.tasks)
    #     if isinstance(allocation, NewVmForEachTask):
    #         drawer.draw_batches_gantt(allocation.tasks, GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH)
    #
                a = allocation.vma(batches)
                if a == 0:
                    vma_status = 'UNSUCCESS'
                    print("VMA UNSUCCESS")
                else:
                    vma_status = 'SUCCESS'
                    print("VMA SUCCESS")

                with open(LOG_FILE, 'a') as f:
                    fieldnames = ['workflow_T', 'cjm_status', 'vma_status']

                    writer = csv.DictWriter(f, fieldnames=fieldnames)

                    row = {fieldnames[0]: t,
                           fieldnames[1]: cjm_status,
                           fieldnames[2]: vma_status}
                    writer.writerow(row)

    #
    #
    # #####################################################
    # ###################### ANALYZING ####################
    # #####################################################
    # T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    # for allocation in allocations:
    #     Analyzer.analyze_allocation(allocation, T_arr)
    #
    #
    # Analyzer.print_comparison_table(allocations)
    #
    #
    # #####################################################
    # ################# DRAWING GANTT PLOTS ###############
    # #####################################################
    # for allocation in allocations:
    #     if isinstance(allocation, AllocationFTL):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         log = log.sort_values(["vm_id", "vm_start"])
    #         drawer.draw_result_gantt(log, GANTT_FIGURES_FTL)
    #     if isinstance(allocation, AllocationASAP):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         log = log.sort_values(["vm_id", "vm_start"])
    #         drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP)
    #     if isinstance(allocation, AllocationASAP_O):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         log = log.sort_values(["vm_id", "vm_start"])
    #         drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP_O)
    #     if isinstance(allocation, AllocationMixed):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         log = log.sort_values(["vm_id", "vm_start"])
    #         drawer.draw_result_gantt(log, GANTT_FIGURES_ASAP_MOD)
    #     if isinstance(allocation, NewVmForEachTask):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         drawer.draw_result_gantt(log, GANTT_FIGURES_NEW_VM_FOR_EACH)
    # a = 0