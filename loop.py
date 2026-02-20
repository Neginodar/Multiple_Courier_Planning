import subprocess

# Path to the directory containing the instances
instances_path = "/Users/negin/Desktop/CDMO_feb/Instances/"

# Loop over the instances inst01.dat to inst10.dat
for i in range(4,7):
    # Generate the instance filename
    instance_filename = f"inst{str(i).zfill(2)}.dat"

    # Full path to the instance file
    instance_file = instances_path + instance_filename
    
    # Run the Python script with the instance file and MIP solver
    print(f"Running instance {instance_filename}...")
    try:
        result = subprocess.run(["python", "run_m.py", instance_file, "MIP"], check=True, capture_output=True, text=True)
        print(result.stdout)  # Output from the script
    except subprocess.CalledProcessError as e:
        print(f"Error while running instance {instance_filename}: {e.stderr}")

print("All instances have been processed.")