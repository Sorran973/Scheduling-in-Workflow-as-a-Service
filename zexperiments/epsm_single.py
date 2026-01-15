import random
from copy import deepcopy
from datetime import datetime

import pandas as pd

from AllocationModule.AllocationASAP_O import AllocationASAP_O
from AllocationModule.AllocationBestFit import AllocationBestFit
from AllocationModule.AllocationFTL import AllocationFTL
from AllocationModule.AllocationASAP import AllocationASAP
from AllocationModule.AllocationMixed import AllocationMixed
from AllocationModule.EPSM.AllocationEPSM_Batch_BestFit import AllocationEPSM_Batch_BestFit
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

# избегать создания новых ВМ:
# 1) поэтому сначала смотрим idle ВМ, у которых есть входные данные для рассматриваемой задачи и могут выполнить задачу,
#    соблюдая дедлайн;
# 2) потом смотрим все idle ВМ, которые могут выполнить задачу, соблюдая дедлайн;
# 3) потом если есть возможность (дедлайн может быть соблюден в следующем цикле планирования при выполнении задачи на
#    самом медленном типе ВМ - почти никогда не выполняется), то нужно отложить выполнение задачи;
# 4) иначе создать новую ВМ

# динамически изменять дедлайны задач:
# 1) если задача выполнилась позже, то пропорционально сократить дедлайны только для задач-потомков;
# 2) если задача наоборот выполнилась раньше, то пропорционально увеличить дедлайны только для задач-потомков.
# То есть, на момент завершения планирования задачи, проверять осталось ли свободное время или дедлайн вообще не был
# соблюден, тогда запускать процедуру перерасчета дедлайнов для задач-потомков

# ВМ уничтожаются при наступлении нового периода биллинга (если он длится час). В случае посекундной тарификации любой
# простой это дополнительные траты, поэтому вероятно надо уничтожать idle ВМ при каждой возможности. Хотя с другой
# стороны, если придерживаться идеи "по возможности избегать аренды новых ВМ", то лучше платить за простой (если он
# меньше времени выделения ВМ) с потенциальной возможностью переиспользовать ВМ


if __name__ == '__main__':

    vm_types = CSVHandler.read_vms_table(VMS_TABLE_FILE_PATH)

    task_volume_multiplier = 1

    workflow_type = EnumWorkflow.SIPHT50

    if workflow_type in (EnumWorkflow.GENOME50, EnumWorkflow.GENOME100, EnumWorkflow.GENOME200,
                         EnumWorkflow.GENOME300, EnumWorkflow.GENOME400, EnumWorkflow.GENOME500):
        task_volume_multiplier = 0.1

    workflow_type_str = workflow_type.value
    # workflow_type_str = "MyTestDAXes/test.xml"
    xml_file = WORKFLOW_EXAMPLES_DIR + workflow_type_str


    workflow_set = WorkflowSet()
    workflow = EPSMWorkflow(XML_FILE=xml_file,
                        T=T,
                        vm_types=vm_types,
                        criteria=CJM_CRITERIA,
                        task_volume_multiplier=task_volume_multiplier,
                        data_volume_multiplier=1,
                        start_time=0)


    start_time = datetime.now()
    workflow_set.addEPSMWorkflow(workflow)
    # workflow_set.addWorkflow(workflow2)
    end_time = datetime.now()
    print('Duration of scheduling (EPSM): {}'.format(end_time - start_time))

    tasks = CSVHandler.read_task_time_table(TASK_TIME_TABLE_FILE)
    workload_start_time = tasks[0].start
    workload_end_time = max(tasks, key=lambda task: task.end).end
    print(f"\n\tWorkload Limit Time: {workload_end_time - workload_start_time}")
    data_transfer = CSVHandler.read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks)


    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)

    epsm_batch_bestfit = AllocationEPSM_Batch_BestFit(VMA_CRITERIA, vm_types, deepcopy(tasks))
    time = 0
    batches = epsm_batch_bestfit.formParallelBatches(time)
    drawer.draw_batches_gantt(epsm_batch_bestfit.tasks, GANTT_FIGURES_BATCHES_EPSM)
    epsm_batch_bestfit.vma(batches)

    T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    Analyzer.analyze_allocation(epsm_batch_bestfit, T_arr)

    log = epsm_batch_bestfit.log
    color = log[["workflow_id"]]
    color = color.drop_duplicates()
    color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    log = pd.merge(log, color, on='workflow_id', how='left')
    log = log.sort_values(["vm_id", "vm_start"])
    # drawer.draw_result_gantt_HEFT(log, GANTT_FIGURES_EPSM)
    drawer.draw_result_gantt(log, GANTT_FIGURES_EPSM)

    #
    # epsm = AllocationEPSM(VMA_CRITERIA, vm_types, deepcopy(tasks))
    #
    # epsm_o = AllocationEPSM_O(VMA_CRITERIA, vm_types, deepcopy(tasks))
    # epsm_o.vma()
    #
    # sorted_tasks = epsm.preprocessing()
    # drawer.draw_batches_gantt_epsm(epsm.tasks, GANTT_FIGURES_BATCHES_EPSM)
    #
    # epsm.vma(sorted_tasks)
    #
    # log = epsm.log
    # color = log[["workflow_id"]]
    # color = color.drop_duplicates()
    # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    # log = pd.merge(log, color, on='workflow_id', how='left')
    # log = log.sort_values(["vm_id", "vm_start"])
    # # drawer.draw_result_gantt_HEFT(log, GANTT_FIGURES_EPSM)
    # drawer.draw_result_gantt(log, GANTT_FIGURES_EPSM)
    #
    # #####################################################
    # ###################### ANALYZING ####################
    # #####################################################
    # T_arr = list(map(lambda workflow: workflow.T, workflow_set.workflows))
    # Analyzer.analyze_allocation(epsm, T_arr)
    #
    #
    # a = 0
