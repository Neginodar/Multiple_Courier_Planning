Here’s a step-by-step guide with the necessary instructions for running your model on Docker:
example:
1.  execute: docker build -t cdmo .
2. edit:
   if [ ! -f "/Users/negin/Desktop/N/CDMO_DEC/Instances/$INSTANCE_FILE" ]; then 
   docker run -it -v /Users/negin/Desktop/CDMO_feb/Instances:/src/Instances -v /Users/negin/Desktop/N/CDMO_feb/res:/src/res $IMAGE_NAME /venv/bin/python3 run_m2.py /src/Instances/$INSTANCE_FILE $SOLVING_METHOD
3. execute: ./run_docker.sh inst01.dat SAT

description:
	1.	Build your Docker Image
First, you need to build your Docker image by running the following command in your terminal:

docker build -t cdmo_final .  

You can replace cdmo_final with any other tag you prefer, which will help you identify and use the image later.
	2.	Edit the run_docker.sh File
Before running the above command, you must edit the run_docker.sh file to specify the correct directories for instances and output. Ensure that you set the correct paths for your input files (instances) and output directory within the run_docker.sh file.

	3.	Run the Docker Image
Once the image is built, you can run it directly or use a script. To run the Docker container, you can use:

./run_docker.sh <instance_file> <method>

Where:
	•	<instance_file>: The path to the instance file (input data).
	•	<method>: The method or solver you want to use for solving the problem.


Make sure to adjust paths and the instance data as needed before executing these steps.

