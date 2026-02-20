
import os
from SMT import SMTsolver1
from SMT import SMTsolver2
from SMT import SMTsolver3
from SMT import SMTsolver5
import json
import math
import time as time_module
from SMT.SMTsolver1 import read_data

def run_SMT_solver(input_dir, output_dir, instance_files, timeout=300):
    dictionary = {}
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load instances
    for instance_file in instance_files:
        # Read instance 
        filepath = os.path.join(input_dir, instance_file)
        m, n, capacities, sizes, distances = read_data(filepath)

        print(f"Running solver for {instance_file}...")

        # Run courier_planning to optimize
        max_iterations = 2500
        max_no_improvement_iterations = 200
        max_time = 5 * 60  # 5 minutes timeout
        
        #*******************baseline***********************
        # Start measuring time
        start_time = time_module.time()

        assign, courier, max_dis, route = SMTsolver1.courier_planning(
            m, n, capacities, sizes, distances, max_iterations, max_no_improvement_iterations, max_time
        )

        # Calculate the elapsed time
        elapsed_time = time_module.time() - start_time
        elapsed_time = math.floor(elapsed_time) 

        # solution is optimal?
        optimal = True
        if elapsed_time >= timeout:
            optimal = False
            elapsed_time = timeout 
        n_route = []
        if route==None:                                                                                                                                                    
            n_route = "N/A"
        else:
            for i in route:
                row = [j+1 for j in i]
                n_route.append(row)
        if max_dis==None:
            max_dis = "N/A"  
                
        # output data to a dictionary
        output_data1 = {"SMT_z3":{"time": elapsed_time, "optimal": optimal, "obj": max_dis, "sol": n_route}}
        
        #****************************cvc5*************************
        # Run courier_planning to optimize
        max_iterations = 2500
        max_no_improvement_iterations = 900
        max_time = 5 * 60  # 5 minutes timeout \

        # clock the timer
        start_time = time_module.time()

        assign, courier, max_dis, route = SMTsolver2.courier_planning(
            m, n, capacities, sizes, distances, max_iterations, max_no_improvement_iterations, max_time
        )

        # elapsed time
        elapsed_time = time_module.time() - start_time
        elapsed_time = math.floor(elapsed_time)  

        # iw the solution optimal?
        optimal = True
        if elapsed_time >= timeout:
            optimal = False
            elapsed_time = timeout 
        n_route = []
        if route==None:                                                                                                                                                    
            n_route = "N/A"
        else:
            for i in route:
                row = [j+1 for j in i]
                n_route.append(row)
        if max_dis==None:
            max_dis = "N/A"  
                
        # output data to a dictionary
        output_data2 = {"SMT_cvc5":{"time": elapsed_time, "optimal": optimal, "obj": max_dis, "sol": n_route}}        

        #********************ET******************
        # optimize courier assignments
        max_iterations = 2500
        max_no_improvement_iterations = 200
        max_time = 5 * 60  # 5 minutes timeout

        # clock the timer
        start_time = time_module.time()

        assign, courier, max_dis, route = SMTsolver3.courier_planning(
            m, n, capacities, sizes, distances, max_iterations, max_no_improvement_iterations, max_time
        )

        elapsed_time = time_module.time() - start_time
        elapsed_time = math.floor(elapsed_time)

        # if the solution is optimal
        optimal = True
        if elapsed_time >= timeout:
            optimal = False
            elapsed_time = timeout
        n_route = []
        if route==None:                                                                                                                                                    
            n_route = "N/A"
        else:
            for i in route:
                row = [j+1 for j in i]
                n_route.append(row)
        if max_dis==None:
            max_dis = "N/A"     
        # output data to a dictionary
        output_data3 = {"SMT_ET":{"time": elapsed_time, "optimal": optimal, "obj": max_dis, "sol": n_route}} 
        
        #************************Lowerbound-Upperbound********************

        assign, courier, max_dis, route = SMTsolver5.courier_planning(
            m, n, capacities, sizes, distances, max_iterations, max_no_improvement_iterations, max_time
        )

        # clock the timer
        elapsed_time = time_module.time() - start_time
        elapsed_time = math.floor(elapsed_time) 

        # if the solution is optimal
        output_data4 = []
        optimal = True
        if assign == "Unsat":
            output_data4 = {"SMT_LB-UB":{"time": 300, "optimal": False, "obj": "N/A", "sol": "N/A"}}
        else:
            if elapsed_time >= timeout:
                optimal = False
                elapsed_time = timeout
            n_route = []
            if route==None:
                if optimal:
                    optimal="UNSAT"                                                                                                                                                    
                n_route = "N/A"
            else:
                for i in route:
                    row = [j+1 for j in i]
                    n_route.append(row)
            if max_dis==None:
                max_dis = "N/A"     
            # put the output data to  dictionary
            output_data4 = {"SMT_LB-UB":{"time": elapsed_time, "optimal": optimal, "obj": max_dis, "sol": n_route}}        


        
        output_data = {**output_data1, **output_data2, **output_data3, **output_data4}
        # Extract instance number from the filenam
        instance_number = int(instance_file.split('inst')[-1].split('.dat')[0])  # Extract instance number
        dictionary[instance_number] = output_data

        # Save the result to a JSON file 
        output_file = os.path.join(output_dir, f"{instance_number}.json")
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
            print(f"Solver execution complete for {instance_file}. Results saved to {output_file}")


    return dictionary




