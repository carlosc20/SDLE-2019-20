import message
from message import *
import math

class FlowNode:
    def __init__(self, id, neighbours, input):
        self.id = id
        self.input = input
        self.local_estimate = input
        self.neighbours = neighbours
        self.degree = len(neighbours)
        self.flows = dict.fromkeys(neighbours, 0)
        self.estimates = dict.fromkeys(neighbours, 0)

    def addNeighbour(self, node):
        self.neighbours.append(node)
        self.flows[node] = 0
        self.estimates[node] = 0
        self.degree += 1

    def removeNeighbour(self, node):
        self.neighbours.remove(node)
        del self.flows[node]
        del self.estimates[node]
        self.degree -= 1
        print("removed: ", self.flows, " " , self.estimates)

    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs

    def handle_messages(self, msgs):

        for m in msgs:
            self._handle_message(m)
        
        self._state_transition()

        return self.generate_messages()


    def _handle_message(self, msg):

        sender = msg.src
        self.flows[sender] = -msg.flow
        self.estimates[sender] = msg.estimate

    def _state_transition(self):
        sum_flows = sum(self.flows.values())
        sum_estimates = sum(self.estimates.values())
        self.local_estimate = (self.input - sum_flows + sum_estimates ) / (self.degree + 1)
            
        
        
        for (fk, (ek, ev)) in zip(self.flows.keys(), self.estimates.items()):
            self.flows[fk] += (self.local_estimate - ev)
            self.estimates[ek] = self.local_estimate
        
        print("node: ", self.id)
        print("Flows: ",self.flows)
        print("Estimates: ", self.estimates, "\n")


class TimeoutFlowNode(FlowNode):
    def __init__(self, id, neighbours, input, timeout_value):
        super().__init__(id, neighbours, input)
        self.timeout_value = timeout_value

    def handle_messages(self, msgs):
        print("Storing Messages")
        for m in msgs:
            super()._handle_message(m)
        return []  

    # returns (timeout, [msg])
    def handle_timeout(self):
        print("Timeout arrived")
        super()._state_transition()
        return Timeout(self.id, self.timeout_value), super().generate_messages()


class SelfTerminateIterNode(FlowNode):
    def __init__(self, id, neighbours, input, max_rounds):
        super().__init__(id, neighbours, input)
        self.max_rounds = max_rounds
        self.working = True
        self.rounds = 0


    def handle_messages(self, msgs):
        if(self.working):
            super().handle_messages(msgs)
            self.rounds += 1
            if(self.rounds >= self.max_rounds):
                self.working = False




class SelfTerminateDifNode(FlowNode):
    def __init__(self, id, neighbours, input, min_dif):
        super().__init__(id, neighbours, input)
        self.min_dif = min_dif
        self.working = True



    def handle_messages(self, msgs):
        if(self.working):
            prev_estimate = self.local_estimate
            super().handle_messages(msgs)
            dif = self.local_estimate / prev_estimate
            if(dif <= min_dif):
                self.working = False



