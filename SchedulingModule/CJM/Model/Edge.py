import math


class Edge:  # Data transfer

    id = 0

    def __init__(self, node_from, node_to, files, data_transfer_channel_speed):
        self.id = Edge.id
        self.node_from = node_from
        self.node_to = node_to
        self.files = files
        self.transfer_size = sum(map(lambda file: file.size, files))
        self.transfer_time = math.ceil(self.transfer_size / data_transfer_channel_speed)
        self.in_critical_path = False
        Edge.id += 1


    def __str__(self):
        return str(self.node_from.id) + \
               " --> " + str(self.node_to.id) + \
               ", transfer_size = " + str(self.transfer_size) + \
               ", transfer_time = " + str(self.transfer_time)
