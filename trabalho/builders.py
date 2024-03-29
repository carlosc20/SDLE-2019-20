import networkx as nx
import message
import nodes
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
from nodes import *
import simulator
import events

class SimulatorBuilder:
    def __init__(self):
        self.simulator = simulator.Simulator()
        self.simulator.is_timeout = False
        self.simulator.base_node_type = "normal"

    #for adding members
    def build_with_simulator(self, simulator):
        self.simulator = simulator
        self.simulator.is_timeout = False
        return self


    def with_loss_rate(self, loss_rate):
        self.simulator.loss_rate = loss_rate
        return self


    def with_agregation_type(self, aggregation_type):
        self.simulator.aggregation_type = aggregation_type
        return self


    def with_confidence_value(self, confidence_value):
        self.simulator.confidence_value = confidence_value
        return self


    def with_flowsums_termination(self):
        self.simulator.termination_type = "flowsums"      
        return self


    def with_rmse_termination(self):
        self.simulator.termination_type = "rmse"   
        return self
    

    def with_self_termination_by_rounds(self, max_rounds):
        self.simulator.termination_type = "self"
        self.simulator.node_termination_component = "max_rounds"
        self.simulator.max_rounds = max_rounds
        return self


    def with_self_termination_by_min_dif(self, max_rounds, min_dif):
        self.simulator.termination_type = "self"
        self.simulator.node_termination_component = "min_dif"
        self.simulator.max_rounds = max_rounds
        self.simulator.min_dif = min_dif
        return self

    
    def with_min_dif_testing(self, min_dif):
        self.simulator.test_type = "self_testing"
        self.simulator.node_termination_component = "min_dif"
        self.simulator.max_rounds = 10000000
        self.simulator.min_dif = min_dif
        return self
        

    def with_multicast_protocol(self, multi):
        self.simulator.base_node_type = "multicast"
        self.multi = multi
        return self

    def with_evaluated_multicast_protocol(self, multi):
        self.simulator.base_node_type = "emulticast"
        self.multi = multi
        return self

    def with_timeout_protocol(self, timeout_value):
        self.simulator.is_timeout = True
        self.simulator.timeout_value = timeout_value
        return self


    #(numero de nodos a adicionar, numero de conexções por nodo, input de cada nodo, ao fim de quantas rondas é ativado, se se repete, peso das conexões)
    def with_scheduled_add_members_event(self, numberToAdd, numberOfConnections, input, n_rounds, repeatable,  w=None):
        self.simulator.graph_events['add_members'].append(events.AddMembers(numberToAdd, numberOfConnections, input, n_rounds, repeatable, w))
        return self


    def with_scheduled_remove_members_event(self, numberToRemove, n_rounds, repeatable):
        self.simulator.graph_events['remove_members'].append(events.RemoveMembers(numberToRemove, n_rounds, repeatable))
        return self

    ## Só usar com flownode normal!!!!
    def with_departure_arrival_members_event(self, numberToRemove, n_rounds, repeatable):
        self.simulator.graph_events['departure_arrival_members'].append(events.DepartureArrivalMembers(numberToRemove, n_rounds, repeatable))
        return self

    # input_by_node = {node:input,....}
    def with_scheduled_change_inputs_event(self, input_by_node, n_rounds):
        self.simulator.graph_events['change_inputs'].append(events.ChangeInputs(input_by_node, n_rounds))
        return self
  

    def _build_nodes_graph(self, input_graph, inputs):
        g_nodes = {}
        inputs_sum = 0
        
        graph = input_graph.copy()

        for n in graph:
            edges = [e for e in graph.edges(n)]
            neighbours = [n for n in graph.neighbors(n)]
            inputs_sum += inputs[n]
            g_nodes[n] = self.buildNode(n, inputs[n], neighbours)

            nx.set_node_attributes(graph, g_nodes, 'flownode')
        return graph, inputs_sum


    def buildNode(self, id, input, neighbours):

        if self.simulator.base_node_type == 'normal':
            if not self.simulator.is_timeout:
                node = nodes.FlowNode(id, neighbours, input)
            else:
                node = nodes.TimeoutFlowNode(id, neighbours, input, self.simulator.timeout_value)

        elif self.simulator.base_node_type == 'multicast':
            if not self.simulator.is_timeout:
                node = nodes.MulticastFlowNode(id, neighbours, input, self.multi)
            else:
                node = nodes.TimeoutMulticastFlowNode(id, neighbours, input, self.multi, self.simulator.timeout_value)

        elif self.simulator.base_node_type == 'emulticast':
            if not self.simulator.is_timeout:
                node = nodes.EvaluatedMulticastFlowNode(id, neighbours, input, self.multi)
            else:
                node = nodes.TimeoutEvaluatedMulticastFlowNode(id, neighbours, input, self.multi, self.simulator.timeout_value)

        else:
            raise



        if self.simulator.node_termination_component == 'max_rounds':
            component = nodes.SelfTerminateRoundsComponent(node, self.simulator.max_rounds)

        elif self.simulator.node_termination_component == 'min_dif':
            for_testing = False
            if self.simulator.termination_type == 'self_testing':
                for_testing = True
            component = nodes.SelfTerminateDifComponent(node, self.simulator.max_rounds, self.simulator.min_dif, for_testing)
        
        else:
            component = None

        node.set_termination_component(component)

        return node

    def build(self, graph, inputs):
        graph, inputs_sum = self._build_nodes_graph(graph, inputs)
        
        self.simulator.input_sum = inputs_sum
        if self.simulator.aggregation_type == 'average':            
            self.simulator.target_value = inputs_sum / len(graph)
        elif self.simulator.aggregation_type == 'count':
            self.simulator.target_value = len(graph)
        else:
            print("unavailable")
            #TODO
        
        self.simulator.graph = graph

        return self.simulator


def main():
    G = graphGen.randomG(1000,3,10)
    inputs = [1] * (len(G))
        
    sim_builder = SimulatorBuilder()
    #as an example, default is already 0
    #sim_builder.with_multicast_protocol(1)
    sim_builder.with_agregation_type('average')
    sim_builder.with_confidence_value(0.001)
    sim_builder.with_min_dif_testing(0.01)
    
    #nodos ficam com resultados diferentes
    #sim_builder.with_self_termination_by_rounds(50)
    #sim_builder.with_self_termination_by_min_dif(50, 0.01)
    #sim_builder.with_timeout_protocol(100)
    #inputs_by_node = dict.fromkeys(range(len(G)), 2)
    #sim_builder.with_scheduled_change_inputs_event(inputs_by_node, 5)
    #sim_builder.with_scheduled_add_members_event(1,1,1,2,False,10)
    
    sim = sim_builder.build(G, inputs)
    t, c, r, y, z = sim.start()
    
    print("finished in: ",  t, " with ", c, " messages sent", " rounds: ", r, max(z))
    
    #print("Final estimates: ")
   # for n in sim.graph:
    #    node = sim.graph.nodes[n]['flownode']
     #   print("node: ", n, " est: ", node.local_estimate)
    


if __name__ == "__main__":
    main()
