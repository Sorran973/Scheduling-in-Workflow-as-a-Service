from abc import ABC, abstractmethod


class Drawer(ABC):

    GANTT_OUTPUT = 'Output/gantt_chart.pdf'

    @abstractmethod
    def drawGraph(self, nodes, edges):
        pass

    @abstractmethod
    def drawTimes(self, nodes):
        pass