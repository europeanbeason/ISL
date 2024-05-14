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

def min_key(keys, mst_set):
    min_val = sys.maxsize
    min_index = -1
    for i in range(len(keys)):
        if keys[i] < min_val and mst_set[i] == False:
            min_val = keys[i]
            min_index = i
    return min_index
#prims algorithm for Minimum Spanning Tree (MST)
def prim_mst(points_list):
    n = len(points_list)
    parent = [-1] * n
    keys = [sys.maxsize] * n
    mst_set = [False] * n
    
    keys[0] = 0
    parent[0] = -1
    
    for _ in range(n-1):
        u = min_key(keys, mst_set)
        mst_set[u] = True
        for v in range(n):
            if not mst_set[v]:
                dist = calculate_distance(points_list[u], points_list[v])
                if dist < keys[v]:
                    parent[v] = u
                    keys[v] = dist
    
    return parent

path = r"C:\Users\Tiziano\Documents\Tilburg\Second year\ISL\data\\"
dir_list = os.listdir(path)
u = 0
dfs = {}  # Dictionary to store DataFrames

for file in dir_list:
    u += 1
    dft = pd.read_csv(path + file)
    dft = dft[dft.columns[0]].str.split(" ", expand=True)
    dft = dft.rename(columns={1: "x_new", 2: "y"})
    dft = dft.drop(columns=0)
    dft = dft.dropna()
    if not ((dft["x_new"] == "0") & (dft["y"] == "0")).any():
        dft = dft.append({"x_new": "0", "y": "0"}, ignore_index=True)
    dfs["df" + str(u)] = dft

a = dfs["df7"]
a["x_new"] = a["x_new"].astype(float)
a["y"] = a["y"].astype(float)

a["y"] = pd.to_numeric(a["y"])
a.sort_values(by=["x_new", "y"])

# Convert DataFrame rows to Points objects
points_list = [Points(row['x_new'], row['y']) for _, row in a.iterrows()]

parent = prim_mst(points_list)

# Reconstruct the path
path_order = []
for i in range(1, len(parent)):
    path_order.append(parent[i])
path_order.append(0)  # Adding the starting point

print("Exact order of points to be traveled:")
for i in range(len(path_order) - 1):
    print(f"From {path_order[i]} to {path_order[i + 1]}")

# Assuming 'path_order' contains the order of points to be traveled
travel_df = pd.DataFrame(columns=['x_new', 'y'])

# Add the point (0, 0) at the beginning and end of the path
travel_df = travel_df.append({"x_new": 0, "y": 0}, ignore_index=True)

# Add points to the DataFrame based on the order
for i in path_order:
    travel_df = travel_df.append(a.iloc[i])

# Add the point (0, 0) at the end of the path
travel_df = travel_df.append({"x_new": 0, "y": 0}, ignore_index=True)

# Plot the travel path
plt.figure(figsize=(8, 6))
plt.plot(travel_df['x_new'], travel_df['y'], marker='o', linestyle='-')
plt.title('Travel Path')
plt.xlabel('x_new')
plt.ylabel('y')
plt.grid(True)
plt.show()

# Calculate the total distance of the travel path
total_distance = 0
for i in range(len(travel_df) - 1):
    point1 = Points(travel_df.iloc[i]['x_new'], travel_df.iloc[i]['y'])
    point2 = Points(travel_df.iloc[i+1]['x_new'], travel_df.iloc[i+1]['y'])
    total_distance += calculate_distance(point1, point2)

print("Total distance of the travel path:", total_distance)
