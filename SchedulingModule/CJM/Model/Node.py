import math

class Node:

    id = 0

    def __init__(self, name, volume, runtime):
        self.id = Node.id
        self.name = name
        self.volume = volume
        self.runtime = runtime
        self.start_time = None
        self.finish_time = None
        self.EST = None
        self.LST = None
        self.EFT = None
        self.LFT = None
        self.visited = False
        self.in_critical_path = False
        self.edges_from = []          # edges from other nodes into this node
        self.edges_to = []          # edges from this node to other nodes
        self.color = 'black'
        self.critical_paths = [] # all critical paths of the node (start from that node) = [length, [obj(nodes and edges)], ...]
        self.input = []
        self.input_size = 0
        self.input_time = 0
        self.input_register = []
        self.input_register_size = 0
        self.input_register_time = 0
        self.output = []
        self.output_size = 0
        self.output_time = 0
        self.output_register = []
        self.output_register_size = 0
        self.output_register_time = 0
        self.weight = None
        self.extra_time = None
        self.budget = None
        Node.id += 1


    def add_file_register(self, file):
        if file.link == 'input':
            if file.register == 'true':
                self.input_register.append(file)
                self.input_register_size += file.size
            else:
                self.input.append(file)
                self.input_size += file.size
        else:
            if file.register == 'true':
                self.output_register.append(file)
                self.output_register_size += file.size
            else:
                self.output.append(file)
                self.output_size += file.size

    def add_file(self, file):
        if file.link == 'input':
            self.input.append(file)
            self.input_size += file.size
        else:
            self.output.append(file)
            self.output_size += file.size


    def add_edge_from(self, edge):
        self.edges_from.append(edge)

    def add_edge_to(self, edge):
        self.edges_to.append(edge)

    def calculate_transfer_time(self, data_transfer_channel):
        self.input_time = math.ceil(self.input_size / data_transfer_channel)
        self.output_time = math.ceil(self.output_size / data_transfer_channel)

        self.input_register_time = math.ceil(self.input_register_size / data_transfer_channel)
        self.output_register_time = math.ceil(self.output_register_size / data_transfer_channel)


    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", name = " + self.name + \
               ", volume = " + str(self.volume) + \
               ", runtime = " + str(self.runtime)