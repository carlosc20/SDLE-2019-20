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
        self.loss_rate = 0 # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.graph = None
        self.current_time = 0
        self.pending = [] # [Event]
        self.n_rounds = 0

        self.input_sum = None
        self.target_value = None

        self.aggregation_type = "average"
        self.confidence_value = 0.01
        self.termination_type = "rmse"
        self.test_type = "none" 

        self.base_node_type = "normal"
        self.timeout_value = None

        self.node_termination_component = None
        self.max_rounds = None
        self.min_dif = None

        self.estimates_per_round = []

        self.graph_events = {}

        self.message_counter = 0

    def start(self):
        # primeira ronda de mensagens
        messages = []
        timeouts = []
        for n in self.graph.nodes:
            node = self.graph.nodes[n]['flownode']
            messages += node.generate_messages()
            if self.base_node_type == "timeout":
                timeouts.append(message.Timeout(n, 1, self.timeout_value))
                
        self.pending += self._create_events(messages, timeouts)

        return self._run_loop()
    


    def _run_loop(self):
        while len(self.pending) > 0:
            
            # evento com menor delay, delay necessario?
            messages, time = self._next_messages()

            self.current_time = time
            self.n_rounds += 1
            self.update_stored_estimates()
   
            inbox = {} # destino -> lista de msgs
            timeouts = {}
            for m in messages:

                if type(m) is message.Timeout:
                    timeouts[m.dst] = m
                    continue

                # drop message
                if random.random() <= self.loss_rate:
                    continue

                inbox.setdefault(m.dst, []).append(m)
            
                            
            # novas mensagens geradas               
            new = self._handle_group_msg(inbox, self.graph)

            if self.base_node_type == 'timeout':
                new += self._handle_timeouts(timeouts, self.graph)

            terminated = False

            if self.termination_type is 'flowsums':
                terminated = self._check_termination_flowsums(self.graph, self.input_sum, self.confidence_value)
            elif self.termination_type is 'rmse':   
                if self.aggregation_type is 'average':            
                    terminated = self._check_termination_rmse_average(self.graph, self.target_value, self.confidence_value)
                elif self.aggregation_type is 'count':
                    terminated = self._check_termination_rmse_count(self.graph, self.target_value, self.confidence_value)
                else:
                    print("unavailable")
                    #TODO        

            if terminated:
                new = []
                
            self.pending += new
            
            if self.base_node_type == 'timeout':
                self._timeout_cleanup()

            self._message_count(new)

            self._handle_events()

            n_e, rounds_self_term = self.get_stats()

        return self.current_time, self.message_counter, self.n_rounds, n_e, rounds_self_term
    

    def update_stored_estimates(self):
        aux = []
        for n in self.graph:
            node = self.graph.nodes[n]['flownode']
            m = 1 / node.local_estimate if (self.aggregation_type is 'count' and node.local_estimate != 0) else node.local_estimate
            aux.append(m)
        self.estimates_per_round.append(aux)

    
    def get_stats(self):
        rounds_self_term = [0] * len(self.graph)
        for n in self.graph:
            node = self.graph.nodes[n]['flownode']
            if self.termination_type is 'self' or self.test_type is 'self_testing':
                rounds_self_term[n] = node.getConsecutiveRounds()

        return self.estimates_per_round, rounds_self_term


    def _message_count(self, events):
        for e in events:
            if type(e.message) is not message.Timeout:
                self.message_counter += 1 


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
            if t != None:
                link_delay = t.time
                new_events.append(events.Event(t, self.current_time + link_delay))
            
        return new_events


    def _handle_group_msg(self, inbox, graph):
        new = [] 
        for dst, msgs in inbox.items():
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

        for dst, timeout in timeouts.items():
            node = graph.nodes[dst]['flownode']
            if not node.old_timeout(timeout):
                msgs = node.handle_transition()
                node.reset_rounds()
                newMsgs += msgs

        for n in graph.nodes:
            node = graph.nodes[n]['flownode']
            if node.latest_timeout != None:
                newTimeouts.append(node.take_latest_timeout())
                for e in self.pending:
                    if type(e.message) is message.Timeout and node.old_timeout(e.message):
                        self.pending.remove(e)

        return self._create_events(newMsgs, newTimeouts)

    
    def _timeout_cleanup(self):
        for n in self.graph.nodes:
            node = self.graph.nodes[n]['flownode']
            if not node.termination_component.working:
                for e in self.pending:
                    if type(e.message) is message.Timeout:
                        self.pending.remove(e)
                    
                    
    # uses the sum of all flows as limit to termination. If the sum is equal to remainder convergion has been reached
    def _check_termination_flowsums(self, graph, input_sum, confidence_value):
        flowsums = 0
        for n in graph.nodes:
            flowsums += sum(graph.nodes[n]['flownode'].flows.values())
        
        r = input_sum % len(graph)
        print('flowsums: ', math.sqrt((flowsums - r) ** 2))
        return (math.sqrt((flowsums - r) ** 2) / len(graph)) < confidence_value


    # uses RMSE as limit to termination
    def _check_termination_rmse_average(self, graph, target_value, target_rmse):
            
        square_error_sum = 0

        for n in graph.nodes:
            node = graph.nodes[n]['flownode']
            square_error_sum += (node.local_estimate - target_value) ** 2
        rmse = math.sqrt(square_error_sum / len(graph))
        #print('rmse: ', rmse)

        return rmse < target_rmse


    # uses RMSE as limit to termination
    def _check_termination_rmse_count(self, graph, target_value, target_rmse):
            
        square_error_sum = 0

        for n in graph.nodes:
            node = graph.nodes[n]['flownode']
            le = 1 / node.local_estimate if node.local_estimate != 0 else 0
            square_error_sum += (le - target_value) ** 2
        rmse = math.sqrt(square_error_sum / len(graph)) 
        #print('rmse: ', rmse)
        return rmse < target_rmse


    def _handle_events(self):
        for (k, v) in self.graph_events.items():
            v.ticker += 1
            if v.ticker == v.n_rounds:
                if k == 'add_members':
                    print("adding members")
                    self._addMembers(v)
                elif k == 'remove_members':
                    print("removing members")
                    self._removeMembers(v)
                elif k == 'change_inputs':
                    print("change inputs")
                    self._changeInputs(v)
                else:
                    print("departure arrival")
                    self._DAMembers(v)
                if v.repeatable:
                    v.ticker = 0


    

    def _changeInputs(self, ci):
        for (n, i) in ci.input_by_nodes.items():
            node = self.graph.nodes[n]['flownode']
            node.input = i


    #input igual para todos os nodos adicionados
    def _addMembers(self, add_e):
        graphGen.addNodes(self.graph, add_e.numberToAdd, add_e.numberOfConnections, add_e.input, self, add_e.w)
        self.input_sum += add_e.input * add_e.numberToAdd

        if self.aggregation_type == 'average':            
            self.target_value = self.inputs_sum / len(self.graph)
        elif self.aggregation_type == 'count':
            self.target_value = len(self.graph)
        else:
            print("unavailable")
            #TODO

    #só usar com grafos maiores. perigosa
    def _removeMembers(self, rem_e):
        removed = graphGen.removeNodes(self.graph, rem_e.numberToRemove) 
        
        for r in removed:
            self.input_sum -= r.input 

        if self.aggregation_type == 'average':            
            self.target_value = self.inputs_sum / len(self.graph)
        elif self.aggregation_type == 'count':
            self.target_value = len(self.graph)
        else:
            print("unavailable")
            #TODO

        #remove messages to removed members
        removed_ids = [n.id for n in removed]
        to_remove = []
        for e in self.pending:
            if e.message.dst in removed_ids or e.message.src in removed_ids:
                to_remove.append(e)

        for e in to_remove:
            self.pending.remove(e)

        #nx.draw(self.graph, with_labels=True)
        #plt.show()

    def _DAMembers(self, da_msg):
        for n in range(da_msg.numberToRemove):
            node = self.graph.nodes[n]['flownode']
            node.__init__(node.id, node.neighbours, node.input)

        i = 0
        for n in self.graph.nodes:
            node = self.graph.nodes[n]['flownode']
            print(node.local_estimate)
            i += 1

        print(i)