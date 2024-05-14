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
