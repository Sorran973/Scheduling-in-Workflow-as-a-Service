from DAG import Node, DAG, Edge
from Visualization import GraphvizModule, PyvisModule, NetworkXModule
from bs4 import BeautifulSoup
import numpy as np



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


def parse(graph):
    with open(XML_FILE) as source_file:
        soup = BeautifulSoup(source_file, 'html.parser')
    # print(soup.prettify())

    soupNodes = soup.find_all('job')
    soupEdges = soup.find_all('child')

    graph.design_graph(soupNodes, soupEdges)


if __name__ == '__main__':
    # XML_FILE = 'JobExamples/Montage_25.xml'
    XML_FILE = 'JobExamples/Epigenomics_25.xml'
    # XML_FILE = 'JobExamples/CyberShake_30.xml'

    graph = DAG()

    parse(graph)

