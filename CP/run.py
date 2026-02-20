import os
import subprocess
import math
import re
import json
import numpy as np
import io

def transform_dat_to_dzn(input_file, output_file):
    # Converting .dat instance file to .dzn format for MiniZinc
    with open(input_file, 'r') as file:
        content = file.readlines()

    courier_count = int(content[0].strip())
    item_count = int(content[1].strip())
    courier_capacities = list(map(int, content[2].strip().split()))
    item_sizes = list(map(int, content[3].strip().split()))
    distance_matrix = [list(map(int, line.strip().split())) for line in content[4:]]

    with open(output_file, 'w') as file:
        file.write(f"m = {courier_count};\n")
        file.write(f"n = {item_count};\n")
        file.write(f"l = {courier_capacities};\n")
        file.write(f"s = {item_sizes};\n")
        file.write("D = [|")
        for idx, row in enumerate(distance_matrix):
            file.write(", ".join(map(str, row)))
            file.write(",\n     |" if idx < len(distance_matrix) - 1 else "|];\n")

def parse_solution(output_text):
    # Parsing MiniZinc output and extracting solution details
    time_match = re.search(r"time elapsed: (\d+\.\d+)", output_text)
    elapsed_time = float(time_match.group(1)) if time_match else 300
    elapsed_time = math.floor(elapsed_time)

    is_optimal = elapsed_time < 300
    if "=UNKNOWN=" in output_text or "=UNSATISFIABLE=" in output_text or "=ERROR=" in output_text:
        return {"time": 300, "optimal": False, "obj": "N/A", "sol": []}
    if elapsed_time>=300:
        elapsed_time=300
    
    obj_line = next((line for line in output_text.splitlines() if "Maximum distance:" in line), None)
    if obj_line:
        objective_value = int(obj_line.split(":")[-1].strip())
    else:
        raise ValueError("Objective value not found in output.")

    # Extracting and processing the H matrix
    h_start = next(i for i, line in enumerate(output_text.splitlines()) if line.strip() == "H:")
    h_matrix_lines = output_text.splitlines()[h_start + 1 :]
    h_matrix = []
    for line in h_matrix_lines:
        if re.match(r"^\d+( \d+)*$", line.strip()):
            h_matrix.append(line.strip())
        else:
            break

    # Converting the H matrix to a numpy array
    H = np.genfromtxt(io.StringIO("\n".join(h_matrix)), dtype=int).tolist()
    if not isinstance(H[0], list):  # To ensure H is 2D, even for a single courier
        H = [H]

    # Determining routes for each courier
    routes = []
    num_couriers = len(H)  # Number of couriers corresponds to rows in H
    for courier_idx, route_sequence in enumerate(H):
        route = []
        visited = set()
        current_location = route_sequence[-1]  # Start at the last location in the sequence

        # Building routes with safeguards to prevent infinite loops
        while current_location not in visited and current_location <= len(route_sequence):
            visited.add(current_location)
            route.append(current_location)
            current_location = route_sequence[current_location - 1]  # Next location

        routes.append(route[:-1])

    return {
        "time": elapsed_time,
        "optimal": is_optimal,
        "obj": objective_value,
        "sol": routes,
    }
    
def execute_solver(params):
    # Running the solver for different models and collecting teh results
    results = {}
    input_dir = params.get('input_directory')
    output_dir = params.get('output_directory')
    input_files = params.get('instance_files')

    input_files = [os.path.abspath(os.path.join(input_dir, f)) for f in input_files]

    model_configs = [
        ("Gecode_sb", "sym.mzn"),
        ("chuffed_sb", "sym.mzn"),
        ("Gecode_nosb", "nosym.mzn"),
        ("chuffed_nosb", "nosym.mzn"),
        ("Gecode_int_nosb", "nosym_intsearch.mzn"),
        ("Gecode_int_sb", "sym_int.mzn")
    ]

    # Executing solver for each model
    for model_name, model_file in model_configs:
        model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), model_file)
        print(f"Executing model: {model_name} with file: {model_path}")

        solver_cmd = [
            "minizinc", "--solver", model_name.split('_')[0], "--output-time", "--solver-time-limit", "300000", model_path, *input_files
        ]

        try:
            execution_output = subprocess.run(solver_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except subprocess.CalledProcessError as error:
            print(f"Error while running model {model_name}: {error.stderr}")
            results[model_name] = {"time": 300, "optimal": False, "obj": "Error", "sol": []}
            continue
        
        solution = parse_solution(execution_output.stdout)
        results[model_name] = solution
        print(f"Model {model_name} executed successfully")

    print(results)
    return results


def save_solution_to_json(results, output_dir, instance_file):
    # And finally, saving the solver results to a JSON file
    instance_id = re.search(r'(\d+)', os.path.basename(instance_file)).group(1)
    instance_id = str(int(instance_id))  
    output_file = os.path.join(output_dir, f"{instance_id}.json")
    
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)
    print(f"Solution saved to {output_file}")