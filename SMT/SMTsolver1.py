import time
from itertools import permutations
from z3.z3 import *

# Reads input data from a file
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

# Finds the optimal route using a greedy nearest-neighbor approach
def find_optimal_tour(products, distances, remaining_time):
    if len(products) == 0:
        return [], 0
    
    origin_index = len(distances) - 1
    unvisited = set(products)
    current = origin_index
    route = [current]
    total_distance = 0
    start_time = time.time()

    # nearest unvisited product iteratively
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
    D = [Real(f"D_{i}") for i in range(num_couriers)]
    Dmax = Real("Dmax")

    # Soft constraint to maintain order in assignments with Lexicographical Ordering 
    for j in range(1, num_products):
        optimizer.add_soft(M[0][j] <= M[0][j-1], weight= 2)

    # Constraints: Each product is assigned to exactly one courier
    for i in range(num_couriers):
        for j in range(num_products):
            optimizer.add(Or(M[i][j] == 0, M[i][j] == 1))
    for j in range(num_products):
        optimizer.add(Sum([M[i][j] for i in range(num_couriers)]) == 1)

    # Ensure couriers do not exceed their capacity
    for i in range(num_couriers):
        optimizer.add(Sum([M[i][j] * product_sizes[j] for j in range(num_products)]) <= capacities[i])

    current_best_max_distance = float('inf')
    solution_found = False
    iteration_count = 0
    no_improvement_count = 0
    previous_assignments = set() 
    start_time = time.time()  
    max_time = 5 * 60  
    best_route = None
    
    while True:
        optimal_route = []
        elapsed_time = time.time() - start_time
        remaining_time = max_time - elapsed_time
        if remaining_time <= 0:
            break

        # Termination conditions
        if not iteration_count < max_iterations:
            break
        if not no_improvement_count < max_no_improvement_iterations:
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

        # Compute the optimal route for each courier
        for i in range(num_couriers):
            assigned_products = [j for j in range(num_products) if assignment_matrix[i][j] == 1]

            if assigned_products:
                tmp_route, optimal_distance = find_optimal_tour(assigned_products, distances, remaining_time)
                tmp_route = tmp_route[1:]
                optimal_route.append(tmp_route)
                total_distances.append(optimal_distance)
            else:
                total_distances.append(0)

        # Update the best-known solution if an improvement is found
        max_distance = max(total_distances)
        if max_distance < current_best_max_distance:
            current_best_max_distance = max_distance
            solution_found = True
            best_assignment_matrix = [row[:] for row in assignment_matrix]
            best_distances_traveled = total_distances[:]
            best_route = optimal_route
            no_improvement_count = 0  
        else:
            no_improvement_count += 1

        different_assignments = []
        for i in range(num_couriers):
            for j in range(num_products):
                different_assignments.append(M[i][j] != assignment_matrix[i][j])

        optimizer.add_soft(Or(different_assignments), weight=1)

    if solution_found:
        return best_assignment_matrix, best_distances_traveled, current_best_max_distance, best_route
    else:
        return None,None,None,None

