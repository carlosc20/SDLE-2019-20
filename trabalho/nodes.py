
class FlowNode:
    def __init__(self, id, neighbours, input):
        self.id = id
        self.input = input
        self.neighbours = neighbours
        self.degree = len(neighbours)
        self.flows = [0] * degree
        self.estimates = [0] * degree


    # broadcast messages to each neighbour
    def generate_messages(self):
        msgs = []
        for (n, f, e) in zip(self.neighbours, self.flows, self.estimates):
            msgs.append(FlowMessage(self.id, n, f, e))

        return msgs

    def handle_messages(self, msgs):

        received = {} 

        for m in msgs:
            received.add(m.src)
            self._handle_message(m)
        
        # mensagens perdidas -> se não chegou nada de x, por exemplo, flow/estimate x permanecem com o valor anterior, mesmo sendo 0
        #for n in self.neighbours:
            #sender = n.id
            #if sender not in received:
                # TODO ??
                #self.flows[sender] = -self.flows[self.id]

        self._state_transition()
        
        return self.generate_messages()


    def _handle_message(self, msg):
        sender = msg.src
        self.flows[sender] = -msg.flow
        self.estimates[sender] = msg.estimate

    def _state_transition(self):
        local_estimate = (input - sum(self.flows) + sum(self.estimates)) / (len(self.neighbours) + 1)

        for (f, e) in zip(self.flows, self.estimates):
            f += (local_estimate + e)
            e = local_estimate





class Message:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class FlowMessage(Message):
    def __init__(self, src, dst, flow, estimate):
        super(src, dst)
        #super().__init__()
