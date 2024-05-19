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
        for i, j in route:
            plt.plot([points[i].x_coordinate, points[j].x_coordinate], [
                points[i].y_coordinate, points[j].y_coordinate], 'b-')

    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.title('Optimal Tour')
    plt.grid(True)
    plt.show()


# plot_tour(points_dict, route)

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


def calculate_total_distance(distance_dict, route, nn=False):
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


def load_initial_solution(model, initial_tour, vars, u):
    # Reset the start attribute for all variables to 0
    for var in vars.values():
        var.start = 0

    # Set the start attribute to 1 for edges in the initial tour
    tour_edges = zip(initial_tour[:-1], initial_tour[1:])
    for i, j in tour_edges:
        if (i, j) in vars:
            vars[i, j].start = 1

    # Initialize subtour elimination variables based on the order in the tour
    # Exclude the return to the start
    for index, city in enumerate(initial_tour[:-1]):
        u[city].start = index + 1  # Position in the tour, starting from 1


def optimize_tsp_with_initial_solution(distance_dict, points, initial_tour, time):
    model = Model("TSP")

    # Decision variables: x[i, j] is 1 if the path is part of the route, else 0
    vars = {}
    for (i, j) in distance_dict.keys():
        vars[i, j] = model.addVar(
            obj=distance_dict[i, j], vtype=GRB.BINARY, name=f"x_{i}_{j}")

    # Subtour elimination variables: u[i] is the position of point i in the tour
    u = model.addVars(points, vtype=GRB.CONTINUOUS, name='u')

    # Constraints: Each city must be entered and left exactly once
    for i in points:
        model.addConstr(quicksum(vars[i, j] for j in points if (
            i, j) in vars) == 1, name=f"enter_{i}")
        model.addConstr(quicksum(vars[j, i] for j in points if (
            j, i) in vars) == 1, name=f"leave_{i}")

    # Subtour elimination constraints (skip for the start city 0)
    for i in points:
        for j in points:
            if i != j and (i != 0 and j != 0) and (i, j) in vars:
                model.addConstr(u[i] - u[j] + len(points) * vars[i, j]
                                <= len(points) - 1, name=f"subtour_{i}_{j}")

    # Constraint for point 0 to start and end the tour
    model.addConstr(quicksum(vars[0, j] for j in points if (
        0, j) in vars) == 1, name="leave_0")
    model.addConstr(quicksum(vars[i, 0] for i in points if (
        i, 0) in vars) == 1, name="enter_0")

    # Load initial solution
    print("Initial solution loaded...")
    load_initial_solution(model, initial_tour, vars, u)

    # Set the model to focus on finding a feasible solution quickly
    model.Params.timeLimit = time * 60
    model.setParam('MIPFocus', 1)

    # Optimize the model
    model.optimize()

    if model.SolCount > 0:
        # A feasible solution is available
        mip_gap = model.MIPGap
        print(f"The solution is within {mip_gap:.2%} of the optimal value.")
        solution = model.getAttr('X', vars)
        route = [(i, j) for i, j in solution if solution[i, j] > 0.5]
        objective_value = model.ObjVal
        return route, objective_value
    else:
        # Handle cases where no feasible solution is found
        if model.status == GRB.TIME_LIMIT:
            print("No feasible solution found within the time limit.")
        else:
            print("Optimization was unsuccessful. Status code:", model.status)
        return None


# initial_tour = nearest_neighbour_v2(distance_dict, points)
opt = [(0, 1), (1, 159), (2, 4), (3, 2), (4, 156), (5, 154), (6, 5), (7, 152), (8, 7), (9, 8), (10, 9), (11, 10), (12, 13), (13, 14), (14, 15), (15, 17), (16, 143), (17, 16), (18, 63), (19, 18), (20, 19), (21, 20), (22, 21), (23, 22), (24, 23), (25, 24), (26, 25), (27, 26), (28, 27), (29, 28), (30, 29), (31, 30), (32, 31), (33, 35), (34, 33), (35, 32), (36, 37), (37, 34), (38, 36), (39, 40), (40, 121), (41, 39), (42, 41), (43, 42), (44, 43), (45, 44), (46, 45), (47, 46), (48, 91), (49, 47), (50, 49), (51, 50), (52, 51), (53, 52), (54, 53), (55, 54), (56, 55), (57, 56), (58, 57), (59, 58), (60, 59), (61, 60), (62, 61), (63, 0), (64, 62), (65, 64), (66, 65), (67, 66), (68, 67), (69, 68), (70, 69), (71, 70), (72, 71), (73, 72), (74, 75), (75, 86), (76, 74), (77, 76), (78, 73), (79, 78), (80, 79), (81, 80), (82, 81), (83, 82), (84, 83), (85, 84),
       (86, 97), (87, 85), (88, 96), (89, 88), (90, 94), (91, 77), (92, 90), (93, 92), (94, 89), (95, 87), (96, 95), (97, 98), (98, 99), (99, 100), (100, 101), (101, 102), (102, 103), (103, 104), (104, 105), (105, 106), (106, 107), (107, 118), (108, 93), (109, 108), (110, 109), (111, 110), (112, 111), (113, 112), (114, 122), (115, 114), (116, 115), (117, 116), (118, 117), (119, 48), (120, 119), (121, 120), (122, 123), (123, 135), (124, 113), (125, 124), (126, 127), (127, 128), (128, 129), (129, 130), (130, 131), (131, 132), (132, 134), (133, 138), (134, 133), (135, 136), (136, 38), (137, 139), (138, 137), (139, 140), (140, 141), (141, 142), (142, 12), (143, 144), (144, 145), (145, 146), (146, 147), (147, 148), (148, 150), (149, 11), (150, 149), (151, 155), (152, 153), (153, 6), (154, 151), (155, 125), (156, 157), (157, 158), (158, 126), (159, 3)]
print(opt)
plot_tour(points=points_dict, route=opt, nn=False)


tuples_dict = {t[0]: t for t in opt}

# Initialize the sorted list starting with the tuple that starts with 0
tuple_sorted = [tuples_dict[0]]

# Build the sorted list
i = 0
current = tuples_dict[0][1]
while current in tuples_dict:
    tuple_sorted.append(tuples_dict[current])
    current = tuples_dict[current][1]
    if current == 0 and i != 0:
        break
    i += 1
# Print the sorted list
print(tuple_sorted)
plot_tour(points=points_dict, route=tuple_sorted, nn=False)

route_nn = [travel[0] for travel in tuple_sorted]
plot_tour(points=points_dict, route=route_nn, nn=True)
