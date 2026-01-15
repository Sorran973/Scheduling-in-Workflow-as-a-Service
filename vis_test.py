import random

from SchedulingModule.CJM.Model.Criteria import CostCriteria
from Utils.CSVHandler import CSVHandler
from SchedulingModule.CJM.WorkflowSet import WorkflowSet
from SchedulingModule.CJM.Workflow import Workflow

import config
from Utils.Visualization.PyvisDrawer import PyvisDrawer
from Utils.Visualization import Drawer



if __name__ == '__main__':
    # vm_types = CSVHandler.read_vms_table(Utils.Configuration.VMS_TABLE_FILE)
    vm_types = CSVHandler.read_vms_table('/Users/artembulkhak/PycharmProjects/Dissertation/Output/test/processor_table.csv')
    workflow_samples = Configuration.WORKFLOW_SAMPLES


    workflow_set = WorkflowSet()
    T = None
    # T = 38
    index_workflow_from_samples = random.randint(0, len(workflow_samples) - 1)

    # workflow = Workflow(XML_FILE=workflow_samples[index_workflow_from_samples],
    workflow = Workflow(XML_FILE=Configuration.TEST,
                        T=T,
                        vm_types=vm_types,
                        criteria=CostCriteria(min),
                        task_volume_multiplier=1,
                        data_volume_multiplier=1,
                        start_time=0)

    # workflow2 = Workflow(XML_FILE=Utils.Configuration.LIGO50,
    #                     T=T,
    #                     vm_types=vm_types,
    #                     criteria=CostCriteria(min),
    #                     task_volume_multiplier=1,
    #                     data_volume_multiplier=1,
    #                     start_time=1000)

    workflow_set.addWorkflow(workflow)
    # workflow_set.addWorkflow(workflow2)

    tasks = CSVHandler.read_task_time_table(Configuration.TASK_TIME_TABLE_FILE)
    data_transfer = CSVHandler.read_data_transfer_table(Configuration.TRANSFER_SIZE_TABLE_FILE, tasks)


    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
