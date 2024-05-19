from all_functions import nearest_neighbour_v2
import time
import itertools
import matplotlib.pyplot as plt
import numpy as np


class Points:
    def __init__(self, x_coordinate, y_coordinate):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate

    def __str__(self):
        return f"({self.x_coordinate}, {self.y_coordinate})"


def calculate_distance(point1, point2):
    x_distance = abs(point1.x_coordinate - point2.x_coordinate)
    y_distance = abs(point1.y_coordinate - point2.y_coordinate)
    return max(x_distance, y_distance)


def get_distance_dict(file_path):
    global points_dict
    points_dict = {}
    points_dict[0] = Points(0, 0)
    with open(file_path, "r") as file:
        num_of_points = int(file.readline().strip())
        for i in range(1, num_of_points + 1):
            _, x, y = file.readline().split()
            points_dict[i] = Points(float(x), float(y))

    # Generate point combinations and calculate distances
    distance_dict = {}
    for combination in itertools.permutations(points_dict.keys(), 2):
        distance_dict[combination] = calculate_distance(
            points_dict[combination[0]], points_dict[combination[1]]
        )

    return distance_dict, points_dict


def calculate_total_distance(route, distance_dict):
    total_distance = 0
    for k in range(len(route) - 1):
        i = route[k]
        j = route[k + 1]
        total_distance += distance_dict[(int(i), int(j))]
    return total_distance


def lin_kernighan(initial_tour, distance_dict, p1=5, p2=2):
    tour = initial_tour[:-1]  # Initial tour
    best_distance = calculate_total_distance(tour, distance_dict)
    start_time = time.time()

    def generate_neighbors(t):
        neighbors = []
        for i in range(1, len(t) - 1):
            for j in range(i + 1, len(t)):
                neighbor = t[:]
                neighbor[i: j + 1] = reversed(t[i: j + 1])
                neighbors.append(neighbor)
        return neighbors

    improved = True
    while improved:
        improved = False
        for k in range(1, p1 + 1):
            for t_prime in generate_neighbors(tour):
                t_prime_distance = calculate_total_distance(
                    t_prime, distance_dict)
                if t_prime_distance < best_distance:
                    tour = t_prime
                    best_distance = t_prime_distance
                    improved = True
                    break
            if improved:
                break
    tour.append(0)
    return tour


def plot_tour(tour, points_dict):
    x_coords = [points_dict[point].x_coordinate for point in tour]
    y_coords = [points_dict[point].y_coordinate for point in tour]
    x_coords.append(points_dict[tour[0]].x_coordinate)
    y_coords.append(points_dict[tour[0]].y_coordinate)

    plt.figure(figsize=(10, 10))
    plt.plot(x_coords, y_coords, marker="o")
    plt.title("Lin-Kernighan TSP Solution")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()


def main():
    file_path = "data/d/d159.dat"
    distance_dict, points_dict = get_distance_dict(file_path)
    points = set()
    for i, j in distance_dict.keys():
        points.add(i)
        points.add(j)
    if points_dict is None or distance_dict is None:
        print("Error in reading data.")
        return
    initial_tour = nearest_neighbour_v2(distance_dict, points)
    tour = lin_kernighan(
        initial_tour, distance_dict)
    print(f"Best tour: {tour}")
    print(f"Total distance: {calculate_total_distance(tour, distance_dict)}")

    plot_tour(tour, points_dict)


if __name__ == "__main__":
    main()
