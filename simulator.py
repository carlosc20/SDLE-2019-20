import sys

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
            print("visited!", self.neighbours)
            for i in self.neighbours:
                res.append((i, "ola")) 
            self.visited = True
        return res


def connector(graph):
    nodes = {}
    distances = {}
    for n in graph:
        edges = [e for e in graph.edges(n)]
        #print("edg ", edges)
        neighbours = [n for n in graph.neighbors(n)]
        #print("nei ", neighbours)
        nodes[n] = Node(neighbours)
        for e in edges:
            distances[e] = graph.get_edge_data(e[0], e[1])['weight']
    #print(distances)
    return nodes, distances
        
              
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
        self.run_loop()

    def run_loop(self):
        while len(self.pending) > 0:
            # - find in 'self.pending' the next message that should be delivered
            tmp_future_time = sys.maxsize
            for i in range(len(self.pending)):
                tmp_sum = self.current_time + self.pending[i][0]
                if(tmp_sum < tmp_future_time):
                    index = i
                    tmp_future_time = tmp_sum
            # - handle such message in its destination
            info = self.pending[index][1]
            src, dst, msg = info[0], info[1], info[2] 
            res = self.nodes[dst].handle(src, msg)
            del self.pending[index]
            # - nodo não foi visitado
            if(len(res) > 0):
                for r in res:
                    # > set the delay according to 'self.distances'
                    tmp_delay = self.distances[(dst, r[0])]
                    messages_to_neighbours = (tmp_delay, (i, r[0], r[1]))
                    # - schedule new messages
                    self.pending.append(messages_to_neighbours)
                    
                # - update 'self.current_time'
                self.current_time += self.pending[index][0]
        print("finished!")
