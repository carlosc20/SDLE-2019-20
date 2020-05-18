import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import nodes
import random
import math

# TODO: Fazer mudanças de ligações no grafo em runtime


class Simulator:

    def __init__(self, graph, loss_rate, input_sum = None, target_rmse = None, aggregation = 'AVERAGE'):
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.graph = graph
        self.current_time = 0
        self.pending = [] # [Event]
        if aggregation == 'AVERAGE':
            self.target_value = input_sum / len(self.graph)
        self.target_rmse = target_rmse
        
        # para o sincrono
        self.n_rounds = 0



    def start(self):
        # primeira ronda de mensagens
        messages = []
        for n in self.graph.nodes:
            
            if self.target_value == None:
                messages += self.graph.nodes[n]['flownode'].generate_messages_termination_flowsums()[0]
            else:
                messages += self.graph.nodes[n]['flownode'].generate_messages_termination_rmse()[0]
                
        self.pending += self._create_events(messages)

        # run the simulation loop
        return self.run_loop()


    def _create_events(self, message_list):
        events = []
        for n in message_list:
            link_delay = self.graph.get_edge_data(n.src, n.dst)['weight']
            events.append(Event(n, self.current_time + link_delay))
            
        return events
    
    def run_loop(self):
        while len(self.pending) > 0:
            #print(self.pending)
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
            self.pending += new
            #self.pendingPrint()

        return self.current_time

    # creates new messages from each node. If reached the termination limit no messages are considered.
    # uses RMSE as limit to termination
    def _handle_termination_rmse(self, group):
        
        new = [] 
        square_error_sum = 0
        
        for dst, msgs in group.items():
            node = self.graph.nodes[dst]['flownode']
            node.handle_messages(msgs)  
            gen, node_local_estimate = node.generate_messages_termination_rmse()
            square_error_sum += (node_local_estimate - self.target_value) ** 2
            new += gen
            
        rmse = math.sqrt(square_error_sum / len(self.graph))
        
        print('round: {} with time: {} -> rmse: {}'.format(self.n_rounds, self.current_time, rmse))
        
        if (rmse > self.target_rmse):
            return self._create_events(new)
        else:
            return []
    
    # uses the sum of all flows as limit to termination. If the sum is equal to 0 convergion has been reached
    def _handle_termination_flowsums(self, group):
        
        new = [] 
        flowsums = 0
        
        for dst, msgs in group.items():
            node = self.graph.nodes[dst]['flownode']
            node.handle_messages(msgs)  
            gen, node_flow_sum = node.generate_messages_termination_flowsums()
            flowsums += node_flow_sum
            new += gen
            
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
        toRemove = []
        for e in self.pending:

            if e.time < time:
                messages = []
                toRemove = []
                time = e.time
            
            if e.time == time:
                messages.append(e.message)
                toRemove.append(e)
        
        for e in toRemove:
            self.pending.remove(e)

        return messages, time


def _addConections(self, numberToAdd, numberOfConnections, w=None, input):
    graph, new_nodes = graphGen.addNodes(self.graph, numberToAdd, numberOfConnections, w, input) 
    self.graph = graph
    for n in new_nodes:
        neighbors = n.neighbors
        for nei in neighbors:
            node = self.graph.nodes[nei]['flownode']
            node.addNeighbour(n)


def _removeNodes(self, number):
    graph, removed_nodes = graphGen.addNodes(self.graph, numberToRemove) 



class Event:
    def __init__(self, message, time):
        self.message = message
        self.time = time


# - nodes: {0: Node, 1: Node, 2: Node, ...}
def graphToNodesAndDistances(graph, fanout):
    g_nodes = {}
    g_distances = {}
    inputs_sum = 0
    
    for n in graph:
        edges = [e for e in graph.edges(n)]
        neighbours = [n for n in graph.neighbors(n)]
        input = random.randint(1, 6)
        print(input)
        inputs_sum += input
        g_nodes[n] = nodes.FlowNode(n, neighbours, input)
        
        #for e in edges:
         #   g_distances[e] = graph.get_edge_data(e[0], e[1])['weight']
        nx.set_node_attributes(graph, g_nodes, 'flownode')
    return graph, inputs_sum


def main():
    graph = graphGen.randomG(10, 3, 10)  # gera grafo
    graph, inputs_sum = graphToNodesAndDistances(graph, 1)

    loss_rate = 0
    sim = Simulator(graph, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start(starting_node, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
