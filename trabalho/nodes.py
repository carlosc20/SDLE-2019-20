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

    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs


    def handle_messages(self, msgs):

        for m in msgs:
            self._handle_message(m)
        
        self._state_transition()


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
        print("Estimates: ", self.estimates)





class GlobalTerminateFlowSumNode(FlowNode):
    def __init__(self, id, neighbours, input):
        super().__init__(id, neighbours, input)


    def generate_messages_termination_flowsums(self):
        msgs = []
        
        flowSum = 0
        
        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))
            flowSum += f
            
        return msgs, flowSum


    # uses the sum of all flows as limit to termination. If the sum is equal to 0 convergion has been reached
    @staticmethod
    def handle_termination(self, group, nodes):
        
        new = [] 
        flowsums = 0
        
        for dst, msgs in group.items():
            node = nodes[dst]
            node.handle_messages(msgs)  
            gen, node_flow_sum = node.generate_messages_termination_flowsums()
            flowsums += node_flow_sum
            new += gen

        if (flowsums > 0):
            return new
        else:
            return []




class GlobalTerminateRMSENode(FlowNode):
    def __init__(self, id, neighbours, input):
        super().__init__(id, neighbours, input)

    # returns local estimate for termination
    def generate_messages_termination_rmse(self):
        msgs = []

        for (n, f, e) in zip(self.neighbours, self.flows.values(), self.estimates.values()):
            msgs.append(FlowMessage(self.id, n, f, e))
            
        return msgs, self.local_estimate

    # creates new messages from each node. If reached the termination limit no messages are considered.
    # uses RMSE as limit to termination
    @staticmethod
    def handle_termination(group, nodes, target_value, target_rmse):
        
        new = [] 
        square_error_sum = 0
        
        for dst, msgs in group.items():
            node = nodes[dst]
            node.handle_messages(msgs)  
            gen, node_local_estimate = node.generate_messages_termination_rmse()
            square_error_sum += (node_local_estimate - target_value) ** 2
            new += gen
            
        rmse = math.sqrt(square_error_sum / len(nodes))
        
        if (rmse > target_rmse):
            return new
        else:
            return []




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


