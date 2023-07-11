from abc import ABC, abstractmethod


class Criteria(ABC):
    @abstractmethod
    def main_criteria(self, perform_time):
        pass

    @abstractmethod
    def cf_criteria(self, arr):
        pass


class AverageResourceLoad(Criteria):

    def __init__(self, num_of_recources, T, CF_criteria):
        self.num_of_recources = num_of_recources
        self.T = T
        self.CF_criteria: str = CF_criteria


    def main_criteria(self, perform_time):
        return round(perform_time / (self.num_of_recources * self.T), 2)

    def cf_criteria(self, arr):
        if self.CF_criteria == 'max':
            return max(arr)
        else:
            return min(arr)