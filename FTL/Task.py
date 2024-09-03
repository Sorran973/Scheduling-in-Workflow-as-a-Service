class Task:

    def __init__(self, id, name, volume, start=0, end=0):
        self.id = id
        self.name = name
        self.volume = volume
        self.start = start
        self.end = end
        self.interval = self.end - self.start
        self.type = "Task"
        self.status = None
        self.assigned_vm = None
        self.allocation_end = None
        self.calc_time = None
        self.latest_start = None
        self.earliest_finish = None
        self.possible_start = None
        self.batch = None
        self.finish_time = None
        self.color = None

        if self.name == "entry" or self.name == "finish":
            self.status = "IO"