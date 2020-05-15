import networkx as nx
import random


def randomG(size=10, max_degree=3, w=None):
    G = nx.Graph()
    G.add_nodes_from(range(size))
    nodes_degree = dict.fromkeys(range(size), 0)

    while not nx.is_connected(G):
        [a,b] = random.sample(set(G.nodes()), 2)
        inside_max_degree = nodes_degree[a] < max_degree and nodes_degree[b] < max_degree
        if not G.has_edge(a, b) and a != b and inside_max_degree:
            if w == None:
                G.add_edge(a, b, weight=random.randint(0, 20))
            else:
                G.add_edge(a, b, weight=w)
            nodes[a] += 1
            nodes[b] += 1
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