class Task:
    task_counter = 0

    def __init__(self, id, name, volume, start=0, end=0, type='task'):
        self.id = id
        Task.task_counter = id
        self.name = name
        self.volume = volume
        self.start = start
        self.end = end
        self.interval = self.end - self.start
        self.type = type
        self.input = []
        self.input_size = 0
        self.input_time = 0
        self.output = []
        self.output_size = 0
        self.output_time = 0
        self.status = None
        self.batch = None
        self.color = None

        self.possible_vms = []
        self.possible_assignments = []

        self.assigned_vm = None
        self.allocation_start = None
        self.allocation_end = None
        self.vm_allocation_start = None
        self.vm_allocation_end = None
        self.allocation_cost = None

        self.calc_time = None
        self.latest_start = None
        # self.earliest_finish = None
        self.possible_start = None
        # self.finish_time = None

        if self.name == 'entry' or self.name == 'finish':
            self.status = 'IO'


    def addInputTransfer(self, data_transfer):
            self.input.append(data_transfer)
            self.input_size += data_transfer.transfer_size

    def addOutputTransfer(self, data_transfer):
            self.output.append(data_transfer)
            self.output_size += data_transfer.transfer_size

    def calculateTransferTime(self, data_transfer_channel):
        self.input_time = round(self.input_size / data_transfer_channel)
        self.output_time = round(self.output_size / data_transfer_channel)

    def setAssignedVm(self, assigned_vm):
        self.assigned_vm = assigned_vm
        assign_info = next(filter(lambda x: x.assigned_vm == assigned_vm, self.possible_assignments))
        self.allocation_start = assign_info.task_allocation_start
        self.allocation_end = assign_info.task_allocation_end
        self.vm_allocation_start = assign_info.vm_allocation_start
        self.vm_allocation_end = assign_info.vm_allocation_end
        self.allocation_cost = assign_info.allocation_cost

    def setAllocationStart(self, allocation_start):
        self.allocation_start = allocation_start

    def setAllocationEnd(self, allocation_end):
        self.allocation_end = allocation_end