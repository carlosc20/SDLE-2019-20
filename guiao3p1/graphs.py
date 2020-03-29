import networkx as nx
import random
import matplotlib
import matplotlib.pyplot as plt

nodes = range(10,13,1)
edges = []
minEdges = []
maxEdges = []
completeEdges = []

for n in nodes:
    total = 0
    r = 10
    for _ in range(r):
        G = nx.Graph()
        G.add_nodes_from(range(n))

        while nx.is_connected(G) == False:
            [a,b] = random.sample(set(G.nodes()), 2)
            if not G.has_edge(a,b) and a != b:
                G.add_edge(a,b) 

        total += G.number_of_edges()
    
    minEdges.append(n-1)
    maxEdges.append((n-1)*(n-2)/2)
    completeEdges.append((n*(n-1))/2)
    edges.append(total/r)
    nx.draw(G, with_labels=True)
    plt.show()


plt.plot(nodes, edges, label='average')
plt.plot(nodes, minEdges, label='min')
plt.plot(nodes, maxEdges, label='max')
plt.plot(nodes, completeEdges, label='complete')
plt.legend(title='Edges:')
plt.show()