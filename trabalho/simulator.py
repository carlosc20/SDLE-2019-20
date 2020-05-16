import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import nodes
import random
import math

# TODO: Fazer mudanças de ligações no grafo em runtime


class Simulator:

    def __init__(self, nodes, distances, loss_rate, target_value = None, target_rmse = None):
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.nodes = nodes # dict: nr -> Node
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [(delay, Message]
        self.target_value = target_value
        self.target_rmse = target_rmse
        
        # para o sincrono
        self.n_rounds = 0



    def start(self):
        # primeira ronda de mensagens
        messages = []
        for n in self.nodes.values():
            
            if self.target_value == None:
                messages += n.generate_messages_termination_flowsums()[0]
            else:
                messages += n.generate_messages_termination_rmse()[0]
                
        self.pending.append(self._create_events(messages))

        # run the simulation loop
        return self.run_loop()


    def _create_events(self, message_list):
 
        events = []
        for n in message_list:
            print(n)
            link_delay = self.distances[(n.src, n.dst)]
            events.append(Event(n, self.current_time + link_delay))
            
        return events
    
    def run_loop(self):
        while len(self.pending) > 0:

            # evento com menor delay, delay necessario?
            messages, time = self._next_messages()
            self.current_time = time
            self.n_rounds += 1
            # dict destino -> lista de msgs
            group = {}
            for m in messages:
                # drop message
                if random.random() <= self.loss_rate:
                    continue

                g = group.get(m.dst)
                if not g:
                    g = []
                    group[m.dst] = g

                g.append(m)
                
            if self.target_value == None:
                new = self._handle_termination_flowsums(group)
            else:
                new = self._handle_termination_rmse(group)
            
            # TODO: por delay nos events
            self.pending.append(new)
            #self.pendingPrint()

        return self.current_time

    
    def _handle_termination_rmse(self, group):
        
        new = [] 
        square_error_sum = 0
        
        for dst, msgs in group.items():
            node = self.nodes[dst]
            node.handle_messages(msgs)  
            gen, node_local_estimate = node.generate_messages_termination_rmse()
            square_error_sum += (node_local_estimate - self.target_value) ** 2
            new.append(gen)
            
        rmse = math.sqrt(square_error_sum / len(self.nodes))
        
        print('round: {} with time: {} -> rmse: {}'.format(self.n_rounds, self.current_time, rmse))
        
        if (rmse > self.target_rmse):
            return self._create_events(new)
        else:
            return []
    
    
    def _handle_termination_flowsums(self, group):
        
        new = [] 
        flowsums = 0
        
        for dst, msgs in group.items():
            node = self.nodes[dst]
            node.handle_messages(msgs)  
            gen, node_flow_sum = generate_messages_termination_flowsums()
            flowsums += node_flow_sum
            new.append(gen)
            
        print('round: {} with time: {} -> flowSums: {}'.format(self.n_rounds, self.current_time, flowsums))
        
        if (flowsums > 0):
            return self._create_events(new)
        else:
            return []
        
    
    # vai buscar e remove do pending as mensagens com menor delay
    # devolve lista de mensagens e delay
    def _next_messages(self):
        time = sys.maxsize
        messages = []
        for m in self.pending:

            if m[0].time < time:
                messages = []
                time = m[0]
            
            if m[0].time == time:
                messages.append(m[1])
        
        for m in messages:
            self.pending.remove(m)

        return messages, time

class Event:
    def __init__(self, message, time):
        self.message = message
        self.time = time

    # TODO antigo, remover se não for preciso:
    def putTimeout(self, event):
        self.pending.append((self.current_time + event.time, event))

    def putSingular(self, event):
        if event is not None:
            link = self.distances[(event.getSrc(), event.getDst())]
            if random.random() > link.loss_rate:
                # - schedule new messages
                self.pending.append((self.current_time + link.delay, event))

    def putList(self, events):
        for e in events:
            # > set the delay according to 'self.distances'
            self.putSingular(e)
        print("c_time: ", self.current_time)


    def pendingPrint(self):
        print("pending.....")
        for e in self.pending:
            print(e[0], vars(e[1]))



# - nodes: {0: Node, 1: Node, 2: Node, ...}
def graphToNodesAndDistances(graph, fanout):
    g_nodes = {}
    g_distances = {}
    
    for n in graph:
        edges = [e for e in graph.edges(n)]
        neighbours = [n for n in graph.neighbors(n)]
        input = random.randint(5, 10)
        g_nodes[n] = nodes.FlowNode(n, neighbours, input)
        
        for e in edges:
            g_distances[e] = graph.get_edge_data(e[0], e[1])['weight']
    
    return g_nodes, g_distances


def main():
    graph = graphGen.randomG(10, 3, 10)  # gera grafo
    nodes = graphToNodesAndDistances(graph, 1)

    loss_rate = 0
    sim = Simulator(nodes, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start(starting_node, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
