import networkx as nx
import random
import nodes
import builders

def addNodes(graph, numberToAdd, numberOfConnections, input, simulator, w=None,):
    n_nodes = len(graph)
    new_nodes = {}
    sim_builder = builders.SimulatorBuilder()
    sim_builder.build_with_simulator(simulator)
    #for n in graph.nodes:
     #   new_nodes[n] = graph.nodes[n]['flownode']

    for n in range(n_nodes, n_nodes + numberToAdd):
        
        connections = []
        aux_nodes = list(graph.nodes)

        if n > n_nodes:
            aux_nodes.remove(n-1)

        for i in range(numberOfConnections):
            a = random.choice(aux_nodes)
            connections.append(a)
            aux_nodes.remove(a)

        graph.add_node(n)
        new_nodes[n] =sim_builder.buildNode(n, input, connections)

        for neighbour in connections:
            print(n, neighbour)
            if w == None:
                graph.add_edge(n, neighbour, weight=random.randint(5, 200))
            else:
                graph.add_edge(n, neighbour, weight=w)
            graph.nodes[neighbour]['flownode'].addNeighbour(n)
        
    nx.set_node_attributes(graph, new_nodes, 'flownode')


def removeNodes(graph, numToRemove):
    aux_nodes = list(graph.nodes)
    removed = []

    max_iter = 25
   
    for n in range(numToRemove):
        i = 0
        while(i <= 25):
            a = random.choice(aux_nodes)

            node = graph.nodes[a]['flownode']
            #só retira folhas
            if(len(node.neighbours) == 1):
                graph.remove_node(a)
                aux_nodes.remove(a)
                removed.append(node)
                break
            i += 1
        if i <= max_iter:
            for nei in node.neighbours:
                graph.nodes[nei]['flownode'].removeNeighbour(a)
    
    return removed


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