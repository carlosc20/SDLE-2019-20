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

    def __init__(self, graph, loss_rate, input_sum, confidence_value, t_type = 'rmse', aggregation = 'AVERAGE'):

        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.graph = graph
        self.current_time = 0
        self.pending = [] # [Event]
        self.input_sum = input_sum
        self.t_type = t_type
        if aggregation == 'AVERAGE':
            self.target_value = input_sum / len(self.graph)
        self.confidence_value = confidence_value
        
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
                
            if self.t_type is 'flowsums':
                new = GlobalTerminateFlowSumNode.handle_termination(group, self.graph, self.input_sum, self.confidence_value)
                if new:
                    new = self._create_events(new)
            else:           
                new = GlobalTerminateRMSENode.handle_termination(group, self.graph, self.target_value, self.confidence_value)
                if new:
                    new = self._create_events(new)
                
            
            # TODO: por delay nos events
            self.pending += new

            if self.n_rounds == 5:
                #self._addMembers(2, 2, 1, 10)
                self._removeMembers(2)
            
            #self.pendingPrint()

        return self.current_time


    #input igual para todos os nodos adicionados
    def _addMembers(self, numberToAdd, numberOfConnections, input, w=None):
        graphGen.addNodes(self.graph, numberToAdd, numberOfConnections, input, self.t_type, w)
        self.input_sum += input * numberToAdd

        #assume average
        self.target_value = self.input_sum / len(self.graph)
        nx.draw(self.graph, with_labels=True)
        plt.show()


    #só usar com grafos maiores. perigosa
    def _removeMembers(self, numberToRemove):
        removed = graphGen.removeNodes(self.graph, numberToRemove) 
        
        for r in removed:
            self.input_sum -= r.input 

        self.target_value = self.input_sum / len(self.graph)

        #remove messages to removed members
        removed_ids = [n.id for n in removed]
        to_remove = []
        for e in self.pending:
            if e.message.dst in removed_ids or e.message.src in removed_ids:
                to_remove.append(e)

        for e in to_remove:
            self.pending.remove(e)

        nx.draw(self.graph, with_labels=True)
        plt.show()



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
def graphToNodesAndDistances(graph, fanout, inputs, node_type='flowSumNode', max_rounds = None):
    g_nodes = {}
    g_distances = {}
    inputs_sum = 0
    
    for n in graph:
        edges = [e for e in graph.edges(n)]
        neighbours = [n for n in graph.neighbors(n)]
        inputs_sum += inputs[n]
        g_nodes[n] = buildNode(n, node_type, inputs[n], neighbours, max_rounds)

        nx.set_node_attributes(graph, g_nodes, 'flownode')
    return graph, inputs_sum


def buildNode(id, node_type, input, neighbours, max_rounds):
    if node_type == 'flowsums':
        node = nodes.GlobalTerminateFlowSumNode(id, neighbours, input)
    elif node_type == 'rmse':
        node = nodes.GlobalTerminateRMSENode(id, neighbours, input)
    else:
        node = nodes.SelfTerminateIterNode(id, neighbours, input, max_rounds)
    return node

def main():
    s_type = 'flowsums'
    #node_type = 'rmseNode'
    #node_type = 'selfNotice'
    G = graphGen.randomG(10,5,10)
    nx.draw(G, with_labels=True)
    plt.show()
        
    inputs = [1,1,1,1,1,1,1,1,1,1]
    graph, input_sum = graphToNodesAndDistances(G, 1, inputs, s_type)
    #graph, input_sum = simulator.graphToNodesAndDistances(G, 1, inputs, node_type, max_rounds = 5)
    
    loss_rate = 0.1
    sim = Simulator(graph, loss_rate, input_sum, 0.01, s_type)
    t = sim.start()
    print("finished in: ",  t)


if __name__ == "__main__":
    main()
