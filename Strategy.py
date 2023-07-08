class Strategy:
    count = 0
    def __init__(self, c_p, time, criteria):
        self.id = Strategy.count
        self.c_p = c_p
        self.time = time
        self.criteria = criteria
        Strategy.count =+ 1

    def change(self, node_id, criteria, time):
        self.criteria[node_id - 1] = criteria
        self.time[node_id - 1] = time