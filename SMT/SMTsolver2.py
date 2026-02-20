import os
import json
import math
import time as time_module
import cvc5
from cvc5 import Kind
import time

#  Reads input data from a file
def read_data(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Extract number of couriers and product
    m = int(lines[0].strip())
    n = int(lines[1].strip())

    # Read capacities, product sizes, and distance matrix
    capacities = list(map(int, lines[2].strip().split()))

    sizes = list(map(int, lines[3].strip().split()))

    distance_matrix = [list(map(int, line.strip().split())) for line in lines[4:]]

    return m, n, capacities, sizes, distance_matrix

def find_optimal_tour(products, distances, remaining_time, origin_index=None):
    if len(products) == 0:
        return [], 0

    # Default origin index is the last node
    if origin_index is None:
        origin_index = len(distances) - 1

    unvisited = set(products)
    current = origin_index
    route = [current]
    total_distance = 0
    start_time = time.time()

    # search nearest unvisited product iteratively
    while unvisited:
        if time.time() - start_time > remaining_time:
          return route[1:len(route)-1], total_distance

        next_product = min(unvisited, key=lambda x: distances[current][x])
        route.append(next_product)
        total_distance += distances[current][next_product]
        current = next_product
        unvisited.remove(next_product)

    total_distance += distances[current][origin_index]
    route.append(origin_index)

    return route[1:len(route)-1], total_distance

def courier_planning(num_couriers, num_products, capacities, product_sizes, distances, max_iterations=2000, max_no_improvement_iterations=100, max_time=5*60):

  solver = cvc5.Solver()
  solver.setOption("produce-models", "true")
  solver.setLogic("QF_UFLIA")  # logic for optimization

  # Decision variables: M[i][j] -> 1 if courier i is assigned to product j
  M = [[solver.mkConst(solver.getBooleanSort(), f"M_{i}_{j}") for j in range(num_products)] for i in range(num_couriers)]

  Dmax = solver.mkConst(solver.getIntegerSort(), "Dmax")

  # Constraints: Each product is assigned to exactly one courier
  for i in range(num_couriers):
      for j in range(num_products):
          solver.assertFormula(solver.mkTerm(Kind.OR,
                                            solver.mkTerm(Kind.EQUAL, M[i][j], solver.mkBoolean(True)),
                                            solver.mkTerm(Kind.EQUAL, M[i][j], solver.mkBoolean(False))))

  
  for j in range(num_products):
      bool_to_int_terms = [solver.mkTerm(Kind.ITE, M[i][j], solver.mkInteger(1), solver.mkInteger(0)) for i in range(num_couriers)]
      assignment_sum = solver.mkTerm(Kind.ADD, *bool_to_int_terms)
      solver.assertFormula(solver.mkTerm(Kind.EQUAL, assignment_sum, solver.mkInteger(1)))

  # Capacity constraints: Total load per courier must not exceed capacity
  for i in range(num_couriers):
      courier_load = solver.mkTerm(Kind.ADD, *[solver.mkTerm(Kind.ITE, M[i][j], solver.mkInteger(product_sizes[j]), solver.mkInteger(0)) for j in range(num_products)])
      solver.assertFormula(solver.mkTerm(Kind.LEQ, courier_load, solver.mkInteger(capacities[i])))

  # Prevent overlapping assignments between couriers with symmetry-breaking constraint
  for i in range(num_couriers - 1):
      for j in range(num_products - 1):
          solver.assertFormula(
              solver.mkTerm(
                  Kind.IMPLIES,
                  solver.mkTerm(Kind.AND, M[i][j], M[i + 1][j + 1]),
                  solver.mkTerm(Kind.NOT, M[i + 1][j])
              )
          )



  start_time = time.time()
  max_time = max_time
  max_iterations = max_iterations
  max_no_improvement_iterations = max_no_improvement_iterations
  iteration_count = 0
  no_improvement_count = 0
  solution_found = False
  best_max_distance = float('inf')
  best_assignment = None
  solution_found = False
  best_route = None

  while True:
      optimal_route = []

      # termination conditions
      elapsed_time = time.time() - start_time
      if elapsed_time >= max_time:
          break

      if iteration_count >= max_iterations:
          break

      if no_improvement_count >= max_no_improvement_iterations:
          break

      result = solver.checkSat()
      if not result.isSat():
          break

      # extract assignment matrix from model
      iteration_count += 1

      current_assignment = []
      for i in range(num_couriers):
          row = []
          for j in range(num_products):
              value = solver.getValue(M[i][j])
              if str(value) == "true":
                  row.append(j)
          current_assignment.append(row)


      current_distances = []
      optimal_route = []

      # compute the optimal route for each courier
      for i in range(num_couriers):
          assigned_products = current_assignment[i]

          if assigned_products:
              tmp_route, optimal_distance = find_optimal_tour(assigned_products, distances, max_time-elapsed_time, origin_index=len(distances) - 1)
              optimal_route.append(tmp_route)
              current_distances.append(optimal_distance)
          else:
              current_distances.append(0)
              optimal_route.append([])

      # update the best-known solution if an improvement is found 
      current_max_distance = max(current_distances)

      if current_max_distance < best_max_distance:
          best_max_distance = current_max_distance
          best_assignment = current_assignment
          no_improvement_count = 0
          solution_found = True
          best_route = optimal_route
      else:
          no_improvement_count += 1

      # enforce divers assignment to explore new solutions
      exclusion_constraints = []
      for i in range(num_couriers):
          for j in range(num_products):
              exclusion_constraints.append(solver.mkTerm(Kind.NOT, solver.mkTerm(Kind.EQUAL, M[i][j], solver.mkBoolean(j in current_assignment[i]))))
      solver.assertFormula(solver.mkTerm(Kind.OR, *exclusion_constraints))

  if solution_found:
        return best_assignment, None, best_max_distance, best_route
  else:
        return None, None, None, None