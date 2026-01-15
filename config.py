from SchedulingModule.CJM.Model.Criteria import Criteria, AverageResourceLoadCriteria, TimeCriteria, CostCriteria
from SchedulingModule.CJM.Model.EnumWorkflow import EnumWorkflow

########################################################################################################################
TEST = 'MyTestDAXes/test.xml'
TEST0 = 'MyTestDAXes/test0.xml'
TEST_1_12 = 'MyTestDAXes/test1_12.xml'
TEST_1_13 = 'MyTestDAXes/test1_13.xml'
TEST_HEFT = 'MyTestDAXes/testHEFT.xml'

########################################################################################################################
# WORKFLOW_SAMPLES = [EnumWorkflow.MONTAGE50,EnumWorkflow.MONTAGE100, EnumWorkflow.MONTAGE200]
#                     # EnumWorkflow.LIGO400, EnumWorkflow.MONTAGE400, EnumWorkflow.CYBERSHAKE400, EnumWorkflow.GENOME400, EnumWorkflow.SIPHT400,
#                     # EnumWorkflow.LIGO500, EnumWorkflow.MONTAGE500, EnumWorkflow.CYBERSHAKE500, EnumWorkflow.GENOME500, EnumWorkflow.SIPHT500]

WORKFLOW_SAMPLES = [EnumWorkflow.LIGO50, EnumWorkflow.MONTAGE50, EnumWorkflow.CYBERSHAKE50, EnumWorkflow.GENOME50, EnumWorkflow.SIPHT50,
                    EnumWorkflow.LIGO100, EnumWorkflow.MONTAGE100, EnumWorkflow.CYBERSHAKE100, EnumWorkflow.GENOME100, EnumWorkflow.SIPHT100,
                    EnumWorkflow.LIGO200, EnumWorkflow.MONTAGE200, EnumWorkflow.CYBERSHAKE200, EnumWorkflow.GENOME200, EnumWorkflow.SIPHT200,
                    EnumWorkflow.LIGO300, EnumWorkflow.MONTAGE300, EnumWorkflow.CYBERSHAKE300, EnumWorkflow.GENOME300, EnumWorkflow.SIPHT300]
                    # EnumWorkflow.LIGO400, EnumWorkflow.MONTAGE400, EnumWorkflow.CYBERSHAKE400, EnumWorkflow.GENOME400, EnumWorkflow.SIPHT400,
                    # EnumWorkflow.LIGO500, EnumWorkflow.MONTAGE500, EnumWorkflow.CYBERSHAKE500, EnumWorkflow.GENOME500, EnumWorkflow.SIPHT500]

VMS_TABLE_FILE = "/vms_table_for_x2_new_prices.csv"
# VMS_TABLE_FILE = "/vms_table_for_x2.csv"
# VMS_TABLE_FILE = "/vms_table_for_1-2.csv"
# VMS_TABLE_FILE = "/vms_table_test.csv"

T = 2

VM_PREP_TIME = 10
VM_SHUTDOWN_TIME = 1
MULTIPLE_STRATEGIES = False

# SCHEDULING_OPTIMIZATION_CRITERIA = 'max'
SCHEDULING_OPTIMIZATION_CRITERIA = 'min'
# CJM_CRITERIA: Criteria = AverageResourceLoadCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
CJM_CRITERIA: Criteria = CostCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)
# CJM_CRITERIA: Criteria = TimeCriteria(SCHEDULING_OPTIMIZATION_CRITERIA)

# DATA_TRANSFER_CHANNEL_SPEED = 0.001
# DATA_TRANSFER_CHANNEL_SPEED = 0.015
# DATA_TRANSFER_CHANNEL_SPEED = 0.1
DATA_TRANSFER_CHANNEL_SPEED = 1.0
# DATA_TRANSFER_CHANNEL_SPEED = 10.0
# DATA_TRANSFER_CHANNEL_SPEED = 100.0

ALLOCATION_OPTIMIZATION_CRITERIA = 'min'
# ALLOCATION_OPTIMIZATION_CRITERIA = 'max' #????
# VMA_CRITERIA: Criteria = AverageResourceLoadCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)
VMA_CRITERIA: Criteria = CostCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)
# VMA_CRITERIA: Criteria = TimeCriteria(ALLOCATION_OPTIMIZATION_CRITERIA)


########################################################################################################################
WORKFLOW_EXAMPLES_DIR = "/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/"

INPUT_DIR = "/Users/artembulkhak/PycharmProjects/Dissertation/Input"
VMS_FOLDER = INPUT_DIR + "/VMsets"
VMS_TABLE_FILE_PATH = VMS_FOLDER + VMS_TABLE_FILE

OUTPUT_DIR = "/Users/artembulkhak/PycharmProjects/Dissertation/Output"
FOLDER = '/LIGO50'
TASK_TIME_TABLE_FILE = OUTPUT_DIR + "/task_time_table.csv"
TRANSFER_SIZE_TABLE_FILE = OUTPUT_DIR + "/transfer_size_table.csv"
ALLOCATION_LOG_FILE = OUTPUT_DIR + FOLDER + "/allocation_log.csv"
CONFIGURATION_FILE = OUTPUT_DIR + FOLDER + "/configuration.csv"
GANTT_FIGURES = OUTPUT_DIR + FOLDER + "/gantt_figures"
GANTT_FIGURES_BASIC = GANTT_FIGURES + "/basic.pdf"
LOG_FILE = OUTPUT_DIR + "/log.csv"

GANTT_FIGURES_BATCHES = GANTT_FIGURES + "/batches"
GANTT_FIGURES_BATCHES_FTL = GANTT_FIGURES_BATCHES + "_ftl.pdf"
GANTT_FIGURES_BATCHES_ASAP_O = GANTT_FIGURES_BATCHES + "_asap_o.pdf"
GANTT_FIGURES_BATCHES_ASAP = GANTT_FIGURES_BATCHES + "_asap.pdf"
GANTT_FIGURES_BATCHES_ASAP_MOD = GANTT_FIGURES_BATCHES + "_asap_mod.pdf"
GANTT_FIGURES_BATCHES_NEW_VM_FOR_EACH = GANTT_FIGURES_BATCHES + "_new_vm_for_each.pdf"
GANTT_FIGURES_BATCHES_TEN_BEST_VM = GANTT_FIGURES_BATCHES + "_ten_best_vm.pdf"
GANTT_FIGURES_BATCHES_EPSM = GANTT_FIGURES_BATCHES + "_epsm.pdf"

GANTT_FIGURES_VM_SORT = GANTT_FIGURES + "/vm_sort"
GANTT_FIGURES_FTL = GANTT_FIGURES_VM_SORT + "_ftl.pdf"
GANTT_FIGURES_ASAP_O = GANTT_FIGURES_VM_SORT + "_asap_o.pdf"
GANTT_FIGURES_ASAP = GANTT_FIGURES_VM_SORT + "_asap.pdf"
GANTT_FIGURES_ASAP_MOD = GANTT_FIGURES_VM_SORT + "_asap_mod.pdf"
GANTT_FIGURES_NEW_VM_FOR_EACH = GANTT_FIGURES_VM_SORT + "_new_vm_for_each.pdf"
GANTT_FIGURES_FIRST_FIT = GANTT_FIGURES_VM_SORT + "_first_fit.pdf"
GANTT_FIGURES_BEST_FIT = GANTT_FIGURES_VM_SORT + "_best_fit.pdf"
GANTT_FIGURES_RANDOM = GANTT_FIGURES_VM_SORT + "_random.pdf"

GANTT_FIGURES_HEFT = GANTT_FIGURES_VM_SORT + "_heft.pdf"
GANTT_FIGURES_EPSM = GANTT_FIGURES_VM_SORT + "_epsm.pdf"
