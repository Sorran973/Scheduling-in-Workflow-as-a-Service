from CSVWriter import CSVWriter
from Job import Node, Job, Edge
from Parser import Parser
from Visualization import GraphvizModule, PyvisModule, NetworkXModule
from bs4 import BeautifulSoup
import numpy as np

'''
Исходные данные: информационный граф G задания пользователя, набор вычислительных узлов R, стратегия st, определяющая 
критериальные функции и направление оптимизации, крайний срок T или максимальный бюджет С выполнения задания. Для всех 
вершин из G заданы априорные оценки времени выполнения соответствующей подзадачи на каждом узле, а для всех рёбер – 
оценки соответствующего времени обмена данными.
'''

# TODO: compare Graphviz и NetworkX (deep)

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


if __name__ == '__main__':
    # XML_FILE = 'JobExamples/test0_6.xml'
    # XML_FILE = 'JobExamples/test1_11.xml'
    XML_FILE = 'JobExamples/Montage_25.xml'
    # XML_FILE = 'JobExamples/Montage_100.xml'
    # XML_FILE = 'JobExamples/Epigenomics_25.xml'
    # XML_FILE = 'JobExamples/CyberShake_30.xml'

    soup_nodes, soup_edges = Parser.parse(XML_FILE)
    job = Job(soup_nodes, soup_edges)

    CSVWriter.write_current_processor_table(file_name='processor_table.csv', nodes=job.nodes, processor_table=job.processor_table)
    CSVWriter.write_task_times_table(file_name='task_times_table.csv', nodes=job.nodes)
    CSVWriter.write_transfer_size_table(file_name='transfer_size_table.csv', edges=job.edges)

    # Job.global_timer = 5
    # Node.id = 0
    # Edge.id = 0
    #
    #
    # soup_nodes, soup_edges = Parser.parse(XML_FILE)
    # job2 = Job(soup_nodes, soup_edges)
    #
    # CSVWriter.write_current_processor_table(file_name='processor_table2.csv', nodes=job2.nodes, processor_table=job2.processor_table)
    # CSVWriter.write_task_times_table(file_name='task_times_table2.csv', nodes=job2.nodes)
    # CSVWriter.write_transfer_size_table(file_name='transfer_size_table2.csv', edges=job2.edges)



    GraphvizModule.graphviz_run(job.graphviz_nodes, job.graphviz_edges)
