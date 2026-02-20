
# Base image
FROM minizinc/minizinc:latest

# Set working directory
WORKDIR /src

# Copy all project files into the Docker image (including requirements.txt)
COPY . .

# Install necessary system packages
RUN apt-get update \
  && apt-get install -y python3 python3-pip python3-venv \
  && apt-get clean

# Create a virtual environment
RUN python3 -m venv /venv

# Upgrade pip and install Python packages
RUN /venv/bin/pip install --upgrade pip setuptools wheel \
  && /venv/bin/pip install -r requirements.txt

# Install amplpy
RUN /venv/bin/pip install amplpy --no-cache-dir

# Install solver modules (including CPLEX)
RUN /venv/bin/python -m amplpy.modules install cbc highs gurobi  --no-cache-dir 
# Verify ampltools installation
RUN /venv/bin/python3 -c "import ampltools" || (echo 'ampltools not installed!' && exit 1)

# Pre-install solvers using ampltools script
RUN /venv/bin/ampltools install --loglevel=debug || echo "ampltools installation failed"

# Set environment variables for instance file and method (at runtime, not in the Dockerfile)
# These will be passed when running the container


# Activate the amplpy license (this should be done at runtime, not during build)
# Leave it empty for now; replace <license-uuid> at runtime.
CMD /bin/bash -c "source /venv/bin/activate && python -c 'from amplpy import modules; modules.activate(\"<dbc006a7-eff8-48ba-a704-f5cb123de33c>\")' && python run_m2.py $instance_file $method"