import sys
import networkx as nx
import matplotlib.pyplot as plt
import graphGen
import simulator

class Node:
    # - neigbours: [1,2,...]
    def __init__(self, neighbours):
        self.neighbours = neighbours
        # problema -> muitas adições à queue, mas não sei se vão fazer falta
        self.visited = False
    #várias implementações dependendo do algoritmo
    # returns e.g. [(dst0, msg0), (dst1, msg1), ....]
    def handle(self, src, msg):
        res = []
        if(self.visited == False):
            # print("visited!", self.neighbours)
            for i in self.neighbours:
                res.append((i, "ola")) 
            self.visited = True
        return res

         
class Sim:
    # - nodes: {0: Node, 1: Node, 2: Node}
    # - distances: {(0,1): 103, (0,2): 40, ...}
    def __init__(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [(delay, (src, dst, msg))]

    def start(self, starting_node, initial_msg):
        # schedule first event
        # for i in self.nodes: -> não sei se passei mal ou o stor queria isto
        
        event = (0, (None, starting_node, initial_msg))
        self.pending.append(event)

        # run the simulation loop
        return self.run_loop()

    def run_loop(self):
        while len(self.pending) > 0:
            # - find in 'self.pending' the next message that should be delivered
            tmp_future_time = sys.maxsize
            for i in range(len(self.pending)):
                if(self.pending[i][0] <= tmp_future_time):
                    index = i
                    tmp_future_time = self.pending[i][0]
            # - handle such message in its destination
            info = self.pending[index][1]
            src, dst, msg = info[0], info[1], info[2] 
            res = self.nodes[dst].handle(src, msg)
            self.current_time = self.pending[0][0]
            del self.pending[index]
            # - nodo não foi visitado
            if(len(res) > 0):
                for r in res:
                    # > set the delay according to 'self.distances'
                    tmp_delay = self.distances[(dst, r[0])]
                    messages_to_neighbours = (self.current_time + tmp_delay, (dst, r[0], r[1]))
                    # - schedule new messages
                    self.pending.append(messages_to_neighbours)
                    
                print(self.pending)
                # - update 'self.current_time'
                print("c_time: ", self.current_time)
                
        return self.current_time


class Broadcast(Node):
    def __init__(self, neighbors, fanout):
        self.neighbours = neighbours
        self.visited = False
        self.fanout = fanout

    def handle(self, src, msg):
        res = []
        if(self.visited == False):
            n = self.neighbours.len
            if(n == 0):
                for i in self.neighbours:
                    res.append((i, "broadcast"))
            else:
                for i in self.neighbours[:self.fanout]:
                    res.append((i, "fanout" + self.fanout))
            self.visited = True
        return res

#dado um grafo G simula N tentativas com N random raizes e calcula Min, Media, Max.
# testar com vários tipos de grafos 
# def analysis():


def connector(graph, type = 'normal'):
    nodes = {}
    distances = {}
    for n in graph:
        edges = [e for e in graph.edges(n)]
        #print("edg ", edges)
        neighbours = [n for n in graph.neighbors(n)]
        #print("nei ", neighbours)
        if (type == 'normal'):
            nodes[n] = Node(neighbours)
        elif (type == 'broadcast'):
            nodes[n] = Broadcast(neighbours)
        for e in edges:
            distances[e] = graph.get_edge_data(e[0], e[1])['weight']
    #print(distances)
    return nodes, distances


def main():
    G = graphGen.randomG(10, 10) # gera grafo
    nodes, distances = simulator.connector(G) # converte grafo gerado em input para simulador
    sim = simulator.Sim(nodes, distances) # cria classe
    time = sim.start(0, "diz olá")  # primeira msg/inicio
    print("finished with: ", time)
    nx.draw(G, with_labels=True)

if __name__ == "__main__":
    main()
