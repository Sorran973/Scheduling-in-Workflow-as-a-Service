from abc import ABC, abstractmethod


class Criteria(ABC):
    @abstractmethod
    def main_criteria(self, perform_time):
        pass

    @abstractmethod
    def cf_criteria(self, arr):
        pass


class AverageResourceLoadCriteria(Criteria):
    def __init__(self, optimization_criteria):
        self.num_of_processors: int
        self.T: int
        self.optimization_criteria: str = optimization_criteria

    def set_parameters(self, num_of_processors, workflow_time):
        self.num_of_processors = num_of_processors
        self.T = workflow_time

    def main_criteria(self, perform_time):
        return round(perform_time / (self.num_of_processors * self.T), 2)

    def cf_criteria(self, arr):
        if self.optimization_criteria == 'max':
            return max(arr)
        else:
            return min(arr)

class TimeCriteria(Criteria):
    def __init__(self, optimization_criteria):
        self.num_of_processors: int
        self.T: int
        self.optimization_criteria: str = optimization_criteria

    def set_parameters(self, num_of_processors, workflow_time):
        self.num_of_processors = num_of_processors
        self.T = workflow_time

    def main_criteria(self, perform_time):
        return round(perform_time, 2)

    def cf_criteria(self, arr):
        if self.optimization_criteria == 'max':
            return max(arr)
        else:
            return min(arr)

class CostCriteria(Criteria):
    def __init__(self, optimization_criteria):
        self.num_of_processors: int
        self.T: int
        self.optimization_criteria: str = optimization_criteria

    def set_parameters(self, num_of_processors, workflow_time):
        self.num_of_processors = num_of_processors
        self.T = workflow_time

    def main_criteria(self, pair):
        perform_time = pair[0]
        vm_cost = pair[1]
        return round(perform_time * vm_cost, 2)

    def cf_criteria(self, arr):
        if self.optimization_criteria == 'max':
            return max(arr)
        else:
            return min(arr)