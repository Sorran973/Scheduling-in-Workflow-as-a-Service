from Visualization import GraphvizModule, PyvisModule, NetworkXModule
from bs4 import BeautifulSoup
import numpy as np


'''Для корректной работы алгоритма предполагаем, что рабочий процесс может иметь только одну задачу 
входа и одну задачу выхода. Этого можно достичь с помощью вставки ‘фиктивных’ задач t_entry и t_exit, время выполнения 
которых равно 0. Все фактические задачи входа являются дочерними для t_entry, а все фактические задачи выхода являются 
родительскими для t_exit.'''


class Node:  # Job
    def __init__(self, id, name, volume):
        self.index = id
        self.name = name
        self.volume = volume

    def __str__(self):
        return 'id = ' + str(self.index) + \
               ", name = " + self.name + \
               ", volume = " + str(self.volume)


class Edge:  # Data transfer
    def __init__(self, source, destination, transfer_time):
        self.source = source
        self.destination = destination
        self.transfer_time = transfer_time

    def __str__(self):
        return str(self.source) + \
               " --> " + self.destination + \
               ", transfer_time = " + str(self.transfer_time)


def pyvis_parse():
    with open(XML_FILE) as source_file:
        soup = BeautifulSoup(source_file, 'html.parser')
    # print(soup.prettify())

    vertices = []
    links = []
    
    nodes = soup.find_all('job')
    edges = soup.find_all('child')

    for node in nodes:
        vertices.append(
            Node(node.get('id'), node.get('id'), node.get('runtime'))
        )

    for edge in edges:
        parents = edge.find_all('parent')
        for i in range(len(parents)):
            links.append(
                (
                    Edge(parents[i].get('ref'), edge.get('ref'), parents[i].get('transfertime'))
                    # edge.find_all('parent')[i].get('ref'),
                    # edge.get('ref')
                )
            )

    # for vertex in vertices:
    #     print(vertex)
    #
    # for link in links:
    #     print(link)

    PyvisModule.pyvis_run(vertices, links)


def graphvis_parse():
    with open(XML_FILE) as source_file:
        soup = BeautifulSoup(source_file, 'html.parser')
    # print(soup.prettify())

    vertices = []
    links = []
    node_dict = {}

    nodes = soup.find_all('job')
    edges = soup.find_all('child')

    i = 1
    for node in nodes:
        index = node.get('id')
        cur_node = Node(i, index, node.get('runtime'))
        vertices.append(
            cur_node
        )
        node_dict[index] = cur_node
        i += 1

    for edge in edges:
        parents = edge.find_all('parent')
        for i in range(len(parents)):
            node_to = node_dict.get(parents[i].get('ref'))
            to = node_to.name + '\n(' + node_to.volume + ')'
            node_destination = node_dict.get(edge.get('ref'))
            destination = node_destination.name + '\n(' + node_destination.volume + ')'

            links.append(
                (
                    Edge(to, destination, parents[i].get('transfertime'))
                )
            )

    # for i in range(len(node_dict)+1):
    #     print(node_dict.get(i))
    #
    # for vertex in vertices:
    #     print(vertex)
    #
    # for link in links:
    #     print(link)

    GraphvizModule.graphviz_run(vertices, links)


if __name__ == '__main__':
    XML_FILE = 'JobExamples/test.xml'

    graphvis_parse()
    # pyvis_parse()