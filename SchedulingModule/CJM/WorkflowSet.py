from Utils.CSVHandler import CSVHandler


class WorkflowSet:

    def __init__(self):
        self.workflows = []
        self.drawn_nodes = []
        self.drawn_edges = []
        CSVHandler.write_headers()
        self.success_scheduled_workflow = []


    def addWorkflow(self, workflow):
        n = len(self.workflows)
        self.workflows.append(workflow)
        workflow.schedule()
        self.drawn_nodes.append(workflow.drawn_nodes)
        self.drawn_edges.append(workflow.drawn_edges)

        print("Workflow #" + str(workflow.T))
        if workflow.best_strategy:
            self.success_scheduled_workflow.append(workflow.T)
            print("Workflow #" + str(workflow.T) + "CJM SUCCESS")

            CSVHandler.write_all_tables(workflow, n)
            print("Workflow " + str(n) + ":")
            print("\tT: " + str(workflow.T))
            print("\tTotal CJM Criteria: " + str(sum(workflow.best_strategy.criteria)))

    def addHEFTWorkflow(self, heft_workflow):
        n = len(self.workflows)
        heft_workflow.set_workflow_id(n)
        self.workflows.append(heft_workflow)
        self.drawn_nodes.append(heft_workflow.drawn_nodes)
        self.drawn_edges.append(heft_workflow.drawn_edges)
        # CSVHandler.write_all_tables(workflow, n)