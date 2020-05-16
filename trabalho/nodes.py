
class FlowNode:
    def __init__(self, id, neighbours, input):
        self.id = id
        self.input = input
        self.neighbours = neighbours
        self.degree = len(neighbours)
        self.flows = [0] * self.degree
        self.estimates = [0] * self.degree
        self.local_estimate = input


    # broadcast messages to each neighbour
    # returns sum of all flows for termination
    def generate_messages_termination_flowsums(self):
        msgs = []
        
        flowSum = 0
        
        for (n, f, e) in zip(self.neighbours, self.flows, self.estimates):
            msgs.append(FlowMessage(self.id, n, f, e))
            flowSum += f
            
        return msgs, flowSum
    
    # returns local estimate for termination
    def generate_messages_termination_rmse(self):
        msgs = []

        for (n, f, e) in zip(self.neighbours, self.flows, self.estimates):
            msgs.append(FlowMessage(self.id, n, f, e))
            
        return msgs, self.local_estimate

    def handle_messages(self, msgs):

        received = {} 

        for m in msgs:
            received.add(m.src)
            self._handle_message(m)
        
        # mensagens perdidas -> se não chegou nada de x, por exemplo, flow/estimate x permanece com o valor anterior, mesmo sendo 0
        #for n in self.neighbours:
            #sender = n.id
            #if sender not in received:
                # TODO ??
                #self.flows[sender] = -self.flows[self.id]

        ##tirei o return para o simulador poder chamar o generateMessage consoante o caso
        self._state_transition()


    def _handle_message(self, msg):
        sender = msg.src
        self.flows[sender] = -msg.flow
        self.estimates[sender] = msg.estimate

    def _state_transition(self):
        self.local_estimate = (input - sum(self.flows) + sum(self.estimates)) / (len(self.neighbours) + 1)

        for (f, e) in zip(self.flows, self.estimates):
            f += (self.local_estimate + e)
            e = self.local_estimate
        

class Message:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class FlowMessage(Message):
    def __init__(self, src, dst, flow, estimate):
        super().__init__(src, dst)
        self.flow = flow
        self.estimate = estimate
