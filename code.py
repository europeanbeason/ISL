import gurobipy as gp
from gurobipy import GRB
distances = {(0, 1): 10, (0, 2): 5, (1, 2): 4,
             (1, 0): 10, (2, 0): 5, (2, 1): 4}
# it's a dictionary with keys (i,j) and values d_{ij}


def TSP(d):
    model = gp.Model("TSP")

    # Decision variables:
    y = {}
    for key in d.keys():
        y[key] = model.addVar(
            name=f'y({key})', vtype=GRB.BINARY)

    n = int(len(y)/2)
    # Objective
    D = model.addVar(vtype=GRB.CONTINUOUS, name="D")
    model.setObjective(D, GRB.MINIMIZE)

    # Constraints
    model.addConstr(gp.quicksum(gp.quicksum(
        d[(i, j)] * y[(i, j)] for j in range(n) if j != i) for i in range(n)) == D, "Distance constraint")

    for j in range(n):
        model.addConstr(gp.quicksum(y[(i, j)] for i in range(
            n) if i != j) == 1, name=f"visit_hole_{j}_once")

    for i in range(n):
        model.addConstr(gp.quicksum(y[(i, j)] for j in range(
            n) if j != i) == 1, name=f"move_hole_{i}_to_another")

    model.addConstr(gp.quicksum(y[(0, j)]
                    for j in range(1, n)) == 1, name=f"start_from_origin")

    # Optimization
    model.optimize()
    # Solution
    solution = {v.varName: v.x for v in model.getVars()}
    return (solution, model.ObjVal)


tsp = TSP(distances)
for var_name, value in tsp[0].items():
    print(f"{var_name} = {value}")
