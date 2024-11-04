from AllocationModule.Model.DataTransfer import DataTransfer
from AllocationModule.Model.Task import Task


class ExchangeHandler:
    @staticmethod
    def exchange_info_from_cjm(nodes, edges):
        tasks = []
        for node in nodes:
            tasks.append(Task(node.id, node.name, node.volume, node.start_time, node.finish_time))

        for edge in edges:
            task_from = tasks[int(edge.node_from.id)]
            task_to = tasks[int(edge.node_to.id)]
            data_transfer = DataTransfer(edge.id, task_from, task_to, edge.transfer_size)
            task_from.addOutputTransfer(data_transfer)
            task_to.add_input_transfer(data_transfer)

        return tasks
