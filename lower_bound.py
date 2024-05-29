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




distance_dict_paths = {}
point_set_path = {}
for filepath in [r"data\d\d159.dat", r"data\b\b493.dat", r"data\e\e1400.dat", r"data\a\a2152.dat", r"data\d2319.dat", r"data\e\e3795.dat"]:
    distance_dict_paths[filepath] = get_distance_dict(filepath)[0]

    points = set()
    for (i, j) in distance_dict_paths[filepath].keys():
        points.add(i)
        points.add(j)
    point_set_path[filepath] = points

distances = []
filepaths = [r"data\d\d159.dat", r"data\b\b493.dat", r"data\e\e1400.dat",
             r"data\a\a2152.dat", r"data\d2319.dat", r"data\e\e3795.dat"]
for filepath in filepaths:
    initial_tour = one_tree_lower_bound(
        distance_dict=distance_dict_paths[filepath], start_city=0)
    distances.append(initial_tour)
    # plot_tour(points_dict=points_dict, route=two_opt_tour, nn=True)


for i in range(len(distances)):
    print(f"File name: {filepaths[i]}")
    print(f"Distance: {distances[i]}")
    print("_____________________\n")
