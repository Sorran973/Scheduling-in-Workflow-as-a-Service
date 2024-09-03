class VM:
    vm_counter = 0

    def __init__(self, type, perf, cost, prep_time=1, release_time=1):
        self.id = VM.vm_counter
        self.type = type
        self.perf = perf
        self.cost = cost
        self.prep_time = prep_time
        self.release_time = release_time

        VM.vm_counter += VM.vm_counter