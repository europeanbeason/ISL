from all_functions import get_distance_dict
import networkx as nx
import itertools


def create_graph(distance_dict):
    G = nx.Graph()
    for (city1, city2), dist in distance_dict.items():
        G.add_edge(city1, city2, weight=dist)
    return G


def one_tree_lower_bound(distance_dict, start_city='A'):
    # Create graph from distance dictionary
    G = create_graph(distance_dict)

    # Remove the start city from the graph
    G.remove_node(start_city)

    # Compute MST on the remaining graph
    mst = nx.minimum_spanning_tree(G, weight='weight')

    # Sum the weights of the MST
    mst_cost = sum(data['weight'] for _, _, data in mst.edges(data=True))

    # Reconnect the start city by finding the two shortest edges connecting it to the MST
    shortest_edges = []
    for node in G.nodes():
        edge_weight = distance_dict.get((start_city, node), float('inf'))
        shortest_edges.append(edge_weight)

    shortest_edges.sort()

    # Add the two shortest edges to the MST cost
    if len(shortest_edges) < 2:
        raise ValueError("Not enough edges to form a 1-tree.")

    one_tree_cost = mst_cost + shortest_edges[0] + shortest_edges[1]

    return one_tree_cost


# Example usage
distance_dict, points_dict = get_distance_dict("data\d2319.dat")

print(one_tree_lower_bound(distance_dict, start_city=0))
