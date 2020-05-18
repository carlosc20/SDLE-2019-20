import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import message
import nodes
from nodes import *
import random
import math


# TODO: Fazer mudanças de ligações no grafo em runtime
# mudanças no grafo, heurísticas para o "fanout" e o método de terminação local e não modo "deus" do simulador

class Simulator:

    def __init__(self, nodes, distances, loss_rate, input_sum = 0, target_rmse = None, termination_func = None, aggregation = 'AVERAGE'):
        self.termination_func = termination_func
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.nodes = nodes # dict: nr -> Node
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [Event]

        if aggregation == 'AVERAGE':
            self.target_value = input_sum / len(self.nodes)
        self.target_rmse = target_rmse
        
        # para o sincrono
        self.n_rounds = 0



    def start(self):
        # primeira ronda de mensagens
        messages = []
        for n in self.nodes.values():
            messages += n.generate_messages()

        self.pending += self._create_events(messages)

        # run the simulation loop
        return self.run_loop()


    def _create_events(self, message_list):
        events = []
        for n in message_list:
            link_delay = self.distances[(n.src, n.dst)]
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
                
            if self.termination_func is not None:
                self.termination_func(group, nodes) # usar partial (do functools) para passar funcao com args adicionais ex: termination_func(target_value = 1, target_rmse = 2)

            # apagar se codigo a cima funcionar
            if self.target_value is None:
                new = GlobalTerminateFlowSumNode.handle_termination(group, self.nodes)
                if new:
                    new = self._create_events(new)
            else:
                #print('round: {} with time: {} -> rmse: {}'.format(self.n_rounds, self.current_time, rmse))
                new = GlobalTerminateRMSENode.handle_termination(group, self.nodes, self.target_value, self.target_rmse)
                if new:
                    new = self._create_events(new)
                
            
            # TODO: por delay nos events
            self.pending += new
            #self.pendingPrint()

        return self.current_time


    

        
    
    # vai buscar e remove do pending as mensagens com menor delay
    # devolve lista de mensagens e delay
    def _next_messages(self):
        time = sys.maxsize
        messages = []
        toRemove = []
        for e in self.pending:

            if e.time < time:
                messages.clear()
                toRemove.clear()
                time = e.time
            
            if e.time == time:
                messages.append(e.message)
                toRemove.append(e)
        
        for e in toRemove:
            self.pending.remove(e)

        return messages, time

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
        
        for e in edges:
            g_distances[e] = graph.get_edge_data(e[0], e[1])['weight']
    
    return g_nodes, g_distances, inputs_sum


def main():
    print("teste")
    graph = graphGen.randomG(10, 3, 10)  # gera grafo
    nodes, distances, inputs_sum = graphToNodesAndDistances(graph, 1)

    loss_rate = 0
    # passar termination_func
    # https://stackoverflow.com/questions/803616/passing-functions-with-arguments-to-another-function-in-python
    sim = Simulator(nodes, distances, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start()  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
