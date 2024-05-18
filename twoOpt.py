import time
import matplotlib.pyplot as plt
from gurobipy import Model, GRB, quicksum
import numpy as np
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


distance_dict = get_distance_dict("data\d\d159.dat")
points = set()
for (i, j) in distance_dict.keys():
    points.add(i)
    points.add(j)
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


def nearest_neighbour_v2(distance_dict, points):
    print("NN started")

    point_to_connections = {p: {} for p in points}
    for (p1, p2), dist in distance_dict.items():
        point_to_connections[p1][p2] = dist
        point_to_connections[p2][p1] = dist

    def find_nearest_point(point, unvisited_points):
        closest_point, min_distance = None, float('inf')
        connections = point_to_connections[point]
        for p, dist in connections.items():
            if p in unvisited_points and dist < min_distance:
                closest_point, min_distance = p, dist
        return closest_point

    tour = [0]
    unvisited_points = set(points)
    unvisited_points.remove(0)
    current_point = 0
    while unvisited_points:
        print(f"Cities left to visit: {len(unvisited_points)}")
        nearest_point = find_nearest_point(current_point, unvisited_points)
        tour.append(nearest_point)
        unvisited_points.remove(nearest_point)
        current_point = nearest_point

    tour.append(0)
    return tour


def twoOpt(tour, distance_dict):
    start_time = time.time()
    tour = tour[:-1]
    n = len(tour)
    improvement = True
    old_distance = calculate_distance(
        distance_dict=distance_dict, route=tour, nn=True)
    while improvement:
        improvement = False
        for i in range(1, n-1):
            if time.time() - start_time > 300:  # 300 seconds = 5 minutes
                print("Time exceeded 5 minutes")
                return tour

            for j in range(i+1, n):
                new_tour = tour[0:i] + tour[i:j + 1][::-1] + tour[j + 1:n]
                new_distance = calculate_distance(
                    distance_dict=distance_dict, route=new_tour, nn=True)
                if new_distance < old_distance:
                    print("Improvement found: New length =", new_distance)
                    tour = new_tour
                    improvement = True
                    break

            if improvement:
                old_distance = new_distance
                print("Improvement made in inner loop, returning to the outer loop.")
                break
    tour.append(0)
    return tour


initial_tour = nearest_neighbour_v2(distance_dict=distance_dict, points=points)
two_opt_tour = twoOpt(tour=initial_tour, distance_dict=distance_dict)

plot_tour(points_dict=points_dict, route=two_opt_tour, nn=True)
