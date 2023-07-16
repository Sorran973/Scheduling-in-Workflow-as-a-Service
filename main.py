from Job import Job
from Visualization import Drawer
from Criteria import *
from Visualization.Drawer import GraphvizDrawer
from Workflow import Workflow


if __name__ == '__main__':
    # XML_FILE = 'JobExamples/test1_11.xml'
    # XML_FILE = 'JobExamples/Montage_25.xml'
    XML_FILE = 'JobExamples/Montage_100.xml'
    # XML_FILE = 'JobExamples/Epigenomics_25.xml'
    # XML_FILE2 = 'JobExamples/CyberShake_30.xml'

    criteria: Criteria = AverageResourceLoad('max')

    workflow = Workflow()
    workflow.addJob(Job(XML_FILE, criteria))
    workflow.addJob(Job(XML_FILE, criteria, 50))
    workflow.addJob(Job(XML_FILE, criteria, 150))
    workflow.addJob(Job(XML_FILE, criteria, 300))
    workflow.schedule()

    drawer: Drawer = GraphvizDrawer()
    drawer.draw(workflow.draw_nodes, workflow.draw_edges)
