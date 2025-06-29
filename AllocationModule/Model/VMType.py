import Utils.Configuration


class VMType:

    def __init__(self, type, perf, cost,
                 prep_time=Utils.Configuration.VM_PREP_TIME,
                 shutdown_time=Utils.Configuration.VM_SHUTDOWN_TIME):
        self.type = type
        self.perf = perf
        self.cost = cost
        self.prep_time = prep_time
        self.shutdown_time = shutdown_time

