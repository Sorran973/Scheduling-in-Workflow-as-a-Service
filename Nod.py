class Node:  # Job
    def __init__(self, id, name, runtime):
        self.id = id
        self.name = name
        self.runtime = runtime
        self.result_time = None
        self.start_time = None
        self.deadline = None
        self.result_C = None
        self.strategies = []

    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", name = " + self.name + \
               ", runtime = " + str(self.runtime)