import itertools
import time
from all_functions import calculate_total_distance, plot_tour, get_distance_dict, nearest_neighbour_v2, twoOpt




def swap_3opt(path, i, j, k):
    new_path = path[:i] + path[i:j][::-1] + path[j:k][::-1] + path[k:]
    return new_path

def improve_3opt(path, distance_dict, total=5):
    start_time = time.time()
    n = len(path)
    improvement = True
    old_distance = calculate_total_distance(route=path, distance_dict=distance_dict, nn=True)
    while improvement:
        improvement = False
        for (i, j, k) in itertools.combinations(range(1, n), 3):  
            if time.time() - start_time > total * 60:
                print(f'Time exceed ' + str(total) + 'minutes')
                return path
                # Ensure valid range for TSP
            if k - i == 1: continue  # Skip adjacent indices
            new_path = swap_3opt(path, i, j, k)
            new_distance = calculate_total_distance(route=new_path, distance_dict=distance_dict, nn=True)
            if new_distance < old_distance:
                print(f'Improvement found: New length =', new_distance)
                path = new_path
                old_distance = new_distance
                improvement = True
    return path

def solve_tsp_3opt(distance_dict, initial_tour, total = 5):
    # Initial path (e.g., simple 0-1-2-...-n-0)
    cities = list(set([key[0] for key in distance_dict.keys()]))
    path = initial_tour  # Ensure starting and ending at city 0
    optimized_path = improve_3opt(path, distance_dict, total)
    return optimized_path




distance_dict_paths = {}
point_set_path = {}
for filepath in [r"data\d\d159.dat", r"data\b\b493.dat", r"data\e\e1400.dat", r"data\a\a2152.dat", r"data\d2319.dat", r"data\e\e3795.dat"]:
    distance_dict_paths[filepath] = get_distance_dict(filepath)[0]

    points = set()
    for (i, j) in distance_dict_paths[filepath].keys():
        points.add(i)
        points.add(j)
    point_set_path[filepath] = points

distances_NN = []
distances_2opt = []
distances_3opt = []
filepaths = [r"data\d\d159.dat", r"data\b\b493.dat", r"data\e\e1400.dat", r"data\a\a2152.dat", r"data\d2319.dat", r"data\e\e3795.dat"]
for filepath in filepaths:
    initial_tour = nearest_neighbour_v2(
        distance_dict=distance_dict_paths[filepath], points=point_set_path[filepath])
    distances_NN.append(calculate_total_distance(
            distance_dict_paths[filepath], initial_tour, True))
    
    two_opt_tour = twoOpt(tour=initial_tour, distance_dict=distance_dict_paths[filepath], total=10)
    distances_2opt.append(calculate_total_distance(
            distance_dict_paths[filepath], two_opt_tour, True))

    three_opt_tour = solve_tsp_3opt(
        initial_tour=initial_tour, distance_dict=distance_dict_paths[filepath], total=10)
    distances_3opt.append(calculate_total_distance(
        distance_dict_paths[filepath], three_opt_tour, True))
    # plot_tour(points_dict=points_dict, route=two_opt_tour, nn=True)


for i in range(len(distances_3opt)):
    print(f"File name: {filepaths[i]}")
    print(f"Distance NN: {distances_NN[i]}")
    print(f"Distance 2OPT: {distances_2opt[i]}")
    print(f"Distance 3OPT: {distances_3opt[i]}")
    print("_____________________\n")
