import pandas as pd

from SchedulingModule.CJM.Model.Criteria import Criteria, AverageResourceLoadCriteria, CostCriteria, TimeCriteria
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow
from AllocationModule.AllocationModule import AllocationModule
from Parsing.CSVHandler import CSVHandler
from Visualization.GraphvizDrawer import GraphvizDrawer
from Visualization.PyvisDrawer import PyvisDrawer, rand_color

from Visualization import Drawer

if __name__ == '__main__':

    MONTAGE50 = 'JobExamples/MONTAGE.n.50.0.dax'
    MONTAGE100 = 'JobExamples/MONTAGE.n.100.0.dax'
    MONTAGE500 = 'JobExamples/MONTAGE.n.500.0.dax'
    MONTAGE1000 = 'JobExamples/MONTAGE.n.1000.1.dax'

    CYBERSHAKE50 = 'JobExamples/CYBERSHAKE.n.50.0.dax'
    CYBERSHAKE100 = 'JobExamples/CYBERSHAKE.n.100.0.dax'
    CYBERSHAKE500 = 'JobExamples/CYBERSHAKE.n.500.0.dax'

    GENOME50 = 'JobExamples/GENOME.n.50.0.dax'
    GENOME100 = 'JobExamples/GENOME.n.100.0.dax'
    GENOME500 = 'JobExamples/GENOME.n.500.0.dax'

    LIGO50 = 'JobExamples/LIGO.n.50.0.dax'
    LIGO100 = 'JobExamples/LIGO.n.100.0.dax'
    LIGO500 = 'JobExamples/LIGO.n.500.0.dax'

    SIPHT50 = 'JobExamples/SIPHT.n.50.0.dax'
    SIPHT100 = 'JobExamples/SIPHT.n.100.0.dax'
    SIPHT500 = 'JobExamples/SIPHT.n.500.0.dax'

    #####################################################
    ################# SCHEDULING MODULE #################
    #####################################################

    XML_FILE = 'JobExamples/test1_12.xml'
    main_directory = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/"
    # folder = 'test1_11'
    folder = 'MONTAGEn50'
    # VMS_TABLE_FILE = main_directory + folder + "/vms_table.csv"
    VMS_TABLE_FILE = main_directory + folder + "/processor_table.csv"
    multiple_strategies = True
    OPTIMIZATION_CRITERIA = 'max'
    # OPTIMIZATION_CRITERIA = 'min'
    T = 214
    criteria: Criteria = AverageResourceLoadCriteria(OPTIMIZATION_CRITERIA)
    # criteria: Criteria = TimeCriteria(OPTIMIZATION_CRITERIA)
    # criteria: Criteria = CostCriteria(OPTIMIZATION_CRITERIA)
    DATA_TRANSFER_SPEED = 500

    workflow_set = WorkflowSet()
    vm_types = CSVHandler.read_vms_table(VMS_TABLE_FILE)
    workflow_set.addWorkflow(Workflow(MONTAGE1000, T, vm_types, criteria, multiple_strategies, 1, 1))
    # workflow_set.addWorkflow(Workflow(MONTAGE1000, T, vm_types, criteria, 1, 1))

    # workflow_set.addWorkflow(Workflow(MONTAGE1000, vm_types, criteria, 1, 1))
    # workflow_set.addWorkflow(Workflow(XML_FILE, T, vm_types, criteria, 1, 1))
    # workflow_set.addWorkflow(Workflow(LIGO50, T, vm_types, criteria, 1, 1))
    # workflow_set.addWorkflow(WorkflowMulti(LIGO50, T, vm_types, criteria, True, 1, 1))

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

    import time

    start_time = time.time()
    workflow_set.schedule()
    print("--- %s seconds ---" % (time.time() - start_time))

    drawer: Drawer = PyvisDrawer()
    # drawer2: Drawer = GraphvizDrawer()
    # drawer2.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    drawer.draw_gantt(workflow_set.drawn_nodes)
    drawer.draw_new_gantt(workflow_set.drawn_nodes)

    #####################################################
    ################# ALLOCATION MODULE #################
    #####################################################

    # DATA_TRANSFER_SPEED = 500
    # OPTIMIZATION_CRITERIA = 'MIN'
    # main_directory = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/"
    # folder = 'MONTAGEn50'
    # # folder = 'mix1_1 (4 workflow montage with 50 nodes) (volume x10)'
    # VMS_TABLE_FILE = main_directory + folder + "/processor_table.csv"
    # TASK_TIME_TABLE_FILE = main_directory + folder + "/task_time_table.csv"
    # TRANSFER_SIZE_TABLE_FILE = main_directory + folder + "/transfer_size_table.csv"
    # ALLOCATION_LOG_FILE = main_directory + folder + "/allocation_log.csv"
    #
    # vm_types = CSVHandler.read_vms_table(VMS_TABLE_FILE)
    # tasks = CSVHandler.read_task_time_table(TASK_TIME_TABLE_FILE)
    # data_transfer = CSVHandler.read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks)
    #
    # allocation = AllocationModule(vm_types, tasks, data_transfer)
    #
    # time = 0
    # batches = allocation.formParallelBatches(time)  # FTL algorithm
    # drawer.draw_batches_gantt(allocation.tasks)
    #
    # allocation.setDataTransferSpeed(DATA_TRANSFER_SPEED)
    # allocation.setOptimizationCriteria(OPTIMIZATION_CRITERIA)
    # allocation.vma(batches)
    #
    # log = allocation.log
    # CSVHandler.write_allocation_logfile(ALLOCATION_LOG_FILE, log)
    # print(log.allocation_cost.sum())
    #
    # color = log[["vm_id"]]
    # color = color.drop_duplicates()
    # color["color"] = color.apply(lambda x: rand_color(x), axis=1)
    # log = pd.merge(log, color, on='vm_id', how='left')
    #
    # drawer.draw_result_gantt(log)
    # log = log.sort_values(["vm_id", "vm_end"])
    # drawer.draw_result_gantt(log)
