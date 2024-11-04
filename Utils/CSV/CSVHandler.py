import csv

from AllocationModule.Model.DataTransfer import DataTransfer
from AllocationModule.Model.Task import Task
from AllocationModule.Model.VMType import VMType
from SchedulingModule.CJM.Model.Edge import Edge
import Utils.CloudConfiguration

PROCESSOR_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/processor_table.csv'
TASK_TIME_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/task_time_table.csv'
TRANSFER_SIZE_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/transfer_size_table.csv'


class CSVHandler:

    @staticmethod
    def write_headers():
        with open(TASK_TIME_TABLE_FILE, 'w') as f:
            fieldnames = ['task_id', 'task_name', 'volume', 'start_time', 'finish_time']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

        with open(TRANSFER_SIZE_TABLE_FILE, 'w') as f:
            fieldnames = ['transfer_id', 'task_from', 'task_to', 'transfer_size']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    @staticmethod
    def write_all_tables(workflow):
        CSVHandler.write_task_times_table(nodes=workflow.nodes)
        CSVHandler.write_transfer_sizes_table(edges=workflow.edges)

    @staticmethod
    def write_processors_table(processor_table_performance):
        with open(PROCESSOR_TABLE_FILE, 'w', newline='') as f:
            fieldnames = ['VM_type', 'performance']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(len(processor_table_performance)):
                row = {fieldnames[0]: i,
                       fieldnames[1]: processor_table_performance[i]}
                writer.writerow(row)

    @staticmethod
    def write_task_times_table(nodes):
        with open(TASK_TIME_TABLE_FILE, 'a') as f:
            fieldnames = ['task_id', 'task_name', 'volume', 'start_time', 'finish_time']

            writer = csv.DictWriter(f, fieldnames=fieldnames)

            for node in nodes:
                row = {fieldnames[0]: node.id,
                       fieldnames[1]: node.name,
                       fieldnames[2]: node.volume,
                       fieldnames[3]: node.start_time,
                       fieldnames[4]: node.finish_time}
                writer.writerow(row)

    @staticmethod
    def write_transfer_sizes_table(edges):
        with open(TRANSFER_SIZE_TABLE_FILE, 'a') as f:
            fieldnames = ['transfer_id', 'task_from', 'task_to', 'transfer_size']

            writer = csv.DictWriter(f, fieldnames=fieldnames)

            for edge in edges:
                row = {fieldnames[0]: edge.id,
                       fieldnames[1]: str(edge.node_from.id) + '/' + edge.node_from.name,
                       fieldnames[2]: str(edge.node_to.id) + '/' + edge.node_to.name,
                       fieldnames[3]: edge.transfer_size}
                writer.writerow(row)

    @staticmethod
    def read_vms_table(VMS_TABLE_FILE):
        vm_types = []
        with open(VMS_TABLE_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                vm_types.append(VMType(row[0], float(row[1]), float(row[2])))

        return vm_types

    @staticmethod
    def read_from_nodes(nodes):
        tasks = []
        for node in nodes:
            task = Task(node.id, node.name, node.volume, node.start_time, node.finish_time)
            tasks.append(task)

        for i, node in enumerate(nodes):
            task = tasks[i]
            for edge in node.edges:
                task.input_transfers.append(Edge(tasks[edge.node_from.id],
                                                 tasks[edge.node_to.id],
                                                 edge.files,
                                                 Utils.Configuration.DATA_TRANSFER_CHANNEL_SPEED))
            task.input_transfers = node.edges
            task.input = node.input
            task.input_size = node.input_size
            task.input_time = node.input_time
            task.output = node.output
            task.output_size = node.output_size
            task.output_time = node.output_time

        return tasks

    @staticmethod
    def read_task_time_table(TASK_TIME_TABLE_FILE):
        tasks = []
        with open(TASK_TIME_TABLE_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                task = Task(int(row[0]), row[1], float(row[2]), float(row[3]), float(row[4]))
                tasks.append(task)

        return tasks

    @staticmethod
    def read_data_transfer_table(TRANSFER_SIZE_TABLE_FILE, tasks):
        data_transfer = []
        with open(TRANSFER_SIZE_TABLE_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                task_from_id = row[1].split('/')[0]
                task_to_id = row[2].split('/')[0]
                transfer = DataTransfer(int(row[0]), tasks[int(task_from_id)], tasks[int(task_to_id)], float(row[3]))
                data_transfer.append(transfer)
                transfer.task_from.addOutputTransfer(transfer)
                transfer.task_to.add_input_transfer(transfer)

        return data_transfer

    @staticmethod
    def write_configuration_file(CONFIGURATION_FILE):
        with open(CONFIGURATION_FILE, 'w') as f:
            fieldnames = ['multiple_strategies', 'scheduling_criteria', 'scheduling_optimization_criteria', 'T',
                          'data_transfer_channel_speed', 'allocation_optimization_criteria']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            file_row = {fieldnames[0]: Utils.Configuration.MULTIPLE_STRATEGIES,
                        fieldnames[1]: Utils.Configuration.CRITERIA,
                        fieldnames[2]: Utils.Configuration.SCHEDULING_OPTIMIZATION_CRITERIA,
                        fieldnames[3]: Utils.Configuration.T,
                        fieldnames[4]: Utils.Configuration.DATA_TRANSFER_CHANNEL_SPEED,
                        fieldnames[5]: Utils.Configuration.ALLOCATION_OPTIMIZATION_CRITERIA}
            writer.writerow(file_row)



    @staticmethod
    def write_allocation_logfile(ALLOCATION_LOG_FILE, log):

        with open(ALLOCATION_LOG_FILE, 'w') as f:
            fieldnames = ['vm_id', 'vm_type', 'task_id', 'task_name', 'task_batch', 'task_start',
                          'task_end', 'interval', 'vm_start', 'input_data', 'task_allocation_start',
                          'task_allocation_end', 'output_data', 'vm_end', 'allocation_cost']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for index, row in log.iterrows():
                file_row = {fieldnames[0]: row.vm_id,
                            fieldnames[1]: row.vm_type,
                            fieldnames[2]: row.task_id,
                            fieldnames[3]: row.task_name,
                            fieldnames[4]: row.task_batch,
                            fieldnames[5]: row.task_start,
                            fieldnames[6]: row.task_end,
                            fieldnames[7]: row.interval,
                            fieldnames[8]: row.vm_start,
                            fieldnames[9]: row.input_data,
                            fieldnames[10]: row.task_allocation_start,
                            fieldnames[11]: row.task_allocation_end,
                            fieldnames[12]: row.output_data,
                            fieldnames[13]: row.vm_end,
                            fieldnames[14]: row.allocation_cost}
                writer.writerow(file_row)
