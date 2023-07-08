class Edge:  # Data transfer

    id = 0

    def __init__(self, source_node, destination_node, transfer_time, transfer_size):
        self.id = Edge.id
        self.source_node = source_node
        self.destination_node = destination_node
        self.transfer_time = transfer_time
        self.transfer_size = transfer_size
        self.in_critical_path = False
        Edge.id += 1


    def __str__(self):
        return str(self.source_node.id) + \
               " --> " + str(self.destination_node.id) + \
               ", transfer_time = " + str(self.transfer_time)