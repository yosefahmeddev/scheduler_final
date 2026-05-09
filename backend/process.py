class Process:
    def __init__(self, pid: str, arrival_time: int, burst_time: int, index: int = 0):

        #set vy the user
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.index = index

        #filled in by the scheduler
        self.remaining_time = burst_time
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1
        self.done = False

    def reset(self):
        #clear all result fields so the same object can be reused
        self.remaining_time  = self.burst_time
        self.finish_time     = 0
        self.waiting_time    = 0
        self.turnaround_time = 0
        self.response_time   = -1
        self.done            = False

    def to_dict(self) -> dict:
        #Return a plain dict so FastAPI can serialise it to JSON
        return {
            "pid"            : self.pid,
            "arrival_time"   : self.arrival_time,
            "burst_time"     : self.burst_time,
            "finish_time"    : self.finish_time,
            "waiting_time"   : self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "response_time"  : self.response_time,
            "index"          : self.index,
        }
