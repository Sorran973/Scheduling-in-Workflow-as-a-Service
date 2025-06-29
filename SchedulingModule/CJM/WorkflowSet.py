from Utils.CSVHandler import CSVHandler


class WorkflowSet:

    def __init__(self):
        self.workflows = []
        self.drawn_nodes = []
        self.drawn_edges = []
        CSVHandler.write_headers()


    def addWorkflow(self, workflow):
        n = len(self.workflows)
        self.workflows.append(workflow)
        workflow.schedule()
        self.drawn_nodes.append(workflow.drawn_nodes)
        self.drawn_edges.append(workflow.drawn_edges)
        CSVHandler.write_all_tables(workflow, n)
        print("Workflow " + str(n) + ":")
        print("\tT: " + str(workflow.T))
        print("\tTotal CJM Criteria: " + str(sum(workflow.best_strategy.criteria)))
