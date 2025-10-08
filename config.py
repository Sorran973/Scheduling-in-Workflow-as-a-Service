from SchedulingModule.CJM.Model.Criteria import Criteria, AverageResourceLoadCriteria, TimeCriteria, CostCriteria

########################################################################################################################
TEST = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/test.xml'
TEST_1_12 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/test1_12.xml'
TEST_1_13 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/test1_13.xml'
TEST_HEFT = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/testHEFT.xml'

MONTAGE50 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.50.0.dax'
MONTAGE100 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.100.0.dax'
MONTAGE200 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.200.0.dax'
MONTAGE300 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.300.0.dax'
MONTAGE400 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.400.0.dax'
MONTAGE500 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.500.0.dax'
MONTAGE1000 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/MONTAGE.n.1000.1.dax'

CYBERSHAKE50 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.50.0.dax'
CYBERSHAKE100 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.100.0.dax'
CYBERSHAKE200 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.200.0.dax'
CYBERSHAKE300 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.300.0.dax'
CYBERSHAKE400 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.400.0.dax'
CYBERSHAKE500 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.500.0.dax'
CYBERSHAKE1000 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/CYBERSHAKE.n.1000.0.dax'

GENOME50 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.50.0.dax'
GENOME100 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.100.0.dax'
GENOME200 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.200.0.dax'
GENOME300 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.300.0.dax'
GENOME400 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.400.0.dax'
GENOME500 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.500.0.dax'
GENOME1000 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/GENOME.n.1000.0.dax'

LIGO50 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.50.0.dax'
LIGO100 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.100.0.dax'
LIGO200 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.200.0.dax'
LIGO300 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.300.0.dax'
LIGO400 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.400.0.dax'
LIGO500 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.500.0.dax'
LIGO1000 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/LIGO.n.1000.0.dax'

SIPHT50 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.50.0.dax'
SIPHT100 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.100.0.dax'
SIPHT200 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.200.0.dax'
SIPHT300 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.300.0.dax'
SIPHT400 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.400.0.dax'
SIPHT500 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.500.0.dax'
SIPHT1000 = '/Users/artembulkhak/PycharmProjects/Dissertation/JobExamples/SIPHT.n.1000.0.dax'
########################################################################################################################
WORKFLOW_SAMPLES = [LIGO50]
# WORKFLOW_SAMPLES = [LIGO50, MONTAGE50, CYBERSHAKE50, GENOME50, SIPHT50,
#                     LIGO100, MONTAGE100, CYBERSHAKE100, GENOME100, SIPHT100]
                    # LIGO200, MONTAGE200, CYBERSHAKE200, GENOME200, SIPHT200,
                    # LIGO300, MONTAGE300, CYBERSHAKE300, GENOME300, SIPHT300]
                    # LIGO400, MONTAGE400, CYBERSHAKE400, GENOME400, SIPHT400,
                    # LIGO500, MONTAGE500, CYBERSHAKE500, GENOME500, SIPHT500]

# VMS_TABLE_FILE = "/vms_table_5_base.csv"
VMS_TABLE_FILE = "/vms_table_5.csv"
# VMS_TABLE_FILE = "/vms_table_n.csv"

T = 917

VM_PREP_TIME = 10
VM_SHUTDOWN_TIME = 1
MULTIPLE_STRATEGIES = True

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


########################################################################################################################
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

GANTT_FIGURES_VM_SORT = GANTT_FIGURES + "/vm_sort"
GANTT_FIGURES_FTL = GANTT_FIGURES_VM_SORT + "_ftl.pdf"
GANTT_FIGURES_ASAP_O = GANTT_FIGURES_VM_SORT + "_asap_o.pdf"
GANTT_FIGURES_ASAP = GANTT_FIGURES_VM_SORT + "_asap.pdf"
GANTT_FIGURES_ASAP_MOD = GANTT_FIGURES_VM_SORT + "_asap_mod.pdf"
GANTT_FIGURES_NEW_VM_FOR_EACH = GANTT_FIGURES_VM_SORT + "_new_vm_for_each.pdf"
GANTT_FIGURES_HEFT = GANTT_FIGURES_VM_SORT + "_heft.pdf"