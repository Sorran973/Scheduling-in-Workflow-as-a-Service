import copy
import math


class Strategy:
    count = 0

    def __init__(self, num_nodes, T, strategy=None):
        self.id = Strategy.count
        Strategy.count = + 1

        if strategy is None:
            self.time = [-math.inf] * num_nodes

            self.criteria = [-math.inf] * num_nodes

            self.dict = {}
            self.dict[0] = [0,0]
            self.dict[num_nodes - 1] = [T, T]
        else:
            self.time = copy.copy(strategy.time)
            self.criteria = copy.copy(strategy.criteria)
            self.dict = copy.copy(strategy.dict)

    def change(self, node_id, time, criteria):
        perform_time = self.time[node_id] = time
        self.criteria[node_id] = criteria
        return perform_time
