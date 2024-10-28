class VM:
    vm_counter = 0

    def __init__(self, type, perf, cost, prep_time=1, release_time=1):
        self.id = VM.vm_counter
        self.type = type
        self.perf = perf
        self.cost = cost
        self.prep_time = prep_time
        self.release_time = release_time
        self.status = 'open'
        self.previous_task = None
        self.vm_allocation_start = None
        self.vm_allocation_end = None
        self.task_allocation_start = None
        self.task_allocation_end = None
        self.color = None

        VM.vm_counter = VM.vm_counter + 1


    def setStatus(self, status):
        self.status = status

    def setPreviousTask(self, task):
        self.previous_task = task

    def setVmAllocationStart(self, vm_allocation_start):
        self.vm_allocation_start = vm_allocation_start

    def setVmAllocationEnd(self, vm_allocation_end):
        self.vm_allocation_end = vm_allocation_end

    def setTaskAllocationStart(self, task_allocation_start):
        self.task_allocation_start = task_allocation_start

    def setTaskAllocationEnd(self, task_allocation_end):
        self.task_allocation_end = task_allocation_end

    def setColor(self, color):
        self.color = color

    def __str__(self):
        return 'id = ' + str(self.id) + \
               ", type = " + self.type + \
               ", perf = " + str(self.perf) + \
               ", cost = " + str(self.cost) + \
               ", prep_time = " + str(self.prep_time) + \
               ", release_time = " + str(self.release_time) + \
               ", status = " + str(self.status)
