## Multiple Courier Delivery & Matching Optimization (CDMO)

This repository contains models, solvers, and instance data used for the CDMO project. The full technical report is included as `CDMO_report.pdf` — refer to it for detailed methodology, experiments and results.

**Contents:**
- **CP/**: MiniZinc constraint programming models and runner scripts.
- **MIP/**: Mixed-Integer Programming implementation and helpers.
- **SMT/**: SMT-based solvers and the `runner.py` orchestrator.
- **Instances/**: Problem instance files (`.dzn`/`.dat`).
- **res/**: JSON result files for CP, MIP and SMT experiments.

**Summary (from the report)**
- We study the Multiple Courier Planning problem and evaluate three modelling approaches: Constraint Programming (CP), Mixed Integer Programming (MIP) and SMT encodings.
- Experiments use the instances in `Instances/` and results are in `res/` — see `CDMO_report.pdf` for performance tables and comparative analysis.

## Quick Start

Requirements:
- Python dependencies: see `requirements.txt`.
- Docker (optional) to run inside a container.

Run locally (examples):
- MIP solver: `python3 MIP/MIP.py <instance_file>`
- CP solver: `python3 CP/run.py <instance_file>`
- SMT solvers: `python3 SMT/runner.py <instance_file>`
- Wrapper runs: `python3 run_m.py <instance_file> <method>` or `python3 run_m2.py <instance_file> <method>`

## Docker — build and run

1. Build the image (run in repository root):
   
   docker build -t cdmo:latest .

2. Example run (macOS — mounts workspace Instances and res):
   
   docker run --rm -it \
     -v /Users/negin/Desktop/CDMO_feb/Instances:/src/Instances \
     -v /Users/negin/Desktop/CDMO_feb/res:/src/res \
     cdmo:latest \
     /venv/bin/python3 run_m2.py /src/Instances/inst01.dat MIP

3. Optional helper script `run_docker.sh` (place in repo root):

```bash
#!/usr/bin/env bash
# run_docker.sh
INSTANCE_FILE="$1"   # e.g. inst01.dat
METHOD="$2"          # e.g. MIP, CP, SMT
IMAGE_NAME="cdmo:latest"

docker build -t "$IMAGE_NAME" .
docker run --rm -it \
  -v "$(pwd)/Instances":/src/Instances \
  -v "$(pwd)/res":/src/res \
  "$IMAGE_NAME" /venv/bin/python3 run_m2.py "/src/Instances/$INSTANCE_FILE" "$METHOD"
```

Make it executable:
   
   chmod +x run_docker.sh

Usage:
   
   ./run_docker.sh inst01.dat MIP

Notes:
- Adjust the mounted host paths or the Python/venv path inside the image if your environment differs.
- If you prefer absolute host paths, replace "$(pwd)/..." with the full path to your workspace.
- The example uses `run_m2.py` — replace with `run_m.py` or a solver-specific script as needed.

## Experiments & Results
- Experimental outputs are stored under `res/CP`, `res/MIP`, and `res/SMT`.
- Consult `CDMO_report.pdf` for the experimental setup, metrics, and a discussion of findings.

## Notes
- Some helper scripts and runners expect instance paths or environment-specific mounts; adjust `run_docker.sh` and script paths to match your local setup.
- If you want, I can add example commands for each solver using specific instances.

## Contact
For questions or to reproduce experiments, open an issue or contact the repository owner.

