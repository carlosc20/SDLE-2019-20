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

    def __init__(self, graph, loss_rate, input_sum, confidence_value, t_type = 'rmse', termination_func = None, aggregation = 'AVERAGE'):
        self.termination_func = termination_func
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.graph = graph
        self.current_time = 0
        self.pending = [] # [Event]
        self.input_sum = input_sum
        self.t_type = t_type
        if aggregation == 'AVERAGE':
            self.target_value = input_sum / len(self.graph)
        self.confidence_value = confidence_value
        self.timeout_mode = timeout_mode
        
        # para o sincrono
        self.n_rounds = 0



    def start(self):
        # primeira ronda de mensagens
        messages = []
        for n in self.graph.nodes:
        
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
            timeouts = {}
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
            new = self._handle_group_msg(self, group, graph)
            terminated = False
            if self.t_type is 'flowsums':
                terminated = self.check_terminate_flowsums(self.graph, self.input_sum, self.confidence_value)
            else:           
                terminated = self.check_terminate_rmse(self.graph, self.target_value, self.confidence_value)
            
            if not terminated:
                new = self._create_events(new)
            else:
                new = []
                   
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


    def _handle_group_msg(self, group, graph):
        new = [] 
        for dst, msgs in group.items():
            node = graph.nodes[dst]['flownode']
            gen = node.handle_messages(msgs)  
            new += gen
        return new

    # uses the sum of all flows as limit to termination. If the sum is equal to remainder convergion has been reached
    def check_terminate_flowsums(self, graph, input_sum, confidence_value):
        flowsums = 0
        for n in graph.nodes:
            flowsums += sum(graph.nodes[n]['flownode'].flows.values())
        
        print('flowsums: ', flowsums)
        r_up = input_sum % len(graph) + confidence_value
        r_down = input_sum % len(graph) - confidence_value
        return flowsums > r_up or flowsums < r_down


    # creates new messages from each node. If reached the termination limit no messages are considered.
    # uses RMSE as limit to termination
    def check_terminate_rmse(self, graph, target_value, target_rmse):
            
        square_error_sum = 0

        for n in graph.nodes:
            node = graph.nodes[n]['flownode']
            square_error_sum += (node.local_estimate - target_value) ** 2
        rmse = math.sqrt(square_error_sum / len(graph))
        print('rmse: ', rmse)

        return rmse > target_rmse


class TimeoutSupportiveSimulator(Simulator):
    def __init__(self, graph, loss_rate, input_sum, confidence_value, t_type = 'rmse', termination_func = None, aggregation = 'AVERAGE'):
        super().__init__(graph, loss_rate, input_sum, confidence_value, t_type, termination_func, aggregation)


    def start(self):
        # primeira ronda de mensagens
        messages = []
        for n in self.graph.nodes:
            node = self.graph.nodes[n]['flownode']
            messages += node.generate_messages()
            mensagens += message.Timeout()
                
        self.pending += self._create_events(messages)

        # run the simulation loop
        return self.run_loop()


    def _create_events(self, timeouts_list, message_list):
        events = []
        for n in message_list:
            link_delay = self.graph.get_edge_data(n.src, n.dst)['weight']
            events.append(Event(n, self.current_time + link_delay))

        for t in timeouts_list:
            link_delay = t.time
            events.append(Event(t, self.current_time + link_delay))

        return events
    

      def _handle_timeouts(self, timeouts):
        newTimeouts = []
        newMsgs = []
        for dst, msgs in timeouts.items():
            node = graph.nodes[dst]['flownode']
            t, msgs = node._handle_timeouts()
            newTimeouts += t
            newMsgs += msgs

        return self._create_events(newTimeouts, newMsgs)

    def run_loop(self):
        while len(self.pending) > 0:
            #print(self.pending)
            # evento com menor delay, delay necessario?
            messages, time = self._next_messages()
            self.current_time = time
            self.n_rounds += 1
            # dict destino -> lista de msgs
            group = {}
            timeouts = {}
            for m in messages:
                # drop message
                if type(m) is message.Timeout:
                    timeouts[m.dst] = m
                else:
                    if random.random() <= self.loss_rate:
                        continue

                    g = group.get(m.dst)
                    if not g:
                        g = []
                        group[m.dst] = g

                    g.append(m)

            #neste caso retorna sempre []
            self._handle_group_msg(self, group, graph)

            new = self._handle_timeouts(timeouts)
            terminated = False
            if self.t_type is 'flowsums':
                terminated = self.check_terminate_flowsums(self.graph, self.input_sum, self.confidence_value)
            else:           
                terminated = self.check_terminate_rmse(self.graph, self.target_value, self.confidence_value)
            
            if terminated:
                new = []
            
            # TODO: por delay nos events
            self.pending += new

            if self.n_rounds == 5:
                #self._addMembers(2, 2, 1, 10)
                self._removeMembers(2)
            
            #self.pendingPrint()

        return self.current_time



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


def buildNode(id, node_type, input, neighbours, max_rounds=None, timeout=None):
    if node_type == 'normal':
        node = nodes.FlowNode(id, neighbours, input)
    elif node_type == 'timeout':
        node = nodes.TimeoutFlowNode(id, neighbours, input, timeout)
    else:
        node = nodes.SelfTerminateIterNode(id, neighbours, input, max_rounds)
    return node

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
