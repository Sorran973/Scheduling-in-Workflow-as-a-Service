class VMType:

    def __init__(self, type, perf, cost, prep_time=1, release_time=1):
        self.type = type
        self.perf = perf
        self.cost = cost
        self.prep_time = prep_time
        self.release_time = release_time

