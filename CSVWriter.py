import csv

PROCESSOR_TABLE_FILE = 'Output/processor_table.csv'
TASK_TIME_TABLE_FILE = 'Output/task_time_table.csv'
TRANSFER_SIZE_TABLE_FILE = 'Output/transfer_size_table.csv'

class CSVWriter:

    @staticmethod
    def write_headers():

        f = open(PROCESSOR_TABLE_FILE, 'w')
        f.close()

        with open(TASK_TIME_TABLE_FILE, 'w') as f:
            fieldnames = ['task_id', 'task_name', 'start_time', 'finish_time']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

        with open(TRANSFER_SIZE_TABLE_FILE, 'w') as f:
            fieldnames = ['transfer_id', 'task_from', 'task_to', 'transfer_size']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


    @staticmethod
    def write_all_tables(job):
        CSVWriter.write_processors_table(nodes=job.nodes, processor_table=job.processor_table)
        CSVWriter.write_task_times_table(nodes=job.nodes)
        CSVWriter.write_transfer_sizes_table(edges=job.edges)


    @staticmethod
    def write_processors_table(nodes, processor_table):

        del nodes[-1:]  # delete entry node
        del nodes[0:1]  # delete finish node

        with open(PROCESSOR_TABLE_FILE, 'a', newline='') as f:
            fieldnames = []
            for node in nodes:
                fieldnames.append(str(node.id) + "/" + node.name)

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(len(processor_table)):
                row = {}
                for j in range(len(processor_table[i])):
                    row[fieldnames[j]] = str(processor_table[i][j])

                writer.writerow(row)
            f.write('\n')

    @staticmethod
    def write_task_times_table(nodes):

        with open(TASK_TIME_TABLE_FILE, 'a') as f:
            fieldnames = ['task_id', 'task_name', 'start_time', 'finish_time']

            writer = csv.DictWriter(f, fieldnames=fieldnames)

            for node in nodes:
                row = {fieldnames[0]: node.id,
                       fieldnames[1]: node.name,
                       fieldnames[2]: node.start_time,
                       fieldnames[3]: node.finish_time}
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