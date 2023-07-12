from abc import ABC, abstractmethod


class Criteria(ABC):
    @abstractmethod
    def main_criteria(self, perform_time):
        pass

    @abstractmethod
    def cf_criteria(self, arr):
        pass


class AverageResourceLoad(Criteria):

    def __init__(self, job, CF_criteria):
        self.num_of_processors = job.num_of_processors
        self.T = job.T
        self.CF_criteria: str = CF_criteria


    def main_criteria(self, perform_time):
        return round(perform_time / (self.num_of_processors * self.T), 2)

    def cf_criteria(self, arr):
        if self.CF_criteria == 'max':
            return max(arr)
        else:
            return min(arr)