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
        self.termination_component = None

    def set_termination_component(self, component):
        self.termination_component = component

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

    def handle_messages(self, msgs):

        for m in msgs:
            self._handle_message(m)

        return self.transition_and_gen_msgs()
        
        
    def _handle_message(self, msg):

        sender = msg.src
        self.flows[sender] = -msg.flow
        self.estimates[sender] = msg.estimate


    def transition_and_gen_msgs(self):
        if self.termination_component != None:
            self.termination_component.prepare_check()

        self._state_transition()

        new = self.generate_messages()
        if self.termination_component != None:
            if self.termination_component.check_termination():
                new = []

        return new


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

    
    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs



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
        new = super().transition_and_gen_msgs()
        timeout = Timeout(self.id, self.timeout_value)

        if self.termination_component != None and not self.termination_component.working:
            timeout = None

        return timeout, new


class SelfTerminateRoundsComponent:
    def __init__(self, node, max_rounds):
        self.node = node
        self.max_rounds = max_rounds
        self.working = True
        self.rounds = 0


    def prepare_check(self):
        pass


    def check_termination(self):
        if(self.working):
            self.rounds += 1
            print("check_termination rounds:", self.rounds)
            if(self.rounds == self.max_rounds):
                self.working = False
                return True
            else:
                return False
        else:
            return True


class SelfTerminateDifComponent:
    def __init__(self, node, max_rounds, min_dif):
        self.node = node
        self.max_rounds = max_rounds
        self.rounds = 0
        self.min_dif = min_dif
        self.prev_estimate = None
        self.working = True


    def prepare_check(self):
        self.prev_estimate = self.node.local_estimate


    def check_termination(self):
        if(self.working):
            dif = abs((self.node.local_estimate - self.prev_estimate)) / self.node.local_estimate
            print("check_termination: dif: ", dif, " rounds:", self.rounds)
            if(dif <= self.min_dif):
                self.rounds += 1
                if self.rounds == self.max_rounds:
                    self.working = False
                    return True
            else:
                self.rounds = 0
                return False
        else:
            return True




