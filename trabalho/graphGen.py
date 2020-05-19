import networkx as nx
import random
import nodes

def addNodes(graph, numberToAdd, numberOfConnections, input, w=None):
    n_nodes = len(self.graph)
    new_nodes = {}
    aux_nodes = graph.nodes.copy()
    for n in range(n_nodes + 1, n_nodes + numberToAdd + 1):

        connections = []
        for i in range(numberOfConnections + 1):
            a = random.choice(aux_nodes)
            connections.append(a)
            aux_nodes.remove(a)

        graph.add_node(n)
        new_nodes[n] = nodes.FlowNode(n, connections, input)
        for neighbour in connections:
            if w == None:
                graph.add_edge(n, neighbor, weight=random.randint(5, 200))
            else:
                graph.add_edge(n, neighbor, weight=w)

    nx.set_node_attributes(graph, g_nodes, 'flownode')
    return graph, new_nodes


def removeNodes(graph, numToRemove):
    aux_nodes = graph.nodes.copy()
    removed = []
    for n in range(numToRemove + 1):
        a = random.choice(aux_nodes)
        removed.append(graph.nodes[a]['flownode'])
        graph.remove_node(n)
        aux_nodes.remove(n)
        
    
    return graph, removed


# Cuidado com o max_degree, especialmente quando é baixo. Devido à aleatoriedade podemos nunca chegar a um grafo conectado.  
# Exemplo: max_degree = 2 -> Se não se formar apenas um grafo linear em que alguns nodos só tem um vértice entramos em ciclo infinito,
# porque uma parcela de nodos vai ficar isolada.
# max_degre >= 3 apresenta bons resultados.

def randomG(size=10, max_degree=3, w=None):
    G = nx.Graph()
    G.add_nodes_from(range(size))
    nodes_degree = dict.fromkeys(range(size), 0)
    
    while not nx.is_connected(G):
        a = random.choice(list(nodes_degree.keys()))
        neighbour_found = False
        if nodes_degree[a] < max_degree:
            while(not neighbour_found):
                b = random.choice(list(nodes_degree.keys()))
                if not G.has_edge(a, b) and a != b and nodes_degree[b] < max_degree:
                    if w == None:
                        r = random.randint(5, 150)
                        G.add_edge(a, b, weight=r)
                        print(a, " -> ", b, " weight: ", r)

                    else:
                        G.add_edge(a, b, weight=w)
                    nodes_degree[a] += 1
                    nodes_degree[b] += 1
                    if nodes_degree[a] == max_degree:
                        del nodes_degree[a]
                    if nodes_degree[b] == max_degree:
                        del nodes_degree[b]
                    neighbour_found = True
    return G


def preferentialG(size=10, w=None):
    G = nx.empty_graph(size)
    G.name="nodes: %d"%(size)

    repeated_nodes = list((G.nodes()))

    while not nx.is_connected(G):
        # Escolhe dois nodes aleatórios
        a = random.choice(repeated_nodes)
        b = random.choice(repeated_nodes)

        # Se forem diferentes e não existir já ligação, cria ligação
        if a != b and not G.has_edge(a, b):
            if w == None:
                G.add_edge(a, b, weight=random.randint(0, 20))
            else:
                G.add_edge(a, b, weight=w)
            # Adicionar nodes ligados
            repeated_nodes.append(a)
            repeated_nodes.append(b)
    return G