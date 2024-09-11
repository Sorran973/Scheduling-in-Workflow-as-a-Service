class PossibleAssignment:
    def __init__(self, vm):
        self.assigned_vm = vm
        self.calc_time = None
        self.allocation_cost = None
        # self.latest_start = None
        # self.earliest_finish = None
        # self.possible_start = None
        self.task_allocation_start = None
        self.task_allocation_end = None
        self.vm_allocation_start = None
        self.vm_allocation_end = None
