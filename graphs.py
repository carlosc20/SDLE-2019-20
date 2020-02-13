import networkx as nx
import random
import matplotlib
import matplotlib.pyplot as plt


nodes = range(10,100,10)
edges = []

for n in nodes:
    total = 0
    r = 10
    for _ in range(r):
        G = nx.Graph()
        G.add_nodes_from(range(n))

        while list(nx.isolates(G)) != []:
            [a,b] = random.sample(set(G.nodes()), 2)
            if not G.has_edge(a,b) and a != b:
                G.add_edge(a,b)

        total += G.number_of_edges()
            
    edges.append(total/r)

    nx.draw(G, with_labels=True)
    plt.show()


plt.plot(nodes, edges)
plt.show()