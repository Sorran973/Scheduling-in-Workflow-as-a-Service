from abc import ABC, abstractmethod


class Drawer(ABC):

    GANTT_OUTPUT = 'Output/gantt_chart.pdf'

    @abstractmethod
    def draw_graph(self, nodes, edges):
        pass

    @abstractmethod
    def draw_gantt(self, nodes):
        pass