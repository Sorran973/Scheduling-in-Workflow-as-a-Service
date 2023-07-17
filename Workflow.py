from CSVWriter import CSVWriter


class Workflow:

    def __init__(self):
        self.jobs = []
        self.draw_nodes = []
        self.draw_edges = []


    def addJob(self, job):
        self.jobs.append(job)


    def schedule(self):
        CSVWriter.write_headers()
        for job in self.jobs:
            job.schedule()
            self.draw_nodes.append(job.draw_nodes)
            self.draw_edges.append(job.draw_edges)
            CSVWriter.write_all_tables(job)
