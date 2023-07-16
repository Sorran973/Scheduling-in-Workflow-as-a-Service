class Node:

    id = 0

    def __init__(self, name, runtime):
        self.id = Node.id
        self.name = name
        self.runtime = runtime
        self.start_time = None
        self.finish_time = None
        self.visited = False
        self.in_critical_path = False
        self.edges = []
        self.color = 'black'
        self.critical_paths = [] # all critical paths of the node (start from that node) = [length, [obj(nodes and edges)], ...]
        self.input = []
        self.input_size = 0
        self.output = []
        self.output_size = 0
        Node.id += 1


    def add_file(self, file):
        if file.link == 'input':
            self.input.append(file)
            self.input_size += file.size
        else:
            self.output.append(file)
            self.output_size += file.size


    def add_edge(self, edge):
        self.edges.append(edge)

    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", name = " + self.name + \
               ", runtime = " + str(self.runtime)