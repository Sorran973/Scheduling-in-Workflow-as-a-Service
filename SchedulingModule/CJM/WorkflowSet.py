from Parsing.CSVHandler import CSVHandler


class WorkflowSet:

    def __init__(self):
        self.workflows = []
        self.drawn_nodes = []
        self.drawn_edges = []


    def addWorkflow(self, workflow):
        self.workflows.append(workflow)


    def schedule(self):
        CSVHandler.write_headers()
        for workflow in self.workflows:
            workflow.schedule()
            self.drawn_nodes.append(workflow.drawn_nodes)
            self.drawn_edges.append(workflow.drawn_edges)
            CSVHandler.write_all_tables(workflow)
