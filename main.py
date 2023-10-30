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
    # workflow_set.addWorkflow(Workflow(XML_FILE, criteria))
    # workflow_set.addWorkflow(Workflow(LIGO50, criteria))


    workflow_set.addWorkflow(Workflow(MONTAGE100, criteria, 10000))
    workflow_set.addWorkflow(Workflow(CYBERSHAKE100, criteria, 15000))
    workflow_set.addWorkflow(Workflow(SIPHT100, criteria))
    workflow_set.addWorkflow(Workflow(LIGO100, criteria, 5000))
    workflow_set.addWorkflow(Workflow(GENOME100, criteria))
    workflow_set.schedule()

    # drawer: Drawer = GraphvizDrawer()
    # drawer.drawGraph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    # drawer.drawTimes(workflow_set.drawn_nodes)

    drawer: Drawer = PyvisDrawer()
    drawer.draw_graph(workflow_set.drawn_nodes, workflow_set.drawn_edges)
    drawer.draw_gantt(workflow_set.drawn_nodes)