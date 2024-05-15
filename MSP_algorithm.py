import sys
import itertools
import pandas as pd
import os
import matplotlib.pyplot as plt


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


def get_points_dict(file_path):
    points_dict = {}
    with open(file_path, "r") as file:
        try:
            num_of_points = int(file.readline().strip())
        except ValueError:
            print("Invalid file format")
            return None

        points_dict[0] = Points(0, 0)
        for i in range(1, num_of_points + 1):
            try:
                _, x, y = file.readline().split()
                points_dict[i] = Points(float(x), float(y))
            except ValueError:
                print("Invalid file format")
                return None

    return points_dict


def min_key(keys, mst_set):
    min_val = sys.maxsize
    min_index = -1
    for i in range(len(keys)):
        if keys[i] < min_val and mst_set[i] == False:
            min_val = keys[i]
            min_index = i
    return min_index


def prim_mst(points_dict):
    n = len(points_dict)
    parent = [-1] * n
    keys = [sys.maxsize] * n
    mst_set = [False] * n
    keys[0] = 0
    parent[0] = -1
    for _ in range(n - 1):
        u = min_key(keys, mst_set)
        mst_set[u] = True
        for v in range(n):
            if not mst_set[v] and v in points_dict:
                dist = calculate_distance(points_dict[u], points_dict[v])
                if dist < keys[v]:
                    parent[v] = u
                    keys[v] = dist

    return parent


def reconstruct_path(parent, points_dict):
    path_order = []
    for i in range(1, len(parent)):
        path_order.append((parent[i], i))
    # Add the return to the starting point (0,0)
    path_order.append((path_order[-1][1], 0))
    return path_order


def plot_tour(points, route):
    plt.figure(figsize=(10, 6))
    # Plot the points
    for point in points.values():
        plt.plot(point.x_coordinate, point.y_coordinate, "bo")
    # Draw the paths
    for i, j in route:
        plt.plot(
            [points[i].x_coordinate, points[j].x_coordinate],
            [points[i].y_coordinate, points[j].y_coordinate],
            "b-",
        )
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.title("Optimal Tour Including Return to Start")
    plt.grid(True)
    plt.show()

    # Calculate the total distance of the travel path
    total_distance = 0
    for i, j in route:
        point1 = points[i]
        point2 = points[j]
        total_distance += calculate_distance(point1, point2)

    print("Total distance of the travel path:", total_distance)


# Main function adjustment for testing
def main():
    file_path = "data/d159.dat"  # Ensure the correct file path
    points_dict = get_points_dict(file_path)
    if points_dict is None:
        return

    parent = prim_mst(points_dict)
    path_order = reconstruct_path(parent, points_dict)
    plot_tour(points_dict, path_order)


if __name__ == "__main__":
    main()


# Main function
def main():
    file_path = "data\d159.dat"
    points_dict = get_points_dict(file_path)
    if points_dict is None:
        return

    parent = prim_mst(points_dict)
    path_order = reconstruct_path(parent, points_dict)
    plot_tour(points_dict, path_order)


if __name__ == "__main__":
    main()
