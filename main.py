from CSVWriter import CSVWriter
from Edge import Edge
from Job import Job
from Node import Node
from Parser import Parser
from Visualization import GraphvizModule, PyvisModule, NetworkXModule
from Criteria import*


# TODO: compare Graphviz и NetworkX (deep)

# def pyvis_parse():
#     with open(XML_FILE) as source_file:
#         soup = BeautifulSoup(source_file, 'html.parser')
#     # print(soup.prettify())
#
#     vertices = []
#     links = []
#
#     nodes = soup.find_all('job')
#     edges = soup.find_all('child')
#
#     for node in nodes:
#         vertices.append(
#             # Node(node.get('id'), node.get('id'), node.get('runtime'))
#         )
#
#     for edge in edges:
#         parents = edge.find_all('parent')
#         for i in range(len(parents)):
#             links.append(
#                 (
#                     # Edge(parents[i].get('ref'), edge.get('ref'), parents[i].get('transfertime'))
#                     # edge.find_all('parent')[i].get('ref'),
#                     # edge.get('ref')
#                 )
#             )
#
#     # for vertex in vertices:
#     #     print(vertex)
#     #
#     # for link in links:
#     #     print(link)
#
#     PyvisModule.pyvis_run(vertices, links)


if __name__ == '__main__':
    # XML_FILE = 'JobExamples/test1_11.xml'
    # XML_FILE = 'JobExamples/Montage_25.xml'
    # XML_FILE = 'JobExamples/Montage_100.xml'
    XML_FILE = 'JobExamples/Epigenomics_25.xml'
    # XML_FILE = 'JobExamples/CyberShake_30.xml'

    soup_nodes, soup_edges = Parser.parse(XML_FILE)
    job = Job(soup_nodes, soup_edges)
    criteria: Criteria = AverageResourceLoad(job, 'max')
    job.schedule(criteria)
    CSVWriter.write_all_tables(job)


    Job.global_timer = 5
    Node.id = 0
    Edge.id = 0


    soup_nodes, soup_edges = Parser.parse(XML_FILE)
    job2 = Job(soup_nodes, soup_edges)
    criteria: Criteria = AverageResourceLoad(job2, 'max')
    job2.schedule(criteria)
    CSVWriter.write_all_tables(job2)


    GraphvizModule.graphviz_run(job)