from abc import ABC, abstractmethod


class Criteria(ABC):
    @abstractmethod
    def main_criteria(self, perform_time):
        pass

    @abstractmethod
    def cf_criteria(self, arr):
        pass


class AverageResourceLoadCriteria(Criteria):

    def __init__(self, CF_criteria):
        self.num_of_processors: int
        self.T: int
        self.CF_criteria: str = CF_criteria

    def set_parameters(self, num_of_processors, workflow_time):
        self.num_of_processors = num_of_processors
        self.T = workflow_time

    def main_criteria(self, perform_time):
        return round(perform_time / (self.num_of_processors * self.T), 2)

    def cf_criteria(self, arr):
        if self.CF_criteria == 'max':
            return max(arr)
        else:
            return min(arr)