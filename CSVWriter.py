import csv

class CSVWriter:

    @staticmethod
    def write_all_tables(job):
        CSVWriter.write_current_processor_table(file_name='processor_table.csv', nodes=job.nodes, processor_table=job.processor_table)
        CSVWriter.write_task_times_table(file_name='task_times_table.csv', nodes=job.nodes)
        CSVWriter.write_transfer_size_table(file_name='transfer_size_table.csv', edges=job.edges)

    @staticmethod
    def write_current_processor_table(file_name, nodes, processor_table):

        del nodes[-1:]  # delete entry node
        del nodes[0:1]  # delete finish node

        with open('Output/' + file_name, 'w', newline='') as f:
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


    @staticmethod
    def write_new_processor_table(file_name, nodes):

        del nodes[-1:]  # delete entry node
        del nodes[0:1]  # delete finish node

        with open('Output/' + file_name, 'w', newline='') as f:
            fieldnames = []
            for node in nodes:
                fieldnames.append(str(node.id) + "/" + node.name)

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for i in range(1, 6):
                row = {}
                for j in range(len(nodes)):
                    row[fieldnames[j]] = str(nodes[j].runtime * i)

                writer.writerow(row)


    @staticmethod
    def write_task_times_table(file_name, nodes):

        # del nodes[-1:]  # delete entry node
        # del nodes[0:1]  # delete finish node

        with open('Output/' + file_name, 'w', newline='') as f:
            fieldnames = ['task_id', 'task_name', 'start_time', 'finish_time']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for node in nodes:
                row = {fieldnames[0] : node.id,
                       fieldnames[1] : node.name,
                       fieldnames[2] : node.start_time,
                       fieldnames[3] : node.finish_time}
                writer.writerow(row)


    @staticmethod
    def write_transfer_size_table(file_name, edges):

        with open('Output/' + file_name, 'w', newline='') as f:
            fieldnames = ['transfer_id', 'task_from', 'task_to', 'transfer_size']

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for edge in edges:
                row = {fieldnames[0] : edge.id,
                       fieldnames[1] : str(edge.source_node.id) + '/' + edge.source_node.name,
                       fieldnames[2] : str(edge.destination_node.id) + '/' + edge.destination_node.name,
                       fieldnames[3] : edge.transfer_size}
                writer.writerow(row)