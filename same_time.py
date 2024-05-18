import multiprocessing
import random
import matplotlib.pyplot as plt
from twoOpt import twoOpt
from NN_refiined import nearest_neighbour_v2, optimize_tsp_with_initial_solution
import itertools


class Points:
    def __init__(self, x_coordinate, y_coordinate):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def __str__(self):
        return f"({self.x_coordinate}, {self.y_coordinate})"


def calculate_distance(point1, point2):
    x_distance = 1.1 * abs(point1.x_coordinate - point2.x_coordinate)
    y_distance = abs(point1.y_coordinate - point2.y_coordinate)
    return max(x_distance, y_distance)


def get_distance_dict(file_path):
    global points_dict
    points_dict = {}
    points_dict[0] = Points(0, 0)
    with open(file_path, 'r') as file:
        num_of_points = int(file.readline().strip())
        for i in range(1, num_of_points + 1):
            _, x, y = file.readline().split()
            points_dict[i] = Points(float(x), float(y))

    # Generate point combinations and calculate distances
    distance_dict = {}
    for combination in itertools.permutations(points_dict.keys(), 2):
        distance_dict[combination] = calculate_distance(
            points_dict[combination[0]], points_dict[combination[1]])

    return distance_dict


# distance_dict = {(0, 1): 5, (0, 2): 10, (1, 2): 3,
# (1, 0): 5, (2, 0): 10, (2, 1): 3}
# points = [0, 1, 2]
# route, obj = solve_tsp(distance_dict, points, 5)


def plot_tour(points_dict, route, nn=False):
    plt.figure(figsize=(10, 6))

    # Plot the points
    for point in points_dict.values():
        plt.plot(point.x_coordinate, point.y_coordinate, 'bo')

    if nn:
        # Draw the paths
        for k in range(len(route)-1):
            i = route[k]
            j = route[k+1]
            plt.plot([points_dict[i].x_coordinate, points_dict[j].x_coordinate], [
                points_dict[i].y_coordinate, points_dict[j].y_coordinate], 'b-')
    else:
        for i, j in route:
            plt.plot([points_dict[i].x_coordinate, points_dict[j].x_coordinate], [
                points_dict[i].y_coordinate, points_dict[j].y_coordinate], 'b-')

    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('Optimal Tour')
    plt.grid(True)
    plt.show()


def calculate_distance(distance_dict, route, nn=False):
    total_distance = 0
    if nn:
        for k in range(len(route)-1):
            i = route[k]
            j = route[k+1]
            total_distance += distance_dict[(int(i), int(j))]
    else:
        for travel in route:
            total_distance += distance_dict[travel]

    return total_distance


def heuristic1(initial_tour, distance_dict, points):
    tour = twoOpt(initial_tour, distance_dict)
    return tour


def heuristic2(initial_tour, distance_dict, points):
    tour = optimize_tsp_with_initial_solution(
        distance_dict, points, initial_tour, 5)
    return tour


def run_heuristic(heuristic, initial_tour, distance_dict, points):
    result = heuristic(initial_tour, distance_dict, points)
    distance = calculate_distance(result)
    print(f"Result: {distance}, tour: {result}")


if __name__ == "__main__":
    # Gathering data
    distance_dict = get_distance_dict("data\d159.dat")
    points = set()
    for (i, j) in distance_dict.keys():
        points.add(i)
        points.add(j)
    initial_tour = nearest_neighbour_v2(
        distance_dict=distance_dict, points=points)

    # Creating processes
    p1 = multiprocessing.Process(target=run_heuristic, args=(
        heuristic1, initial_tour, distance_dict, points))
    p2 = multiprocessing.Process(target=run_heuristic, args=(
        heuristic2, initial_tour, distance_dict, points))

    # Starting processes
    p1.start()
    p2.start()

    # Wait for all processes to finish
    p1.join()
    p2.join()


def optimize_file(distance_dict, points):
    import time
    start_time = time.time()
    initial_tour = nearest_neighbour_v2(
        distance_dict=distance_dict, points=points)
    two_opt_tour = twoOpt(initial_tour, distance_dict)
    end_time = time.time()
    elapsed_time_seconds = end_time - start_time
    elapsed_time_minutes = elapsed_time_seconds / 60

    if elapsed_time_minutes < 5:
        optimal_tour = optimize_tsp_with_initial_solution(
            distance_dict, points, initial_tour, 5 - elapsed_time_minutes)
    else:
        optimal_tour = two_opt_tour

    return optimal_tour
