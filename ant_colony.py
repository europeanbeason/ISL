import timeit
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
    global num_of_points
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


def initialize_pheromones(city_pairs, initial_pheromone):
    pheromones = {pair: initial_pheromone for pair in city_pairs}
    return pheromones


def probability_to_move(pheromones, distances, alpha, beta, current_city, visited):
    probabilities = {}
    total_prob = 0
    for (from_city, to_city), dist in distances.items():
        if from_city == current_city and to_city not in visited:
            pheromone = pheromones[(from_city, to_city)] ** alpha
            attractiveness = (1.0 / dist) ** beta
            prob = pheromone * attractiveness
            probabilities[to_city] = prob
            total_prob += prob

    probabilities = {city: prob / total_prob if total_prob >
                     0 else 0 for city, prob in probabilities.items()}
    return probabilities


def construct_tours(num_ants, city_list, pheromones, distances, alpha, beta, start_city):
    tours = []
    for ant in range(num_ants):
        tour = [start_city]
        visited = set(tour)

        while len(tour) < len(city_list):
            current_city = tour[-1]
            probabilities = probability_to_move(
                pheromones, distances, alpha, beta, current_city, visited)
            if probabilities:
                next_city = np.random.choice(
                    list(probabilities.keys()), p=list(probabilities.values()))
                tour.append(next_city)
                visited.add(next_city)
            else:
                # Break if no unvisited cities are reachable (unlikely in a fully connected graph)
                break

        tours.append(tour)
    return tours


def update_pheromones(pheromones, tours, distances, evaporation_rate):
    for tour in tours:
        tour_length = sum(distances[(tour[i], tour[i+1])]
                          for i in range(len(tour) - 1))
        for i in range(len(tour) - 1):
            pheromones[(tour[i], tour[i+1])] += 1.0 / tour_length
            # For undirected graph
            pheromones[(tour[i+1], tour[i])] = pheromones[(tour[i], tour[i+1])]
    pheromones = {k: v * (1 - evaporation_rate) for k, v in pheromones.items()}


def ant_colony_optimization(city_list, distances, num_ants, alpha, beta, evaporation_rate, initial_pheromone, iterations, start_city):
    pheromones = initialize_pheromones(distances.keys(), initial_pheromone)

    best_tour = None
    best_length = float('inf')
    i = 0
    for _ in range(iterations):
        print(f"Itermation: {i}")
        i += 1
        tours = construct_tours(num_ants, city_list,
                                pheromones, distances, alpha, beta, start_city)
        update_pheromones(pheromones, tours, distances, evaporation_rate)

        for tour in tours:
            if len(tour) == len(city_list):  # Ensure complete tours are evaluated
                tour_length = sum(distances[(tour[i], tour[i+1])]
                                  for i in range(len(tour) - 1))
                if tour_length < best_length:
                    best_tour = tour
                    best_length = tour_length

    return best_tour, best_length


distance_dict = get_distance_dict("data\d159.dat")
points = list(range(0, num_of_points+1))


# Parameters
num_ants = 5
alpha = 1.0  # Influence of pheromone
beta = 2.0   # Influence of heuristic information (inverse of distance)
evaporation_rate = 0.5
initial_pheromone = 0.1
iterations = 20

best_tour, best_length = ant_colony_optimization(
    points, distance_dict, num_ants, alpha, beta, evaporation_rate, initial_pheromone, iterations, 0)

best_tour.append(0)


def calculate_distance(distance_dict, route, nn=False):
    total_distance = 0
    if nn:
        for k in range(len(route)-1):
            i = route[k]
            j = route[k+1]
            total_distance += distance_dict[(int(i), int(j))]
    else:
        for travel in route[0]:
            total_distance += distance_dict[travel]

    return total_distance


def plot_tour(points, route, nn=False):
    plt.figure(figsize=(10, 6))

    # Plot the points
    for point in points.values():
        plt.plot(point.x_coordinate, point.y_coordinate, 'bo')

    if nn:
        # Draw the paths
        for k in range(len(route)-1):
            i = route[k]
            j = route[k+1]
            plt.plot([points[i].x_coordinate, points[j].x_coordinate], [
                points[i].y_coordinate, points[j].y_coordinate], 'b-')
    else:
        for i, j in route[0]:
            plt.plot([points[i].x_coordinate, points[j].x_coordinate], [
                points[i].y_coordinate, points[j].y_coordinate], 'b-')

    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('Optimal Tour')
    plt.grid(True)
    plt.show()


print(best_tour)
print(calculate_distance(distance_dict, best_tour, True))
plot_tour(points_dict, best_tour, True)
