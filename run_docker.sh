#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <instance_file> <method>"
    exit 1
fi

# Get the instance file and method from the arguments
INSTANCE_FILE=$1
SOLVING_METHOD=$2

# Check if the instance file exists in the local directory
if [ ! -f "/Users/negin/Desktop/CDMO_feb/Instances/$INSTANCE_FILE" ]; then
    echo "Error: Instance file '$INSTANCE_FILE' not found."
    exit 1
fi

# Set the Docker image name
IMAGE_NAME="cdmo_img"

# Run the Docker container with the provided arguments
docker run -it -v /Users/negin/Desktop/CDMO_feb/Instances:/src/Instances -v /Users/negin/Desktop/CDMO_feb/res:/src/res $IMAGE_NAME /venv/bin/python3 run_m2.py /src/Instances/$INSTANCE_FILE $SOLVING_METHOD