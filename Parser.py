from bs4 import BeautifulSoup

class Parser:

    @staticmethod
    def parse(xml_file):
        with open(xml_file) as source_file:
            soup = BeautifulSoup(source_file, 'html.parser')
        # print(soup.prettify())

        soup_nodes = soup.find_all('job')
        soup_edges = soup.find_all('child')

        return soup_nodes, soup_edges