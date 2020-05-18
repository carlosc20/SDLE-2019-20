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

    def __init__(self, graph, loss_rate, input_sum = 0, target_rmse = None, termination_func = None, aggregation = 'AVERAGE'):
        self.termination_func = termination_func
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
                messages += self.graph.nodes[n]['flownode'].generate_messages()
            else:
                messages += self.graph.nodes[n]['flownode'].generate_messages()
                
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
                
            if self.termination_func is not None:
                self.termination_func(group, self.graph) # usar partial (do functools) para passar funcao com args adicionais ex: termination_func(target_value = 1, target_rmse = 2)

            # apagar se codigo a cima funcionar
            if self.target_value is None:
                new = GlobalTerminateFlowSumNode.handle_termination(group, self.graph)
                if new:
                    new = self._create_events(new)
            else:
                #print('round: {} with time: {} -> rmse: {}'.format(self.n_rounds, self.current_time, rmse))
                new = GlobalTerminateRMSENode.handle_termination(group, self.graph, self.target_value, self.target_rmse)
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
    self.graph = graph
    for n in removed_nodes:
        neighbors = n.neighbors
        for nei in neighbors:
            node = self.graph.nodes[nei]['flownode']
            node.removeNeighbour(n)

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
    print("teste")
    graph = graphGen.randomG(10, 3, 10)  # gera grafo
    graph, inputs_sum = graphToNodesAndDistances(graph, 1)

    loss_rate = 0
    sim = Simulator(graph, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start()  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
