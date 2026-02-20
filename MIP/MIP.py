model_no = r"""
reset;

# Parameters
param m;
param n;
set couriers := {1..m};
set items := {1..n};
set DS := {1..n+1};

param capacity {couriers} > 0 integer;
param size {items} > 0 integer;
param D {DS, DS} >= 0 integer;
param upbound;
param lowbound := max {i in items} (D[n+1,i] + D[i,n+1]);
param M >= 0 integer;
let M := 1000;

# Decision Variables
var X {couriers, DS, DS} binary;
set Pos := {1..n};
var H {items} in Pos;
var Obj >= lowbound, <= upbound integer;

# Constraints
# Each item must be delivered
subject to ItemDelivery {i in items}:
    sum {c in couriers, d1 in DS} X[c, d1, i] = 1;
# Couriers must start and end at the depot
subject to StartAndEndAtDepot {i in couriers}:
    sum {y in DS} X[i, n+1, y] = 1
    and
    sum {x in DS} X[i, x, n+1] = 1;
# Balance the pickups and deliveries
subject to balanced_pickup {i in couriers, x in items}:
    sum {y in DS} X[i,x,y] = sum {y in DS} X[i,y,x];
# Ensure courier capacity is not exceeded
subject to CourierCapacity {c in couriers}:
    sum {i in items, d in DS} size[i] * X[c, d, i] <= capacity[c];
# Ensure proper visit order
subject to Subtourelimination {i in couriers, x in items, y in items}:
    H[x] >= H[y] - M * (1 - X[i,y,x]) + 1;

subject to obj_func {i in couriers}:
    sum {x in DS, y in DS} X[i,x,y] * D[x,y] <= Obj;

# Objective Function
minimize Obj_function: Obj;
"""

model_sym = r"""
reset;

# Parameters
param m;
param n;
set couriers := {1..m};
set items := {1..n};
set DS := {1..n+1};

param capacity {couriers} > 0 integer;
param size {items} > 0 integer;
param D {DS, DS} >= 0 integer;
param upbound;
param lowbound := max {i in items} (D[n+1,i] + D[i,n+1]);
param M >= 0 integer;
let M := 1000;

# Decision Variables
var X {couriers, DS, DS} binary;
set Pos := {1..n};
var H {items} in Pos;
var Obj >= lowbound, <= upbound integer;

# Constraints
# Each item must be delivered
subject to ItemDelivery {i in items}:
    sum {c in couriers, d1 in DS} X[c, d1, i] = 1;
# Couriers must start and end at the depot

subject to StartAndEndAtDepot {i in couriers}:
    sum {y in DS} X[i, n+1, y] = 1
    and
    sum {x in DS} X[i, x, n+1] = 1;
# Balance the pickups and deliveries

subject to balanced_pickup {i in couriers, x in items}:
    sum {y in DS} X[i,x,y] = sum {y in DS} X[i,y,x];
    
# Ensure courier capacity is not exceeded

subject to CourierCapacity {c in couriers}:
    sum {i in items, d in DS} size[i] * X[c, d, i] <= capacity[c];
# Ensure proper visit order

subject to Subtourelimination {i in couriers, x in items, y in items}:
    H[x] >= H[y] - M * (1 - X[i,y,x]) + 1;

# Symmetry Breaking Constraint
subject to symmetry_breaking {i in couriers: i < m}:
    sum {x in DS, y in DS} X[i, x, y] >= sum {x in DS, y in DS} X[i+1, x, y];

subject to obj_func {i in couriers}:
    sum {x in DS, y in DS} X[i,x,y] * D[x,y] <= Obj;

# Objective Function
minimize Obj_function: Obj;
 """
import numpy as np
import math
from amplpy import AMPL, modules
from typing import List, Tuple, Dict

# Active AMPL module
modules.activate("7f227b25-6563-4b6c-bd54-e768d3215df0")

class CourierOptimization:
    def __init__(self, m: int, n: int, loads: List[int], sizes: List[int], distance_matrix: np.ndarray):
        # Initializing model parameters
        self.m = m
        self.n = n
        self.loads = loads
        self.sizes = sizes
        self.distance_matrix = distance_matrix
        # Sorting couriers by load
        self.sorted_loads, self.permutation = self.sort_couriers_by_load()

    def sort_couriers_by_load(self) -> Tuple[List[int], List[int]]:
        # Sorting load in descending order
        sorted_loads = sorted([(load, i) for i, load in enumerate(self.loads)], reverse=True)
        loads_sorted, permutation = zip(*sorted_loads)
        return list(loads_sorted), list(permutation)

    def compute_optimization_bounds(self) -> Tuple[int, int]:
        # Getting max distance and round trip
        max_distance = np.max(self.distance_matrix)
        max_round_trip = np.max(self.distance_matrix[self.n, :]) + np.max(self.distance_matrix[:, self.n])
        return max_distance, max_round_trip

    def prepare_ampl_parameters(self) -> Dict:
        # Preparing parameters for AMPL solver
        max_distance, max_round_trip = self.compute_optimization_bounds()
        ampl_params = {
            'm': self.m,
            'n': self.n,
            'capacity': self.sorted_loads,
            'size': self.sizes,
            'D': np.ravel(self.distance_matrix).tolist(),
            'upbound': max_distance + max_round_trip
        }
        return ampl_params

    def run_solver(self, solver: str, model_func):
        # Running the AMPL solver and processing the solution
        ampl = AMPL()
        ampl.eval(model_func)
        
        ampl_params = self.prepare_ampl_parameters()
        for param, value in ampl_params.items():
            ampl.param[param] = value

        ampl.option["solver"] = solver
        ampl.option[f"{solver}_options"] = "timelim=300"
        
        ampl.solve()
        return self.process_solution(ampl)

    def process_solution(self, ampl) -> Dict:
        # Processing and returning the solution status
        solve_status = ampl.get_value("solve_result")
        elapsed_time = min(300, math.floor(ampl.get_value('_total_solve_time')))
        
        if solve_status == "infeasible":
            return {"time": elapsed_time, "optimal": False, "obj": "UNSAT", "routes": []}
        
        obj_value = round(ampl.get_objective('Obj_function').value())
        if obj_value == 0:
            return {"time": 300, "optimal": False, "obj": "N/A"}
        
        routes = self.decode_routes(ampl)
        return {"time": elapsed_time, "optimal": elapsed_time < 300, "obj": obj_value, "routes": routes}

    def decode_routes(self, ampl) -> List[List[int]]:
        # Decoding and returning courier routes
        raw_routes = ampl.get_variable("X").get_values().to_list()
        route_mapping = {i: {} for i in range(self.m)}
        
        for courier, start, end, assigned in raw_routes:
            if round(assigned) == 1:
                courier, start, end = map(int, (courier, start, end))
                route_mapping[self.permutation[courier - 1]][start - 1] = end - 1

        all_routes = []
        for courier in range(self.m):
            path = []
            next_stop = route_mapping[courier].get(self.n)
            while next_stop is not None and next_stop != self.n:
                path.append(next_stop + 1)
                next_stop = route_mapping[courier].get(next_stop)
            if path:
                all_routes.append(path)

        return all_routes


class OptimizationRunner:
    def __init__(self, model_configs: List[Tuple[str, callable]]):
        # Initialization with model configurations
        self.model_configs = model_configs

    def run(self, instance_file: str) -> Dict[str, Dict]:
        # Running optimization models on instance file
        results = {}
        m, n, loads, sizes, distance_matrix = self.load_instance(instance_file)

        optimizer = CourierOptimization(m, n, loads, sizes, distance_matrix)

        for model_name, model_func in self.model_configs:
            solver = model_name.split('_')[0]
            try:
                results[model_name] = optimizer.run_solver(solver, model_func)
            except Exception as e:
                print(f"Error running model {model_name}: {e}")
                results[model_name] = {"error": f"Optimization failed: {str(e)}"}
            else:
                print(f"Optimization completed for model: {model_name}")

        return results

    def load_instance(self, file_path: str) -> Tuple[int, int, List[int], List[int], np.ndarray]:
        # Loading instance data from files
        with open(file_path) as file:
            m = int(file.readline()) 
            n = int(file.readline())  
            loads = list(map(int, file.readline().split()))  
            sizes = list(map(int, file.readline().split()))  
            distance_matrix = np.genfromtxt(file, dtype=int)  

        return m, n, loads, sizes, distance_matrix