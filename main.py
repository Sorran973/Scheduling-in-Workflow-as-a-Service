import pandas as pd
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from AllocationModule.AllocationModule import AllocationModule
import Utils.Configuration
from Utils.Visualization.PyvisDrawer import PyvisDrawer, rand_color
from Utils.Visualization import Drawer



if __name__ == '__main__':

    #####################################################
    ################# SCHEDULING MODULE #################
    #####################################################
    vm_types = CSVHandler.read_vms_table(Utils.Configuration.VMS_TABLE_FILE)

    workflow_set = WorkflowSet()
    workflow_set.addWorkflow(Workflow(Utils.Configuration.XML_FILE,
                                      Utils.Configuration.T,
                                      vm_types,
                                      Utils.Configuration.CRITERIA,
                                      1,
                                      1))
    workflow_set.schedule()

    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer.draw_gantt(workflow_set.drawn_nodes)
    # drawer.draw_new_gantt(workflow_set.drawn_nodes)

    #####################################################
    ################# ALLOCATION MODULE #################
    #####################################################

    tasks = CSVHandler.read_task_time_table(Utils.Configuration.TASK_TIME_TABLE_FILE)
    data_transfer = CSVHandler.read_data_transfer_table(Utils.Configuration.TRANSFER_SIZE_TABLE_FILE, tasks)

    allocation = AllocationModule(vm_types, tasks)
    time = 0
    batches = allocation.formParallelBatches(time)  # FTL algorithm
    drawer.draw_batches_gantt(allocation.tasks)

    allocation.setDataTransferSpeed(Utils.Configuration.DATA_TRANSFER_CHANNEL_SPEED)
    allocation.setOptimizationCriteria(Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA)
    allocation.vma(batches)

    log = allocation.log
    CSVHandler.write_allocation_logfile(Utils.Configuration.ALLOCATION_LOG_FILE, log)
    CSVHandler.write_configuration_file(Utils.Configuration.CONFIGURATION_FILE)
    print("Total Cost: " + str(log.allocation_cost.sum()))
    print("Total Time: " + str(log.vm_end.max()))

    color = log[["vm_id"]]
    color = color.drop_duplicates()
    color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    log = pd.merge(log, color, on='vm_id', how='left')

    drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_BASIC)
    log = log.sort_values(["vm_id", "vm_end"])
    drawer.draw_result_gantt(log, Utils.Configuration.GANTT_FIGURES_VM_SORT)





    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(MONTAGE1000, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(SIPHT50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(GENOME50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 55))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 110))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 230))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))
    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 10, 10, 0))

    # workflow_set.addWorkflow(
    #     Workflow(MONTAGE50, criteria, task_volume_multiplier=100, data_volume_multiplier=100, start_time=3000))
    # workflow_set.addWorkflow(
    #     Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=15, data_volume_multiplier=0, start_time=500))
    # workflow_set.addWorkflow(
    #     Workflow(SIPHT50, criteria, task_volume_multiplier=2, data_volume_multiplier=5, start_time=5000))
    # workflow_set.addWorkflow(
    #     Workflow(LIGO50, criteria, task_volume_multiplier=10, data_volume_multiplier=15, start_time=1000))
    # workflow_set.addWorkflow(
    #     Workflow(GENOME50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, task_volume_multiplier=100, data_volume_multiplier=100, start_time=0))
    # workflow_set.addWorkflow(Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=15, data_volume_multiplier=0, start_time=-0))
    # workflow_set.addWorkflow(Workflow(SIPHT50, criteria, task_volume_multiplier=2.5, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(GENOME50, criteria, task_volume_multiplier=0.61, data_volume_multiplier=1, start_time=0))
