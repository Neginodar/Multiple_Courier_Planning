
import os
import sys
import json
import jsbeautifier
import re
import numpy as np
import io
import math
from MIP.MIP import CourierOptimization, OptimizationRunner, model_no, model_sym
from CP.run import execute_solver
from SMT.runner import run_SMT_solver


def convert_dat_to_dzn(input_filename, output_filename):
    if input_filename.endswith(".dzn"):
        print(f"{input_filename} is already in .dzn format. Skipping conversion.")
        return
    
    with open(input_filename, 'r') as f:
        lines = f.readlines()

    try:
        m = int(lines[0].strip())
        n = int(lines[1].strip())
        l = list(map(int, lines[2].strip().split()))
        s = list(map(int, lines[3].strip().split()))

        D = []
        for line in lines[4:]:
            row = list(map(int, line.strip().split()))
            D.append(row)
    except ValueError as e:
        print(f"Error parsing .dat file: {input_filename}")
        raise e

    with open(output_filename, 'w') as f:
        f.write(f"m = {m};\n")
        f.write(f"n = {n};\n")
        f.write(f"l = {l};\n")
        f.write(f"s = {s};\n")
        f.write("D = [|")
        for i in range(n + 1):
            f.write(", ".join(map(str, D[i])))
            if i < n:
                f.write(",\n     |")
            else:
                f.write("|];\n")

def get_instance_number(filename):
    solving_method = sys.argv[2]
    if solving_method == "CP":
        groups = re.findall(r"inst(\d+)\.(dat|dzn)", filename)
    else:
        groups = re.findall(r"inst(\d+)\.dat", filename)

    if len(groups) == 0:
        print(f"ValueError: the instance filename must end with instX.dzn if using CP and instX.dat otherwise, where X is the instance number")
        exit()
    if solving_method == "CP":
        return int(groups[0][0])
    else:
        return int(groups[0])

def beautify_and_save_output(result, output_dir, inst_number):
    opts = jsbeautifier.default_options()
    opts.keep_array_indentation = True
    output = jsbeautifier.beautify(json.dumps(result), opts)

    os.makedirs(output_dir, exist_ok=True)
    outfile_name = os.path.join(output_dir, f"{inst_number}.json")

    with open(outfile_name, "w+") as outfile:
        outfile.write(output)

    print(f"Successfully saved output to {outfile_name}")

def validate_arguments():
    if len(sys.argv) != 3:
        print(f"ValueError: Exactly two arguments expected: 1. path to instance file, 2. solving method (SAT, MIP, CP, SMT)")
        exit()

def run_optimization():
    validate_arguments()

    instance_file = sys.argv[1]
    solving_method = sys.argv[2]
    instance_number = get_instance_number(instance_file)
    input_directory = "/src/Instances"
    output_directory = "/src/res"

    if solving_method == "MIP":
        m, n, loads, sizes, distance_matrix = load_instance(instance_file)
        optimizer = CourierOptimization(m, n, loads, sizes, distance_matrix)
        model_configs = [
            ("highs", model_no),
            ("gurobi", model_no),
            ("gurobi_sb", model_sym),
            ("highs_sb", model_sym)
        ]

        runner = OptimizationRunner(model_configs)
        results = runner.run(instance_file)

        beautify_and_save_output(results, output_directory +"/MIP", instance_number)

    elif solving_method == "CP":
        print(f"Running CP solver on {instance_file}")

        inst_number = get_instance_number(instance_file)
        dzn_file = instance_file if instance_file.endswith(".dzn") else os.path.join(input_directory, f"inst{inst_number:02d}.dzn")
        
        if not instance_file.endswith(".dzn"):
            convert_dat_to_dzn(instance_file, dzn_file)
        
        solver_args = {
            'input_directory': input_directory,
            'output_directory': output_directory,
            'instance_files': [dzn_file]
        }
        solutions = execute_solver(solver_args)
        
        if solutions is None:
            print("Error: CP solver did not return a result.")
            exit()

        beautify_and_save_output(solutions, output_directory+"/CP", inst_number)
    

    elif solving_method == "SMT":
        print(f"Running SMT solver on {instance_file}")
        inst_number = get_instance_number(instance_file)
        inst_files = [f"inst{inst_number:02d}.dat"]
        run_SMT_solver(input_directory, output_directory+"/SMT", inst_files)

    else:
        print(f"ValueError: Invalid solving method '{solving_method}'")
        exit()

def load_instance(file_path):
    with open(file_path) as file:
        m = int(file.readline())
        n = int(file.readline())
        loads = list(map(int, file.readline().split()))
        sizes = list(map(int, file.readline().split()))
        distance_matrix = np.genfromtxt(file, dtype=int)

    return m, n, loads, sizes, distance_matrix

if __name__ == "__main__":
    run_optimization()