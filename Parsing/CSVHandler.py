import csv

from FTL.Task import Task
from FTL.VMType import VMType

PROCESSOR_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/processor_table.csv'
TASK_TIME_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/task_time_table.csv'
TRANSFER_SIZE_TABLE_FILE = '/Users/artembulkhak/PycharmProjects/Dissertation/Output/transfer_size_table.csv'


PROCESSOR_TABLE = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/test/processor_table.csv"
TASK_TIME_TABLE_FILE = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/test/task_time_table.csv"
TRANSFER_SIZE_TABLE_FILE = "/Users/artembulkhak/PycharmProjects/Dissertation/Output/test/transfer_size_table.csv"

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
        CSVHandler.write_processors_table(processor_table_performance=workflow.processor_table_performance)
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
                       fieldnames[1]: str(edge.source_node.id) + '/' + edge.source_node.name,
                       fieldnames[2]: str(edge.destination_node.id) + '/' + edge.destination_node.name,
                       fieldnames[3]: edge.transfer_size}
                writer.writerow(row)



    @staticmethod
    def read_processors_table():
        vm_types = []
        with open(PROCESSOR_TABLE, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                # vms.append(VMType(int(row[0]), float(row[1]), float(row[1])))
                vm_types.append(VMType(row[0], float(row[1]), float(row[1])))

        return vm_types


    @staticmethod
    def read_task_time_table():
        tasks = []
        with open(TASK_TIME_TABLE_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            headers = next(reader)
            for row in reader:
                if row[3] != '':
                    task = Task(int(row[0]), row[1], float(row[2]), float(row[3]), float(row[4]))
                else:
                    task = Task(int(row[0]), row[1], float(row[2]))

                tasks.append(task)

        return tasks


    # @staticmethod
    # def read_data_transfer_table(data_transfer):
    #     data_transfer = []
    #     with open(TRANSFER_SIZE_TABLE_FILE, newline='') as csvfile:
    #         reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    #         headers = next(reader)
    #         for row in reader:
    #             vms.append(VM(int(row[0]), float(row[1]), float(row[1])))
    #
    #     return data_transfer

