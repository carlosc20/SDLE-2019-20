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


class Simulator:
    # - nodes: {0: Node, 1: Node, 2: Node, ...}
    def __init__(self, nodes, loss_rate):
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.nodes = nodes
        self.current_time = 0
        self.pending = [] # [(delay, (src, dst, msg))]


    def start(self, starting_node, initial_msg):
        
        # eventos inicias
        # self.pending.append(event)

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
            node = self.nodes[event.getDst()]
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
                res = node.handle_message(event)

            self.pending.append(res)
            self.pendingPrint()

        return self.current_time


    def calcTmpTime(self, index):
        tmp_time = self.pending[index][0]
        del self.pending[index]
        return tmp_time

    def pendingPrint(self):
        print("pending.....")
        for e in self.pending:
            print(e[0], vars(e[1]))



# - nodes: {0: Node, 1: Node, 2: Node, ...}
def graphToNodes(graph, fanout):
    nodes = {}
    for n in graph:
        neighbours = [n for n in graph.neighbors(n)]
        input = random.randint(5, 10)
        nodes[n] = nodes.FlowNode(n, neighbours, input)

    return nodes


def main():
    graph = graphGen.randomG(10, 10)  # gera grafo
    nodes = graphToNodes(graph, 1)

    loss_rate = 0
    sim = Simulator(nodes, loss_rate)  # cria classe
    starting_node = 0
    time = sim.start(starting_node, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(graph, with_labels=True)


if __name__ == "__main__":
    main()
