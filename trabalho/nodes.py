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
            
        
        
        for (fk, (ek, ev)) in zip(self.flows.keys(), self.estimates.items()):
            self.flows[fk] += self.local_estimate - ev
            self.estimates[ek] = self.local_estimate
        
        #print("node: ", self.id)
        #print("Flows: ",self.flows)
        #print("Estimates: ", self.estimates, "\n")

    
    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs



# Flow Updating with Preferential Grouping
class FUPGNode(FlowNode):
    def __init__(self, id, neighbours, input):
        super().__init__(id, neighbours, input)
        self.participants = {}
        self.next_leader = self.id
        self.rp = self.initRP() # reduction potential
        self.rps = dict.fromkeys(neighbours, 0) # ?

    def handle_messages(self, msgs):
        for m in msgs:
            super()._handle_message(m)
        return []  

    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            flow = None
            if participants.contains(n):
                flow = f
            
            msgs.append(FUPGMessage(self.id, n, flow, estimate(), self.next_leader, self.rp))

        return msgs

    def handle_messages(self, msgs):

        map(self._handle_message, msgs)
        return self.transition_and_gen_msgs()
        
        
    def _handle_message(self, msg):
        # TODO supostamente isto faz parte do transition, n sei se afeta a termination isto ser chamado antes das cenas de self terminate

        sender = msg.src

        # flows
        if msg.flow is not None:
            self.flows[sender] = -msg.flow

        # estimates
        if sender not in self.participants:
            self.estimates[sender] = msg.estimate

        local_estimate = estimate()

        # rp
        self.rps[sender] = msg.rp

        #participants
        if msg.leader == self.id:
            self.participants.append(sender)


    def _state_transition(self):

        leader = self.next_leader

        # two neighbors cannot choose each other as leader in the same round
        if(leader != self.id and leader in self.participants): 
            if(self.id > leader):
                self.participants.remove(leader)
            else:
                self.participants.add(self.id)
                leader = self.id

        if len(self.participants) != 0:

            sum_estimates = sum([self.estimates[p] for p in self.participants])
            self.local_estimate = sum_estimates / len(participants)


            for p in self.participants:
                if p == self.id:
                    continue
                self.flows[p] += self.local_estimate - self.estimates[p]
                self.estimates[p] = self.local_estimate

        if leader != self.id:
            self.next_leader = self.id
        else:
            self.next_leader = self.decideLeader()

        self.rp = self.computeRP(leader)

            

    def estimate(self):
        return self.input - sum(self.flows.values())

    def initRP(self):
        return 0 #TODO

    # computes a value representing the expected variance reduction (reduction potential)
    def computeRP(self, leader):
        self.estimates
        self.rps #?
        #TODO magia
        return self.rp

    def decideLeader(self):
        self.rps #?
        self.rp
        self.participants
        #TODO magia
        return self.id


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




