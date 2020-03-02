class Node:
    # - neigbours: [1,2,...]
    def _init_(self, neighbours):
        self.neighbours = neighbours
    #handle 'msg' by process 'src' at time 't'
    #várias implementações dependendo do algoritmo
    def handle(self, src, msg, t):
        # returns e.g. [(dst0, msg0), (dst1, msg1), ....]
        res = []
        for i in self.neigbours:
            res.append((i, "ola"))  
        return res

class Sim:
    # - nodes: {0: Node, 1: Node, 2: Node}
    # - distances: {(0,1): 103, (0,2): 40, ...}
    def _init_(self, nodes, distances):
        self.nodes = nodes
        self.distances = distances
        self.current_time = 0
        self.pending = [] # [(delay, (src, dst, msg))]

    def start(self, initial_msg):
        # schedule first event
        for i in self.nodes:
            event = (0, (None, i, initial_msg))
            self.pending.append(event)

        # run the simulation loop
        self.run_loop()

    def run_loop(self):
        while len(self.pending) > 0:
            #TODO
            # - find in 'self.pending' the next message that should be delivered
            # - handle such message in its destination
            # - schedule new messages (if any)
            # > set the delay according to 'self.distances'
            # - update 'self.current_time'

