import config


class VMType:

    def __init__(self, type, perf, cost, bandwidth,
                 prep_time=config.VM_PREP_TIME,
                 shutdown_time=config.VM_SHUTDOWN_TIME):
        self.type = type
        self.perf = perf
        self.cost = cost
        self.bandwidth = bandwidth
        self.prep_time = prep_time
        self.shutdown_time = shutdown_time

