import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import nodes
import random

# Carlos: Fazer mudanças de ligações no grafo em runtime

class Link:
    def __init__(self, delay, loss_rate):
        self.loss_rate = loss_rate
        self.delay = delay


class Sim:
    # - nodes: {0: Node, 1: Node, 2: Node, ...}
    # - distances: {(0,1): Link, (0,2): Link, ...}
    def __init__(self, nodestore, distances, loss_rate):
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.nodestore = nodestore
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [(delay, (src, dst, msg))]

    def start(self, starting_node, initial_msg):
        
        # initialize garbagecollection
        for node in self.nodestore.values():
            self.putTimeout(node.createGarbageCollectionEvent())

        # schedule first event
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

            event = self.pending[index][1]

            # works with timeout (src == dst)
            node = self.nodestore[event.getDst()]
            res = []
            # update time
            self.current_time = self.calcTmpTime(index)
            # - handle event in its destination
            if type(event) is nodes.Timeout:
                action = node.handleTimeout(event.eventId)
                if type(action) is nodes.SendRequest:
                    self.putSingular(action)
                else:
                    self.putTimeout(action)

            elif random.random() > self.loss_rate:
                if type(event) is nodes.EagerMessage:
                    res = node.handleEager(event)
                    self.putList(res[0])
                    self.putSingular(res[1])

                elif type(event) is nodes.LazyMessage:
                    res = node.handleLazy(event)
                    self.putTimeout(res[0])
                    self.putSingular(res[1])

                elif type(event) is nodes.SendRequest:
                    p = node.handleSendRequest(event)
                    self.putSingular(p)

                elif type(event) is nodes.PayloadDelivery: # = eager resposta
                    node.handlePayload(event)

                elif type(event) is nodes.Acknowledgment:
                    node.handleAck(event)

                elif type(event) is nodes.GarbageCollection:
                    res = node.handleGarbageCollection()
                    self.putList(res[0])
                    if res[1] is not None:
                        self.putTimeout(res[1])

            self.pendingPrint()
        return self.current_time


    def calcTmpTime(self, index):
        tmp_time = self.pending[index][0]
        del self.pending[index]
        return tmp_time

    def putTimeout(self, event):
        self.pending.append((self.current_time + event.time, event))

    def putSingular(self, event):
        if event is not None:
            link = self.distances[(event.getSrc(), event.getDst())]
            if random.random() > link.loss_rate:
                # - schedule new messages
                self.pending.append((self.current_time + link.delay, event))

    def putList(self, events):
        for e in events:
            # > set the delay according to 'self.distances'
            self.putSingular(e)
        print("c_time: ", self.current_time)

    def pendingPrint(self):
        print("pending.....")
        for e in self.pending:
            print(e[0], vars(e[1]))



# - nodestore: {0: Node, 1: Node, 2: Node, ...}
# - distances: {(0,1): Link, (0,2): Link, ...}
def connector(graph, fanout):
    nodestore = {}
    distances = {}
    for n in graph:
        neighbours = [n for n in graph.neighbors(n)]
        nodestore[n] = nodes.TimeoutNode(neighbours, n, fanout)

        edges = [e for e in graph.edges(n)]
        for e in edges:
            # TODO parametrizar loss_rate
            distances[e] = Link(graph.get_edge_data(e[0], e[1])['weight'], 0)

    # print(distances)
    return nodestore, distances


def main():
    graph = graphGen.randomG(10, 10)  # gera grafo
    nodestore, distances = connector(graph, 1)  # converte grafo gerado em input para simulador
    loss_rate = 0
    sim = Sim(nodestore, distances, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start(starting_node, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
