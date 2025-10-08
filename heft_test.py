from datetime import datetime

import pandas as pd

from AllocationModule.HEFT.HEFT import HEFT
from AllocationModule.HEFT.HEFTVM import HEFTVM
from AllocationModule.HEFT.HEFTWorkflow import HEFTWorkflow
from SchedulingModule.CJM.Model.Criteria import CostCriteria
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet

import config
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer



if __name__ == '__main__':
    vm_types = CSVHandler.read_vms_table(Configuration.VMS_TABLE_FILE)
    workflow_samples = Configuration.WORKFLOW_SAMPLES

    # FTL: 142
    # ASAP: 122
    # ASAP_MIX: 126

    # New_VM: 150
    # x: 60
    # 1X: 15
    # 2X: 33
    # 3X: 21
    # XXX: 21
    vm_numbers = [21, 21, 33, 15, 60]
    vms = []
    for i, num in enumerate(vm_numbers):
        for j in range(num):
            vms.append(HEFTVM(vm_types[i].type, vm_types[i].perf, vm_types[i].cost, vm_types[i].prep_time,
                              vm_types[i].shutdown_time))
        # vms_value = []
        # for j in range(1, len(self.nodes) - 1):
        #     exec_time = round_up(self.nodes[j].volume / i.perf)
        #     vms_value.append(exec_time)
        #     self.nodes[j].exec_times_by_vm.append(exec_time)
        # self.vms_table.append(vms_value)
        # self.vms_cost.append(i.cost)


    T = None
    # T = 38

    # workflow_set = WorkflowSet()
    # index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
    #
    # n_worfklow = 100
    # period = 60
    # n_workflow_per_period = 1
    # current_time = 0
    # repeat_workflow_set_flag = "new_test"
    # # repeat_workflow_set_flag = "old_test"
    # indexes = []
    # starts = []
    # T_arr = []
    # T_arr_new = []
    # j = 0
    # k = 0
    #
    # if repeat_workflow_set_flag == "old_test":
    #     with open("/Users/artembulkhak/PycharmProjects/Dissertation/Output/indexes_arr.csv", newline='') as f:
    #         reader = csv.reader(f, delimiter=',', quotechar='|')
    #         headers = next(reader)
    #         for row in reader:
    #             indexes.append(int(row[1]))
    #             # T_arr.append(int(row[2]))
    #             starts.append(int(row[3]))
    #
    # # if T_arr:
    # workflow_set = WorkflowSet()
    # while n_worfklow > 0:
    #     if n_worfklow < n_workflow_per_period:
    #         n_workflow_per_period = n_worfklow
    #     for i in range(n_workflow_per_period):
    #         if repeat_workflow_set_flag == "old_test":
    #             index_workflow_from_samples = indexes[j]
    #             # T = T_arr[j]
    #             T = None
    #             workflow_start_time = starts[j]
    #             j += 1
    #         else:
    #             index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)
    #             T = None
    #             # T = 2000
    #             workflow_start_time = random.randint(current_time, current_time + period)
    #             indexes.append(index_workflow_from_samples)
    #             starts.append(workflow_start_time)
    #
    #         workflow = Workflow(XML_FILE=workflow_samples[index_workflow_from_samples],
    #                             T=T,
    #                             vm_types=vm_types,
    #                             criteria=Utils.Configuration.CJM_CRITERIA,
    #                             task_volume_multiplier=1,
    #                             data_volume_multiplier=1,
    #                             # start_time=random.randint(current_time, current_time + period))
    #                             # start_time= period * k)
    #                             start_time=current_time)
    #         # k += 1
    #         workflow_set.addWorkflow(workflow)
    #         T_arr_new.append(workflow.T)
    #
    #     current_time += period
    #     n_worfklow -= n_workflow_per_period
    #
    # # if repeat_workflow_set_flag == "new_test":
    # with open("/Users/artembulkhak/PycharmProjects/Dissertation/Output/indexes_arr.csv", 'w') as f:
    #     fieldnames = ['workflow_id', 'index_in_sample', 'T', 'start_time']
    #     writer = csv.DictWriter(f, fieldnames=fieldnames)
    #     writer.writeheader()
    #
    #     for i, index in enumerate(indexes):
    #         row = {fieldnames[0]: i,
    #                fieldnames[1]: index,
    #                fieldnames[2]: T_arr_new[i],
    #                fieldnames[3]: starts[i]}
    #         writer.writerow(row)

    workflow_set = WorkflowSet()
    start_time = datetime.now()
    workflow = HEFTWorkflow(XML_FILE=Configuration.LIGO50,
                            T=T,
                            vm_types=vm_types,
                            vms=vms,
                            criteria=CostCriteria(min),
                            task_volume_multiplier=1,
                            data_volume_multiplier=1,
                            start_time=0)

    workflow2 = HEFTWorkflow(XML_FILE=Configuration.LIGO50,
                             T=T,
                             vm_types=vm_types,
                             vms=vms,
                             criteria=CostCriteria(min),
                             task_volume_multiplier=1,
                             data_volume_multiplier=1,
                             start_time=60)

    workflow3 = HEFTWorkflow(XML_FILE=Configuration.LIGO50,
                             T=T,
                             vm_types=vm_types,
                             vms=vms,
                             criteria=CostCriteria(min),
                             task_volume_multiplier=1,
                             data_volume_multiplier=1,
                             start_time=120)


    workflow_set.addHEFTWorkflow(workflow)
    workflow_set.addHEFTWorkflow(workflow2)
    workflow_set.addHEFTWorkflow(workflow3)

    heft = HEFT(vms, workflow_set)
    end_time = datetime.now()
    print('Duration of scheduling (HEFT): {}'.format(end_time - start_time))
    print("Total Cost of HEFT: " + str(heft.total_cost))

    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)

    log = heft.log
    color = log[["workflow_id"]]
    color = color.drop_duplicates()
    color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    log = pd.merge(log, color, on='workflow_id', how='left')
    log = log.sort_values(["vm_id", "vm_start"])
    drawer.draw_result_gantt_HEFT(log, Configuration.GANTT_FIGURES_HEFT)
    # drawer.draw_result_gantt_HEFT_vms(heft.vms, Utils.Configuration.GANTT_FIGURES_HEFT)
    # drawer.draw_result_gantt_HEFT_nodes(heft.nodes, heft.vms, Utils.Configuration.GANTT_FIGURES_HEFT)

    print(log.task_end.max())
    a = 0

    # tasks = CSVHandler.read_task_time_table(Utils.Configuration.TASK_TIME_TABLE_FILE)
    # workload_start_time = tasks[0].start
    # workload_end_time = max(tasks, key=lambda task: task.end).end
    # print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    # data_transfer = CSVHandler.read_data_transfer_table(Utils.Configuration.TRANSFER_SIZE_TABLE_FILE, tasks)
    #
    #
    # drawer: Drawer = PyvisDrawer()
    # drawer.draw_graph(workflow.drawn_nodes, workflow.drawn_edges)
    #
    # allocations = []
    # # allocations.append(AllocationFTL(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # # allocations.append(AllocationModule(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # # allocations.append(AllocationMixed(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # # allocations.append(NewVmForEachTask(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    # allocations.append(HEFT(Utils.Configuration.VMA_CRITERIA, vm_types, deepcopy(tasks)))
    #
    # for allocation in allocations:
    #     time = 0
    #     batches = allocation.formParallelBatches(time)
    #
    #     if isinstance(allocation, HEFT):
    #         drawer.draw_batches_gantt(allocation.tasks, Utils.Configuration.GANTT_FIGURES_BATCHES_TEN_BEST_VM)
    #
    #     allocation.vma(batches)
    #
    #
    # #####################################################
    # ###################### ANALYZING ####################
    # #####################################################
    # workflow_set = WorkflowSet
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
    #     if isinstance(allocation, HEFT):
    #         log = allocation.log
    #         color = log[["workflow_id"]]
    #         color = color.drop_duplicates()
    #         color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    #         log = pd.merge(log, color, on='workflow_id', how='left')
    #         log = log.sort_values(["vm_id", "vm_start"])
    #         drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_TEN_BEST_VM)