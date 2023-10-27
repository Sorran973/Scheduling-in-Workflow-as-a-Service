from CSVWriter import CSVWriter


class WorkflowSet:

    def __init__(self):
        self.workflow = []
        self.drawn_nodes = []
        self.drawn_edges = []


    def addWorkflow(self, workflow):
        self.workflow.append(workflow)


    def schedule(self):
        CSVWriter.write_headers()
        for workflow in self.workflow:
            workflow.schedule()
            self.drawn_nodes.append(workflow.drawn_nodes)
            self.drawn_edges.append(workflow.drawn_edges)
            CSVWriter.write_all_tables(workflow)
