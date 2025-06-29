from SchedulingModule.CJM.Model.Criteria import Criteria, AverageResourceLoadCriteria, TimeCriteria, CostCriteria

########################################################################################################################
TEST = 'JobExamples/test.xml'
TEST_1_12 = 'JobExamples/test1_12.xml'
TEST_1_13 = 'JobExamples/test1_13.xml'

MONTAGE50 = 'JobExamples/MONTAGE.n.50.0.dax'
MONTAGE100 = 'JobExamples/MONTAGE.n.100.0.dax'
MONTAGE200 = 'JobExamples/MONTAGE.n.200.0.dax'
MONTAGE300 = 'JobExamples/MONTAGE.n.300.0.dax'
MONTAGE400 = 'JobExamples/MONTAGE.n.400.0.dax'
MONTAGE500 = 'JobExamples/MONTAGE.n.500.0.dax'
MONTAGE1000 = 'JobExamples/MONTAGE.n.1000.1.dax'

CYBERSHAKE50 = 'JobExamples/CYBERSHAKE.n.50.0.dax'
CYBERSHAKE100 = 'JobExamples/CYBERSHAKE.n.100.0.dax'
CYBERSHAKE200 = 'JobExamples/CYBERSHAKE.n.200.0.dax'
CYBERSHAKE300 = 'JobExamples/CYBERSHAKE.n.300.0.dax'
CYBERSHAKE400 = 'JobExamples/CYBERSHAKE.n.400.0.dax'
CYBERSHAKE500 = 'JobExamples/CYBERSHAKE.n.500.0.dax'

GENOME50 = 'JobExamples/GENOME.n.50.0.dax'
GENOME100 = 'JobExamples/GENOME.n.100.0.dax'
GENOME200 = 'JobExamples/GENOME.n.200.0.dax'
GENOME300 = 'JobExamples/GENOME.n.300.0.dax'
GENOME400 = 'JobExamples/GENOME.n.400.0.dax'
GENOME500 = 'JobExamples/GENOME.n.500.0.dax'

LIGO50 = 'JobExamples/LIGO.n.50.0.dax'
LIGO100 = 'JobExamples/LIGO.n.100.0.dax'
LIGO200 = 'JobExamples/LIGO.n.200.0.dax'
LIGO300 = 'JobExamples/LIGO.n.300.0.dax'
LIGO500 = 'JobExamples/LIGO.n.500.0.dax'

SIPHT50 = 'JobExamples/SIPHT.n.50.0.dax'
SIPHT100 = 'JobExamples/SIPHT.n.100.0.dax'
SIPHT200 = 'JobExamples/SIPHT.n.200.0.dax'
SIPHT300 = 'JobExamples/SIPHT.n.300.0.dax'
SIPHT400 = 'JobExamples/SIPHT.n.400.0.dax'
SIPHT500 = 'JobExamples/SIPHT.n.500.0.dax'

# WORKFLOW_SAMPLES = [LIGO50]
WORKFLOW_SAMPLES = [LIGO50, MONTAGE50, CYBERSHAKE50, GENOME50, SIPHT50]
# WORKFLOW_SAMPLES = [LIGO50, MONTAGE50, CYBERSHAKE50, GENOME50, SIPHT50,
#                     LIGO100, MONTAGE100, CYBERSHAKE100, GENOME100, SIPHT100,
#                     LIGO200, MONTAGE200, CYBERSHAKE200, GENOME200, SIPHT200,
#                     LIGO300, MONTAGE300, CYBERSHAKE300, GENOME300, SIPHT300]
########################################################################################################################

XML_FILE = LIGO50
main_directory = "/Users/artembulkhak/PycharmProjects/Dissertation/Output"
folder = '/LIGO50'
VMS_TABLE_FILE = main_directory + "/vms_table.csv"
TASK_TIME_TABLE_FILE = main_directory + "/task_time_table.csv"
TRANSFER_SIZE_TABLE_FILE = main_directory + "/transfer_size_table.csv"
ALLOCATION_LOG_FILE = main_directory + folder + "/allocation_log.csv"
CONFIGURATION_FILE = main_directory + folder + "/configuration.csv"
GANTT_FIGURES = main_directory + folder + "/gantt_figures"
GANTT_FIGURES_BASIC = GANTT_FIGURES + "/basic.pdf"

GANTT_FIGURES_BATCHES = GANTT_FIGURES + "/batches"
GANTT_FIGURES_BATCHES_FTL = GANTT_FIGURES_BATCHES + "_ftl.pdf"
GANTT_FIGURES_BATCHES_ASAP = GANTT_FIGURES_BATCHES + "_asap.pdf"
GANTT_FIGURES_BATCHES_ASAP_MOD = GANTT_FIGURES_BATCHES + "_asap_mod.pdf"
GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH = GANTT_FIGURES_BATCHES + "_new_vm_for_each.pdf"

GANTT_FIGURES_VM_SORT = GANTT_FIGURES + "/vm_sort"
GANTT_FIGURES_FTL = GANTT_FIGURES_VM_SORT + "_ftl.pdf"
GANTT_FIGURES_ASAP = GANTT_FIGURES_VM_SORT + "_asap.pdf"
GANTT_FIGURES_ASAP_MOD = GANTT_FIGURES_VM_SORT + "_asap_mod.pdf"
GANTT_FIGURES_NEW_VM_FOR_EACH = GANTT_FIGURES_VM_SORT + "_new_vm_for_each.pdf"


T = None
VM_PREP_TIME = 0
VM_SHUTDOWN_TIME = 0
MULTIPLE_STRATEGIES = False
# SCHEDULING_OPTIMIZATION_CRITERIA = 'max'
SCHEDULING_OPTIMIZATION_CRITERIA = 'min'
# CJM_CRITERIA: Criteria = AverageResourceLoadCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
# CJM_CRITERIA: Criteria = TimeCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
CJM_CRITERIA: Criteria = CostCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)

# DATA_TRANSFER_CHANNEL_SPEED = 0.001
# DATA_TRANSFER_CHANNEL_SPEED = 0.015
# DATA_TRANSFER_CHANNEL_SPEED = 0.1
DATA_TRANSFER_CHANNEL_SPEED = 1.0
# DATA_TRANSFER_CHANNEL_SPEED = 10.0
# DATA_TRANSFER_CHANNEL_SPEED = 100.0

ALLOCATION_OPTIMIZATION_CRITERIA = 'min'
# ALLOCATION_OPTIMIZATION_CRITERIA = 'max' #????
# VMA_CRITERIA: Criteria = AverageResourceLoadCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)
# VMA_CRITERIA: Criteria = TimeCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)
VMA_CRITERIA: Criteria = CostCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)