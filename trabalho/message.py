
class Message:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class Timeout(Message):
    def __init__(self, src, time):
        self.src = src
        self.dst = src
        self.time = time


class FlowMessage(Message):
    def __init__(self, src, dst, flow, estimate):
        super().__init__(src, dst)
        self.flow = flow
        self.estimate = estimate