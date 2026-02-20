import time
from itertools import permutations
from z3 import *

def read_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    m = int(lines[0].strip())
    n = int(lines[1].strip())
    capacities = list(map(int, lines[2].strip().split()))
    sizes = list(map(int, lines[3].strip().split()))
    distance_matrix = [list(map(int, line.strip().split())) for line in lines[4:]]
    return m, n, capacities, sizes, distance_matrix

def find_optimal_tour(products, distances, remaining_time):
    if len(products) == 0:
        return [], 0

    origin_index = len(distances) - 1
    unvisited = set(products)
    current = origin_index
    route = [current]
    total_distance = 0
    start_time = time.time()

    while unvisited:
        if time.time() - start_time > remaining_time:
            return route[1:], total_distance
        next_product = min(unvisited, key=lambda x: distances[current][x])
        route.append(next_product)
        total_distance += distances[current][next_product]
        current = next_product
        unvisited.remove(next_product)

    total_distance += distances[current][origin_index]
    return route[1:], total_distance

def courier_planning(num_couriers, num_products, capacities, product_sizes, distances, max_iterations=2000, max_no_improvement_iterations=100, max_time=5*60):
    optimizer = Optimize()
    optimizer.set("timeout", 300000)

    sorted_products = sorted(range(num_products), key=lambda x: -product_sizes[x])
    sorted_couriers = sorted(range(num_couriers), key=lambda x: -capacities[x])

    sorted_product_sizes = [product_sizes[i] for i in sorted_products]
    sorted_capacities = [capacities[i] for i in sorted_couriers]

    product_mapping = {sorted_products[i]: i for i in range(num_products)}
    courier_mapping = {sorted_couriers[i]: i for i in range(num_couriers)}

    M = [[Int(f"M_{i}_{j}") for j in range(num_products)] for i in range(num_couriers)]
    D = [Real(f"D_{i}") for i in range(num_couriers)]
    Dmax = Real("Dmax")

    for i in range(num_couriers):
        for j in range(num_products):
            optimizer.add(Or(M[i][j] == 0, M[i][j] == 1))

    for j in range(num_products):
        optimizer.add(Sum([M[i][j] for i in range(num_couriers)]) == 1)

    for i in range(num_couriers):
        optimizer.add(Sum([M[i][j] * sorted_product_sizes[j] for j in range(num_products)]) <= sorted_capacities[i])

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

        if not iteration_count < max_iterations:
            break
        if not no_improvement_count < max_no_improvement_iterations:
            break

        iteration_count += 1
        if optimizer.check() != sat:
            break

        model = optimizer.model()
        total_distances = []

        assignment_matrix = [[model.evaluate(M[i][j]).as_long() for j in range(num_products)] for i in range(num_couriers)]

        assignment_plan = tuple(frozenset(j for j in range(num_products) if assignment_matrix[i][j] == 1) for i in range(num_couriers))

        if assignment_plan in previous_assignments:
            continue

        previous_assignments.add(assignment_plan)

        for i in range(num_couriers):
            assigned_products = [sorted_products[j] for j in range(num_products) if assignment_matrix[i][j] == 1]

            if assigned_products:
                tmp_route, optimal_distance = find_optimal_tour(assigned_products, distances, remaining_time)
                total_distances.append(optimal_distance)
                optimal_route.append(tmp_route)
            else:
                total_distances.append(0)

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
        new_ass = []
        for i in best_route:
          new_ass.append([sorted_products[j] for j in i])
        c = []
        #print(courier_mapping)
        #print(best_assignment_matrix)
        
        for i in range(len(best_assignment_matrix)):
            c.append([])
        print(c)
        courier_mapping.values()
        for ind,k in enumerate(best_route):
          print(ind, k)
          print(best_route, c)
          c[ind] = best_route[k]  
        return best_assignment_matrix, best_distances_traveled, current_best_max_distance, c
    else:
        return None, None, None, None
