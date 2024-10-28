from SchedulingModule.CJM.Model.Criteria import Criteria, AverageResourceLoadCriteria, TimeCriteria

########################################################################################################################
TEST_1_12 = 'JobExamples/test1_12.xml'

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
########################################################################################################################

XML_FILE = MONTAGE50
main_directory = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/"
folder = 'MONTAGE50'
VMS_TABLE_FILE = main_directory + "/vms_table.csv"
TASK_TIME_TABLE_FILE = main_directory + "/task_time_table.csv"
TRANSFER_SIZE_TABLE_FILE = main_directory + "/transfer_size_table.csv"
ALLOCATION_LOG_FILE = main_directory + folder + "/allocation_log.csv"
CONFIGURATION_FILE = main_directory + folder + "/configuration.csv"
GANTT_FIGURES = main_directory + folder + "/gantt_figures/"
GANTT_FIGURES_BATCHES = GANTT_FIGURES + "/batches.pdf"
GANTT_FIGURES_BASIC = GANTT_FIGURES + "/basic.pdf"
GANTT_FIGURES_VM_SORT = GANTT_FIGURES + "/vm_sort.pdf"

T = None
MULTIPLE_STRATEGIES = False
# SCHEDULING_OPTIMIZATION_CRITERIA = 'max'
SCHEDULING_OPTIMIZATION_CRITERIA = 'min'

# CRITERIA: Criteria = AverageResourceLoadCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
CRITERIA: Criteria = TimeCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
# CRITERIA: Criteria = CostCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
DATA_TRANSFER_CHANNEL_SPEED = 10

ALLOCATION_OPTIMIZATION_CRITERIA = 'min'
# ALLOCATION_OPTIMIZATION_CRITERIA = 'max' #????

