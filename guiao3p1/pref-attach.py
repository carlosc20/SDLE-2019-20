import networkx as nx
import random
import matplotlib
import matplotlib.pyplot as plt
import collections

node_range = [50]#range(10,100,10)
edges = []
minEdges = []
maxEdges = []
completeEdges = []
degree_sequence = []

for n in node_range:
    total = 0
    r = 1
    for _ in range(r):
        G = nx.empty_graph(n)
        G.name="nodes: %d"%(n)

        #nodes = list(G.nodes())
        #sum_degree = sum([d+1 for n, d in G.degree()])

        repeated_nodes = list((G.nodes()))

        while nx.is_connected(G) == False:
            # Escolhe dois nodes aleatórios
            a = random.choice(repeated_nodes)
            b = random.choice(repeated_nodes)
            
            # Se forem diferentes e não existir já ligação, cria ligação
            if a != b and not G.has_edge(a,b):
                G.add_edge(a,b) 
                # Adicionar nodes ligados
                repeated_nodes.append(a)
                repeated_nodes.append(b)

        degree_sequence = degree_sequence + [d for n, d in G.degree()]
        total += G.number_of_edges()
    
    degreeCount = collections.Counter(sorted(degree_sequence))
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)

    # draw graph in inset
    plt.axes([0.4, 0.4, 0.5, 0.5])
    Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
    pos = nx.spring_layout(G)
    plt.axis('off')
    nx.draw_networkx_nodes(G, pos, node_size=20)
    nx.draw_networkx_edges(G, pos, alpha=0.4)

    plt.show()


    #minEdges.append(n-1)
    #maxEdges.append((n-1)*(n-2)/2)
    #completeEdges.append((n*(n-1))/2)
    #edges.append(total/r)
    #nx.draw(G, with_labels=True)
    #plt.show()


plt.plot(node_range, edges, label='average')
plt.plot(node_range, minEdges, label='min')
plt.plot(node_range, maxEdges, label='max')
plt.plot(node_range, completeEdges, label='complete')
plt.legend(title='Edges:')
plt.show()