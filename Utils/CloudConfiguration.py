from Utils.CSV.CSVHandler import CSVHandler
from Utils.Visualization.Drawer import Drawer, PyvisDrawer

MAIN_DIRECTORY = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/CloudPlatformStatistics"
VMS_TABLE_FILE = MAIN_DIRECTORY + "/cloud_vm_types.csv"

# TASK_TIME_TABLE_FILE = MAIN_DIRECTORY + "/task_time_table.csv"
# TRANSFER_SIZE_TABLE_FILE = MAIN_DIRECTORY + "/transfer_size_table.csv"
ALLOCATION_LOG_FILE = "/allocation_log.csv"
CONFIGURATION_FILE = "/configuration.csv"
GRAPHVIZ_CJM_GRAPH = "/cjm_graph.pdf"
PYVIS_CJM_GRAPH = "/pyvis_cjm_graph.html"
CJM_GANTT = "/cjm_gantt.pdf"
GANTT_FIGURES_FOLDER = "/gantt_figures"
GANTT_FIGURES_BATCHES = "/gantt_batches.pdf"
GANTT_FIGURES_BASIC = "/gantt_basic.pdf"
GANTT_FIGURES_VM_SORT = "/gantt_vm_sort.pdf"

DATA_TRANSFER_CHANNEL_SPEED = 10
DRAWER: Drawer = PyvisDrawer()

VM_TYPES = CSVHandler.read_vms_table(VMS_TABLE_FILE)
