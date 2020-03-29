import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import nodes
     

class Sim:
    # - nodes: {0: Node, 1: Node, 2: Node}
    # - distances: {(0,1): 103, (0,2): 40, ...}
    def __init__(self, nodestore, distances):
        self.nodestore = nodestore
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [(delay, (src, dst, msg))]

    def start(self, starting_node, initial_msg):
        # schedule first event
        # for i in self.nodes: -> não sei se passei mal ou o stor queria isto
        sNode = self.nodestore[starting_node]

        event = (0, sNode.createMsg(initial_msg))
        self.pending.append(event)

        # run the simulation loop
        return self.run_loop()

    def run_loop(self):
        while len(self.pending) > 0:
            # - find in 'self.pending' the next message that should be delivered
            tmp_future_time = sys.maxsize
            index = 0
            for i in range(len(self.pending)):
                if self.pending[i][0] <= tmp_future_time:
                    index = i
                    tmp_future_time = self.pending[i][0]
            # - handle event in its destination
            event = self.pending[index][1]

            # works with timeout (src == dst)
            node = self.nodestore[event.getDst()]
            res = []
            if isinstance(event, nodes.Timeout):
                res = node.handleTimeout(event.eventId)
            elif isinstance(event, nodes.EagerMessage):
                res = node.handleEager(event)
            elif isinstance(event, node.LazyMessage):
                res = node.handleLazy(event)
            elif isinstance(event, node.SendRequest):
                res = node.handleSendRequest(event)
            elif isinstance(event, node.PayloadDelivery):
                res = node.handlePayload(event)
            self.computeDelays(res, index)
                
        return self.current_time

    def computeDelays(self, events, index):
        self.current_time = self.pending[0][0]
        del self.pending[index]
        # - nodo não foi visitado
        if not isinstance(events, list):
            events = [events]
            if len(events) > 0:
                for e in events:
                    # > set the delay according to 'self.distances'
                    tmp_delay = self.distances[(e.getSrc(), e.getDst())]
                    messages_to_neighbours = (self.current_time + tmp_delay, e)
                    # - schedule new messages
                    self.pending.append(messages_to_neighbours)

                print(self.pending)
                # - update 'self.current_time'
                print("c_time: ", self.current_time)


# dado um grafo G simula N tentativas com N random raizes e calcula Min, Media, Max.
# testar com vários tipos de grafos 
# def analysis():

def connector(graph, type='normal', **kwargs):
    nodestore = {}
    distances = {}
    for n in graph:
        edges = [e for e in graph.edges(n)]
        # print("edg ", edges)
        neighbours = [n for n in graph.neighbors(n)]
        # print("nei ", neighbours)
        if type == 'normal':
            nodestore[n] = nodes.Node(neighbours)
        elif type == 'broadcast':
            nodestore[n] = nodes.BroadcastNode(neighbours, n, kwargs.get('fanout'))
        elif type == 'timeout':
            nodestore[n] = nodes.TimeoutNode(neighbours, n, kwargs.get('fanout'))
        for e in edges:
            distances[e] = graph.get_edge_data(e[0], e[1])['weight']
    # print(distances)
    return nodestore, distances


def main():
    g = graphGen.randomG(10, 10)  # gera grafo
    nodestore, distances = connector(g, 'timeout', fanout=1)  # converte grafo gerado em input para simulador
    sim = Sim(nodestore, distances)  # cria classe
    time = sim.start(0, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(g, with_labels=True)


if __name__ == "__main__":
    main()
