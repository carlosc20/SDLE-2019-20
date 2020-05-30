import message
from message import *
import math
import random

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
        #print("removed: ", self.flows, " " , self.estimates)

    def handle_messages(self, msgs):
        for m in msgs:
            self._handle_message(m)

        return self.transition_and_gen_msgs()
        
        
    def _handle_message(self, msg):

        sender = msg.src
        self.flows[sender] = -msg.flow
        self.estimates[sender] = msg.estimate


    def transition_and_gen_msgs(self):
        if self.termination_component != None :
            if not self.termination_component.working:
                return []
            self.termination_component.prepare_check()
            self._state_transition()
            new = self.generate_messages()
            if self.termination_component.check_termination():
               # print("Node: ", self.id, " terminated")
                new = []
        else:
            self._state_transition()
            new = self.generate_messages()
        return new


    def _state_transition(self):
        sum_flows = sum(self.flows.values())
        sum_estimates = sum(self.estimates.values())
        self.local_estimate = (self.input - sum_flows + sum_estimates ) / (self.degree + 1)

        print(self.local_estimate)
        
        for n in self.neighbours:
            self.flows[n] += self.local_estimate - self.estimates[n]
            self.estimates[n] = self.local_estimate

        
        #print("node: ", self.id)
        #print("Flows: ",self.flows)
        #print("Estimates: ", self.estimates, "\n")

    
    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs



class MulticastFlowNode(FlowNode):
    def __init__(self, id, neighbours, input, multi):
        super().__init__(id, neighbours, input)
        self.multi = multi
        self.chosen_neighbours = self._choose_neighbours()

    def generate_messages(self):
        msgs = []
        for n in self.chosen_neighbours:
            msgs.append(FlowMessage(self.id, n, self.flows[n], self.estimates[n]))
        return msgs

    def _state_transition(self):
        sum_flows = sum(self.flows.values())
        sum_estimates = sum(self.estimates.values())
        self.local_estimate = (self.input - sum_flows + sum_estimates ) / (self.degree + 1)

        self.chosen_neighbours = self._choose_neighbours()

        for n in self.chosen_neighbours:
            self.flows[n] += self.local_estimate - self.estimates[n]
            self.estimates[n] = self.local_estimate


    def _choose_neighbours(self):
        # escolhido uniformemente

        if len(self.neighbours) <= self.multi:
            return self.neighbours

        chosen = random.sample(self.neighbours, self.multi)
        return chosen





class EvaluatedMulticastFlowNode(MulticastFlowNode):
    def __init__(self, id, neighbours, input, multi):
        super().__init__(id, neighbours, input, multi)
        self.chosen_neighbours = super()._choose_neighbours()

    def _choose_neighbours(self):
        if len(self.neighbours) <= self.multi:
            return self.neighbours

        discrepancies = list((n, self.local_estimate - self.estimates[n]) for n in self.neighbours)
        chosen = sorted(discrepancies, key=lambda pair: pair[1], reverse=True)[:self.multi]

        return [i[0] for i in chosen]



    
class TimeoutFlowNode(FlowNode):
    def __init__(self, id, neighbours, input, timeout_value):
        super().__init__(id, neighbours, input)
        self.timeout_value = timeout_value
        self.latest_timeout = None
        self.round = 1
        self.neighbours_arrived = dict.fromkeys(neighbours, 0)


    def handle_messages(self, msgs):
       # print("Node: ", self.id, " Storing Messages")
        for m in msgs:
            self.neighbours_arrived[m.src] += 1
            super()._handle_message(m)
        
        minimum = min(self.neighbours_arrived.values())

        new = []
        if minimum == self.round:
            new = self.handle_transition()
            self.round += 1
        return new 


    # returns (timeout, [msg])
    def handle_transition(self):
        #print("Node: ", self.id, " Transitioning")
        new = super().transition_and_gen_msgs()
        
        if self.termination_component != None and not self.termination_component.working:
            self.latest_timeout = None
        else:
            self.latest_timeout = Timeout(self.id, self.round, self.timeout_value)

        return new

    def reset_rounds(self):
        self.neighbours_arrived = dict.fromkeys(self.neighbours, 0)
        self.round = 1

    def take_latest_timeout(self):
        t = self.latest_timeout
        self.latest_timeout = None
        return t

    def old_timeout(self, timeout):
        return timeout.round < self.round


class TimeoutMulticastFlowNode(MulticastFlowNode, TimeoutFlowNode):
    def __init__(self, id, neighbours, input, multi, timeout_value):
        MulticastFlowNode.__init__(id, neighbours, input, multi)
        TimeoutFlowNode.__init__(id, neighbours, input, timeout_value)


class TimeoutEvaluatedMulticastFlowNode(EvaluatedMulticastFlowNode, TimeoutFlowNode):
    def __init__(self, id, neighbours, input, multi, timeout_value):
        EvaluatedMulticastFlowNode.__init__(self, id, neighbours, input, multi)
        TimeoutFlowNode.__init__(self, id, neighbours, input, timeout_value)


    
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
            #print("check_termination rounds:", self.rounds)
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
            #print("check_termination: dif: ", dif, " rounds:", self.rounds)
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




