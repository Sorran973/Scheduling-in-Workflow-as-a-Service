class DataTransfer:
    def __init__(self, transfer_id, task_from, task_to, transfer_size, transfer_time):
        self.transfer_id = transfer_id
        self.task_from = task_from
        self.task_to = task_to
        self.transfer_size = transfer_size
        self.transfer_time = transfer_time

    def __str__(self):
        return str(self.task_from.id) + \
               " --> " + str(self.task_to.id) + \
               ", transfer_size = " + str(self.transfer_size) + \
               ", transfer_time = " + str(self.transfer_time)