import networkx as nx
import random



def randomG(size = 10):
    G = nx.Graph()
    G.add_nodes_from(range(size))

    while nx.is_connected(G) == False:
        [a,b] = random.sample(set(G.nodes()), 2)
        if not G.has_edge(a,b) and a != b:
            G.add_edge(a,b, weight = random.randint(0,100)) 

    return G

def preferentialG(size = 10):
    G = nx.empty_graph(size)
    G.name="nodes: %d"%(size)

    repeated_nodes = list((G.nodes()))

    while nx.is_connected(G) == False:
        # Escolhe dois nodes aleatórios
        a = random.choice(repeated_nodes)
        b = random.choice(repeated_nodes)

        # Se forem diferentes e não existir já ligação, cria ligação
        if a != b and not G.has_edge(a,b):
            G.add_edge(a,b, weight = random.randint(0,100)) 
            # Adicionar nodes ligados
            repeated_nodes.append(a)
            repeated_nodes.append(b)
    return G