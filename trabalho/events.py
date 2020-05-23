class Event:
    def __init__(self, message, time):
        self.message = message
        self.time = time


class SimulatorEvent:
    def __init__(self, n_rounds, repeatable):
        self.n_rounds = n_rounds
        self.ticker = 0
        self.repeatable = repeatable


class AddMembers(SimulatorEvent):
    def __init__(self, numberToAdd, numberOfConnections, input, n_rounds, repeatable, w=None):
        super().__init__(n_rounds, repeatable)
        self.numberToAdd = numberToAdd
        self.numberOfConnections = numberOfConnections
        self.input = input
        self.w = w


class RemoveMembers(SimulatorEvent):
    def __init__(self, numberToRemove, n_rounds, repeatable):
        super().__init__(n_rounds, repeatable)
        self.numberToRemove = numberToRemove