import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import nodes
import random

# TODO: Fazer mudanças de ligações no grafo em runtime


class Simulator:

    def __init__(self, nodes, loss_rate):
        self.loss_rate = loss_rate # 0 a 1 corresponde á probabilidade de perda de uma mensagem
        self.nodes = nodes # dict: nr -> Node
        self.current_time = 0
        self.pending = [] # [(delay, Message]



    def start(self):
        # primeira ronda de mensagens
        for n in self.nodes:
            messages = n.generate_messages()
            self.pending.append(messages)

        # run the simulation loop
        return self.run_loop()



    def run_loop(self):
        while len(self.pending) > 0:

            # evento com menor delay, delay necessario?
            messages, time = self._next_messages()
            self.current_time = time
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

            new = []  
            for dst, msgs in group.items():
                node = self.nodes[dst]
                gen = node.handle_messages(msgs)
                new.append(gen)


            # TODO: por delay nos events
            self.pending.append(new)
            self.pendingPrint()

        return self.current_time

    # vai buscar e remove do pending as mensagens com menor delay
    # devolve lista de mensagens e delay
    def _next_messages(self):
        time = sys.maxsize
        messages = []
        for m in self.pending:

            if m[0] < time:
                messages = []
                time = m[0]

            if m[0] == time:
                messages.append(m[1])
        
        for m in messages:
            self.pending.remove(m)

        return messages, time


    # TODO antigo, remover se não for preciso:
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
