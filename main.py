from DAG import Node, DAG, Edge
from Visualization import GraphvizModule, PyvisModule, NetworkXModule
from bs4 import BeautifulSoup
import numpy as np

'''Для корректной работы алгоритма предполагаем, что рабочий процесс может иметь только одну задачу 
входа и одну задачу выхода. Этого можно достичь с помощью вставки ‘фиктивных’ задач t_entry и t_exit, время выполнения 
которых равно 0. Все фактические задачи входа являются дочерними для t_entry, а все фактические задачи выхода являются 
родительскими для t_exit.'''


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
            # Node(node.get('id'), node.get('id'), node.get('runtime'))
        )

    for edge in edges:
        parents = edge.find_all('parent')
        for i in range(len(parents)):
            links.append(
                (
                    # Edge(parents[i].get('ref'), edge.get('ref'), parents[i].get('transfertime'))
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


def graphvis_parse(graph):
    with open(XML_FILE) as source_file:
        soup = BeautifulSoup(source_file, 'html.parser')
    # print(soup.prettify())

    visualNodes = []
    visualEdges = []
    node_dict = {}

    soupNodes = soup.find_all('job')
    soupEdges = soup.find_all('child')

    i = 1
    for node in soupNodes:
        name = node.get('id')
        runtime = node.get('runtime')
        currunt_node = Node(i, name, runtime)

        visualNodes.append(currunt_node)
        node_dict[name] = currunt_node

        graph.add_node(currunt_node)

        i += 1


    graph.set_dp()

    for edge in soupEdges:
        parents = edge.find_all('parent')
        for parent in parents:
            node_from = node_dict.get(parent.get('ref'))
            node_to = node_dict.get(edge.get('ref'))
            transfer_time = float(parent.get('transfertime'))

            node_from_str = node_from.name + '\n(' + node_from.runtime + ')'
            node_to_str = node_to.name + '\n(' + node_to.runtime + ')'

            visualEdges.append([node_from_str, node_to_str, parent.get('transfertime')])

            graph.add_edge(Edge(node_from, node_to, transfer_time))

    GraphvizModule.graphviz_run(visualNodes, visualEdges)


if __name__ == '__main__':
    XML_FILE = 'JobExamples/Montage_25.xml'
    # XML_FILE = 'JobExamples/Epigenomics_25.xml'
    # XML_FILE = 'JobExamples/CyberShake_30.xml'

    graph = DAG()
    graphvis_parse(graph)
    print(graph.findLongestPath())

