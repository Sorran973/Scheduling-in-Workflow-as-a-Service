from Visualization.GraphvizDrawer import GraphvizDrawer
from Visualization.PyvisDrawer import PyvisDrawer

from Workflow import Workflow
import Drawer
from Criteria import *
from WorkflowSet import WorkflowSet


if __name__ == '__main__':
    XML_FILE = 'JobExamples/test1_11.xml'

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



    criteria: Criteria = AverageResourceLoadCriteria('max')

    workflow_set = WorkflowSet()
    workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, 1, 1))
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
    #     Workflow(MONTAGE50, criteria, task_volume_multiplier=200, data_volume_multiplier=200, start_time=0))
    # workflow_set.addWorkflow(
    #     Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))
    # workflow_set.addWorkflow(
    #     Workflow(SIPHT50, criteria, task_volume_multiplier=5, data_volume_multiplier=5, start_time=2000))
    # workflow_set.addWorkflow(
    #     Workflow(LIGO50, criteria, task_volume_multiplier=15, data_volume_multiplier=15, start_time=1000))
    # workflow_set.addWorkflow(
    #     Workflow(GENOME50, criteria, task_volume_multiplier=1, data_volume_multiplier=1, start_time=0))

    # workflow_set.addWorkflow(Workflow(MONTAGE50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(CYBERSHAKE50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(SIPHT50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))
    # workflow_set.addWorkflow(Workflow(GENOME50, criteria, task_volume_multiplier=10, data_volume_multiplier=10, start_time=0))

    workflow_set.schedule()


    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    drawer.draw_gantt(workflow_set.drawn_nodes)