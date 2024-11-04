import os

from AllocationModule.Allocation import AllocationModule
from Utils.CSV.CSVHandler import CSVHandler
from Utils.ExchangeHandler import ExchangeHandler
import Utils.CloudConfiguration


class CloudPlatform:
    def __init__(self):
        self.time = 0
        self.workflows = []
        self.allocations = []
        self.vm_types = Utils.CloudConfiguration.VM_TYPES
        self.DATA_TRANSFER_CHANNEL_SPEED = Utils.CloudConfiguration.DATA_TRANSFER_CHANNEL_SPEED
        self.drawer = Utils.CloudConfiguration.DRAWER

    def add_workflow(self, workflow, allocation_optimization_criteria):
        workflow.allocation_optimization_criteria = allocation_optimization_criteria
        self.workflows.append(workflow)

    def run(self):
        for workflow in self.workflows:
            ################# SCHEDULING #################
            workflow.schedule()
            self.time += workflow.global_timer

            ############# MODULES EXCHANGING #############
            cjm_nodes = workflow.nodes
            cjm_edges = workflow.edges
            tasks = ExchangeHandler.exchange_info_from_cjm(cjm_nodes, cjm_edges)

            ################# ALLOCATION #################
            allocation = AllocationModule(self.vm_types, tasks)
            allocation.setDataTransferSpeed(self.DATA_TRANSFER_CHANNEL_SPEED)
            allocation.setOptimizationCriteria(workflow.allocation_optimization_criteria)
            #TODO: track time parameter from very cjm
            # time = 0
            allocation.formParallelBatches(self.time)  # FTL algorithm
            allocation.vma(allocation.batches)

            self.allocations.append(allocation)

    def get_cloud_result(self):
        for i, allocated_workflow in enumerate(self.allocations):
            folder_name = Utils.CloudConfiguration.MAIN_DIRECTORY + "/{0}-".format(i) + self.workflows[i].xml_file_name
            gantt_folder_name = folder_name + Utils.CloudConfiguration.GANTT_FIGURES_FOLDER
            print("/{0}-".format(i) + self.workflows[i].xml_file_name)

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            if not os.path.exists(gantt_folder_name):
                os.makedirs(gantt_folder_name)

            log = allocated_workflow.log
            CSVHandler.write_allocation_logfile(folder_name + Utils.CloudConfiguration.ALLOCATION_LOG_FILE, log)
            print("Total Cost: " + str(log.allocation_cost.sum()))
            print("Total Time: " + str(log.vm_end.max()))
            self.drawer.draw_batches_gantt(allocated_workflow.tasks,
                                           gantt_folder_name + Utils.CloudConfiguration.GANTT_FIGURES_BATCHES)
            self.drawer.draw_allocation_result_gantt(log,
                                                     gantt_folder_name + Utils.CloudConfiguration.GANTT_FIGURES_BASIC,
                                                     gantt_folder_name + Utils.CloudConfiguration.GANTT_FIGURES_VM_SORT)


