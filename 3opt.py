import itertools
import time
from all_functions import calculate_total_distance, plot_tour, get_distance_dict, nearest_neighbour_v2, twoOpt


def generate_3opt_variants(path, i, j, k):
    """
    Generate all possible 3-opt variants for the path given three breakpoints i, j, k.
    """
    a, b, c, d, e, f = path[i-1], path[i], path[j -
                                                1], path[j], path[k-1], path[k % len(path)]

    variants = [
        path[:i] + path[i:j][::-1] + path[j:k] +
        path[k:],  # Case 1: reverse (i,j)
        path[:i] + path[i:j] + path[j:k][::-1] + \
        path[k:],  # Case 2: reverse (j,k)
        # Case 3: swap (i,j) and (j,k)
        path[:i] + path[j:k] + path[i:j] + path[k:],
        # Case 4: reverse (i,j) and swap with (j,k)
        path[:i] + path[j:k] + path[i:j][::-1] + path[k:],
        path[:i] + path[i:j][::-1] + path[j:k][::-1] + \
        path[k:],  # Case 5: reverse (i,j) and (j,k)
        path[:i] + path[k-1:j-1:-1] + path[i:j][::-1] + \
        path[k:],  # Case 6: reverse (j,k) and swap with (i,j)
        path[:i] + path[k-1:j-1:-1] + path[i:j] + \
        path[k:],  # Case 7: reverse all three segments
    ]

    return variants


def improve_3opt(path, distance_dict, total=5):
    start_time = time.time()
    n = len(path)
    old_distance = calculate_total_distance(
        route=path, distance_dict=distance_dict, nn=True)
    improvement = True

    while improvement and (time.time() - start_time) < total * 60:
        improvement = False
        for (i, j, k) in itertools.combinations(range(1, n), 3):
            if k - j == 1 or j - i == 1:
                continue  # Skip adjacent indices

            variants = generate_3opt_variants(path, i, j, k)

            for variant in variants:
                new_distance = calculate_total_distance(
                    route=variant, distance_dict=distance_dict, nn=True)

                if new_distance < old_distance:
                    print(f'Improvement found: New length = {new_distance}')
                    path = variant
                    old_distance = new_distance
                    improvement = True
                    break  # Exit inner loop to restart with the new path

            if improvement:
                break  # Exit outer loop to restart with the new path

    return path


def solve_tsp_3opt(distance_dict, initial_tour, total=5):
    optimized_path = improve_3opt(initial_tour, distance_dict, total)
    return optimized_path


distance_dict_paths = {}
points_dict_dict = {}
point_set_path = {}
for filepath in [r"data\e\e3795.dat"]:
    distance_dict_paths[filepath], points_dict_dict[filepath] = get_distance_dict(
        filepath)
    points = set()
    for (i, j) in distance_dict_paths[filepath].keys():
        points.add(i)
        points.add(j)
    point_set_path[filepath] = points

distances_NN = []
distances_2opt = []
distances_3opt = []
filepaths = [r"data\e\e3795.dat"]
for filepath in filepaths:
    initial_tour = nearest_neighbour_v2(
        distance_dict=distance_dict_paths[filepath], points=point_set_path[filepath])
    distances_NN.append(calculate_total_distance(
        distance_dict_paths[filepath], initial_tour, True))
    three_opt_tour = solve_tsp_3opt(
        initial_tour=initial_tour, distance_dict=distance_dict_paths[filepath], total=2)
    plot_tour(points=points_dict_dict[filepath], route=three_opt_tour, nn=True)
    distances_3opt.append(calculate_total_distance(
        distance_dict_paths[filepath], three_opt_tour, True))
    # plot_tour(points_dict=points_dict, route=two_opt_tour, nn=True)


for i in range(len(distances_3opt)):
    print(f"File name: {filepaths[i]}")
    print(f"Distance NN: {distances_NN[i]}")
    print(f"Distance 2OPT: {distances_2opt[i]}")
    print(f"Distance 3OPT: {distances_3opt[i]}")
    print("_____________________\n")
