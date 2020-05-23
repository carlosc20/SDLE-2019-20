import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import message
import nodes
from nodes import *
import random
import math
import events

class Simulator:

    def __init__(self):
        #TODO não sei o que é isto
        self.termination_func = None
        self.loss_rate = 0 # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.graph = None
        self.current_time = 0
        self.pending = [] # [Event]
        self.n_rounds = 0

        self.input_sum = None
        self.target_value = None

        self.aggregation_type = "average"
        self.confidence_value = 0.01
        self.t_type = "rmse"

        self.base_node_type = "normal"
        self.timeout_value = None

        self.special_node_type = None
        self.max_rounds = None

        self.graph_events = {}

    def start(self):
        # primeira ronda de mensagens
        messages = []
        timeouts = []
        for n in self.graph.nodes:
            node = self.graph.nodes[n]['flownode']
            messages += node.generate_messages()
            if self.base_node_type == "timeout":
                timeouts += message.Timeout(n, timeout_time)
                
        self.pending += self._create_events(messages, timeouts)

        # run the simulation loop
        return self.run_loop()
    

    
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

    
    def _create_events(self, message_list, timeout_list):
        new_events = []
        for n in message_list:
            link_delay = self.graph.get_edge_data(n.src, n.dst)['weight']
            new_events.append(events.Event(n, self.current_time + link_delay))
        
        for t in timeout_list:
            link_delay = t.time
            new_events.append(events.Event(t, self.current_time + link_delay))
            
        return new_events


    def _handle_group_msg(self, group, graph):
        new = [] 
        for dst, msgs in group.items():
            node = graph.nodes[dst]['flownode']
            gen = node.handle_messages(msgs)  
            new += gen

        if new:
            return self._create_events(new, [])
        #timeout node case
        else:
            return new


    def _handle_timeouts(self, timeouts, graph):
        newTimeouts = []
        newMsgs = []
        for dst in timeouts.keys():
            node = graph.nodes[dst]['flownode']
            t, msgs = node._handle_timeouts()
            newTimeouts += t
            newMsgs += msgs

        return self._create_events(newTimeouts, newMsgs)


    # uses the sum of all flows as limit to termination. If the sum is equal to remainder convergion has been reached
    def check_terminate_flowsums(self, graph, input_sum, confidence_value):
        flowsums = 0
        for n in graph.nodes:
            flowsums += sum(graph.nodes[n]['flownode'].flows.values())
        
        print('flowsums: ', flowsums)
        r_up = input_sum % len(graph) + confidence_value
        r_down = input_sum % len(graph) - confidence_value
        return flowsums < r_up and flowsums > r_down

    # uses RMSE as limit to termination
    def check_terminate_rmse(self, graph, target_value, target_rmse):
            
        square_error_sum = 0

        for n in graph.nodes:
            node = graph.nodes[n]['flownode']
            square_error_sum += (node.local_estimate - target_value) ** 2
        rmse = math.sqrt(square_error_sum / len(graph))
        print('rmse: ', rmse)

        return rmse < target_rmse


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

                if type(m) is message.Timeout:
                    timeouts[m.dst] = m
                    continue

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


            new = self._handle_group_msg(group, self.graph)

            if self.base_node_type == 'timout':
                new += self._handle_timeouts(timeouts, self.graph)

            terminated = False

            if self.t_type is 'flowsums':
                terminated = self.check_terminate_flowsums(self.graph, self.input_sum, self.confidence_value)
            elif self.t_type is 'rmse':           
                terminated = self.check_terminate_rmse(self.graph, self.target_value, self.confidence_value)
            else:
                print("unavailable")

            if terminated:
                new = []
                   
            self.pending += new

            self._handle_events()

        return self.current_time


    def _handle_events(self):
        for (k, v) in self.graph_events.items():
            v.ticker += 1
            if v.ticker == v.n_rounds:
                if k == 'add_members':
                    self._addMembers(v)
                else:
                    self._removeMembers(v)
            if v.repeatable:
                v.ticker = 0

    #input igual para todos os nodos adicionados
    def _addMembers(self, add_e):
        graphGen.addNodes(self.graph, add_e.numberToAdd, add_e.numberOfConnections, add_e.input, self, add_e.w)
        self.input_sum += add_e.input * add_e.numberToAdd

        #assume average
        self.target_value = self.input_sum / len(self.graph)
        nx.draw(self.graph, with_labels=True)
        plt.show()


    #só usar com grafos maiores. perigosa
    def _removeMembers(self, rem_e):
        removed = graphGen.removeNodes(self.graph, rem_e.numberToRemove) 
        
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