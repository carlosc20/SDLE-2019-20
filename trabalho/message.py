
class Message:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class FlowMessage(Message):
    def __init__(self, src, dst, flow, estimate):
        super().__init__(src, dst)
        self.flow = flow
        self.estimate = estimate