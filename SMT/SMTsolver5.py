import time
from itertools import permutations
from z3.z3 import *

# Function to read input data from a file
def read_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Extract number of couriers and products
    m = int(lines[0].strip())
    n = int(lines[1].strip())

    # Read capacities, product sizes, and distance matrix
    capacities = list(map(int, lines[2].strip().split()))
    sizes = list(map(int, lines[3].strip().split()))
    distance_matrix = [list(map(int, line.strip().split())) for line in lines[4:]]

    return m, n, capacities, sizes, distance_matrix

# Function to find the optimal delivery route for a courier
def find_optimal_tour(products, distances, remaining_time):
    if len(products) == 0:
        return [], 0

    origin_index = len(distances) - 1
    unvisited = set(products)
    current = origin_index
    route = [current]
    total_distance = 0
    start_time = time.time()

    # Greedy selection of the nearest unvisited product
    while unvisited:
        if time.time() - start_time > remaining_time:
            return route, total_distance
        next_product = min(unvisited, key=lambda x: distances[current][x])
        route.append(next_product)
        total_distance += distances[current][next_product]
        current = next_product
        unvisited.remove(next_product)

    total_distance += distances[current][origin_index]
    return route, total_distance

def courier_planning(num_couriers, num_products, capacities, product_sizes, distances, max_iterations=2000, max_no_improvement_iterations=100, max_time=5*60):
    optimizer = Optimize()
    optimizer.set("timeout", 300000) 

    # Decision variables: M[i][j] -> 1 if courier i is assigned to product j
    M = [[Int(f"M_{i}_{j}") for j in range(num_products)] for i in range(num_couriers)]
    D = [Real(f"D_{i}") for i in range(num_couriers)]  # Distance traveled by each courier
    Dmax = Real("Dmax")  # Max distance traveled by any courier

    # Constraints: Each product must be assigned to exactly one courier
    for i in range(num_couriers):
        for j in range(num_products):
            optimizer.add(Or(M[i][j] == 0, M[i][j] == 1))

    for j in range(num_products):
        optimizer.add(Sum([M[i][j] for i in range(num_couriers)]) == 1)

    # Capacity constraints for couriers
    for i in range(num_couriers):
        optimizer.add(Sum([M[i][j] * product_sizes[j] for j in range(num_products)]) <= capacities[i])

    # Distance calculations
    for i in range(num_couriers):
        optimizer.add(D[i] == Sum([M[i][j] * distances[-1][j] for j in range(num_products)]))
        optimizer.add(Dmax >= D[i])

    # lower and upper bounds for optimization
    total_item_distances = sum(distances[-1][j] for j in range(num_products))
    LB = max(total_item_distances / num_couriers, 0)
    UB = float('inf')

    optimizer.add(Dmax >= LB)  # Ensure Dmax is at least the lower bound

    # Iterative search for an optimal solution
    current_best_max_distance = float('inf')
    solution_found = False
    iteration_count = 0
    no_improvement_count = 0
    previous_assignments = set()
    start_time = time.time()
    best_route = None

    while True:
        elapsed_time = time.time() - start_time
        remaining_time = max_time - elapsed_time

        # Termination conditions
        if remaining_time <= 0 or iteration_count >= max_iterations or no_improvement_count >= max_no_improvement_iterations:
            break

        iteration_count += 1

        if optimizer.check() != sat:
            break

        model = optimizer.model()
        total_distances = []

        # Extract assignment matrix from model
        assignment_matrix = [[model.evaluate(M[i][j]).as_long() for j in range(num_products)] for i in range(num_couriers)]
        assignment_plan = tuple(frozenset(j for j in range(num_products) if assignment_matrix[i][j] == 1) for i in range(num_couriers))

        # Avoid duplicate assignments
        if assignment_plan in previous_assignments:
            continue
        previous_assignments.add(assignment_plan)

        boundingbol = False
        optimal_route = []

        # Compute the optimal route for each courier
        for i in range(num_couriers):
            assigned_products = [j for j in range(num_products) if assignment_matrix[i][j] == 1]

            if assigned_products:
                tmp_route, optimal_distance = find_optimal_tour(assigned_products, distances, remaining_time)
                if optimal_distance <= UB and optimal_distance >= LB:
                    tmp_route = tmp_route[1:]  # Remove starting location
                    optimal_route.append(tmp_route)
                    total_distances.append(optimal_distance)
                else:
                    boundingbol = True
                    break
            else:
                total_distances.append(0)

        if boundingbol:
            continue

        # get the max_distance of current planning to check for improvment
        max_distance = max(total_distances)

        valid_solution = True
        for i in range(num_couriers):
            assigned_products = [j for j in range(num_products) if assignment_matrix[i][j] == 1]
            total_size = sum(product_sizes[j] for j in assigned_products)
            if total_size > capacities[i]:
                valid_solution = False
                break

        if valid_solution and max_distance < current_best_max_distance:
            current_best_max_distance = max_distance
            UB = current_best_max_distance + 1
            optimizer.add(Dmax <= UB)
            solution_found = True
            best_assignment_matrix = [row[:] for row in assignment_matrix]
            best_distances_traveled = total_distances[:]
            best_route = optimal_route
            no_improvement_count = 0
        else:
            no_improvement_count += 1

        # Enforce diversity in assignments to explore new solutions
        different_assignments = []
        for i in range(num_couriers):
            for j in range(num_products):
                different_assignments.append(M[i][j] != assignment_matrix[i][j])

        optimizer.add_soft(Or(different_assignments), weight=1)

    if solution_found:
        return best_assignment_matrix, best_distances_traveled, current_best_max_distance, best_route
    else:
        return "Unsat", "Unsat", "Unsat", "Unsat"
