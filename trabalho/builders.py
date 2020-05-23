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

    #for adding members
    def build_with_simulator(self, simulator):
        self.simulator = simulator


    def with_loss_rate(self, loss_rate):
        self.simulator.loss_rate = loss_rate


    def with_agregation_type(self, aggregation_type):
        self.simulator.aggregation_type = aggregation_type


    def with_confidence_value(self, confidence_value):
        self.simulator.confidence_value = confidence_value


    def with_flowsums_termination(self):
        self.simulator.t_type = "flowsums"      


    def with_rmse_termination(self):
        self.simulator.t_type = "rmse"   

    
    def with_self_termination_by_rounds(self, max_rounds):
        self.simulator.t_type = "self"
        self.simulator.node_termination_component = "max_rounds"
        self.simulator.max_rounds = max_rounds


    def with_self_termination_by_min_dif(self, max_rounds, min_dif):
        self.simulator.t_type = "self"
        self.simulator.node_termination_component = "min_dif"
        self.simulator.max_rounds = max_rounds
        self.simulator.min_dif = min_dif
        

    def with_timeout_protocol(self, timeout_value):
        self.simulator.base_node_type = "timeout"
        self.simulator.timeout_value = timeout_value


    #(numero de nodos a adicionar, numero de conexções por nodo, input de cada nodo, ao fim de quantas rondas é ativado, se se repete, peso das conexões)
    def with_scheduled_add_members_event(self, numberToAdd, numberOfConnections, input, n_rounds, repeatable,  w=None):
        self.simulator.graph_events['add_members'] = events.AddMembers(numberToAdd, numberOfConnections, input, n_rounds, repeatable, w)


    def with_scheduled_remove_members_event(self, numberToRemove, n_rounds, repeatable):
        self.simulator.graph_events['remove_members'] = events.RemoveMembers(numberToRemove, n_rounds, repeatable)
  

    def _build_nodes_graph(self, graph, fanout, inputs):
        g_nodes = {}
        g_distances = {}
        inputs_sum = 0
        
        for n in graph:
            edges = [e for e in graph.edges(n)]
            neighbours = [n for n in graph.neighbors(n)]
            inputs_sum += inputs[n]
            g_nodes[n] = self.buildNode(n, inputs[n], neighbours)

            nx.set_node_attributes(graph, g_nodes, 'flownode')
        return graph, inputs_sum


    def buildNode(self, id, input, neighbours):
        if self.simulator.base_node_type == 'normal':
            node = nodes.FlowNode(id, neighbours, input)
        else:
            node = nodes.TimeoutFlowNode(id, neighbours, input, self.simulator.timeout_value)

        if self.simulator.node_termination_component == 'max_rounds':
            component = nodes.SelfTerminateRoundsComponent(node, self.simulator.max_rounds)

        elif self.simulator.node_termination_component == 'min_dif':
            component = nodes.SelfTerminateDifComponent(node, self.simulator.max_rounds, self.simulator.min_dif)
        
        else:
            component = None

        node.set_termination_component(component)

        return node

    def build(self, fanout, graph, inputs):
        #TODO fanout
        graph, inputs_sum = self._build_nodes_graph(graph, fanout, inputs)
        
        self.simulator.input_sum = inputs_sum
        if self.simulator.aggregation_type == 'average':            
            self.simulator.target_value = inputs_sum / len(graph)
        else:
            print("unavailable")
            #TODO
        
        self.simulator.graph = graph

        return self.simulator


def main():
    G = graphGen.randomG(5,3)
    inputs = [1] * len(G)
    nx.draw(G, with_labels=True)
    plt.show()
        
    sim_builder = builders.SimulatorBuilder()
    #as an example, default is already 0
    sim_builder.with_loss_rate(0)
    sim_builder.with_agregation_type('average')
    #sim_builder.with_flowsums_termination()
    
    #nodos ficam com resultados diferentes
    #sim_builder.with_self_termination_by_rounds(50)
    sim_builder.with_self_termination_by_min_dif(50, 0.01)
    sim_builder.with_timeout_protocol(100)
    #sim_builder.with_scheduled_add_members_event(1,1,1,2,False,10)
    
    fanout = 1
    sim = sim_builder.build(fanout, G, inputs)
    t = sim.start()
    print("finished in: ",  t)
    
    print("Final estimates: ")
    for n in sim.graph:
        node = sim.graph.nodes[n]['flownode']
        print("node: ", n, " est: ", node.local_estimate)
    


if __name__ == "__main__":
    main()
