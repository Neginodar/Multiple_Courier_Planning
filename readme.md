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

Docker (build and run):
1. Build the image:

```bash
docker build -t cdmo_final .
```

2. Use the included script (edit paths inside `run_docker.sh` if needed):

```bash
./run_docker.sh inst01.dzn CP
```

## Experiments & Results
- Experimental outputs are stored under `res/CP`, `res/MIP`, and `res/SMT`.
- Consult `CDMO_report.pdf` for the experimental setup, metrics, and a discussion of findings.

## Notes
- Some helper scripts and runners expect instance paths or environment-specific mounts; adjust `run_docker.sh` and script paths to match your local setup.
- If you want, I can add example commands for each solver using specific instances.

## Contact
For questions or to reproduce experiments, open an issue or contact the repository owner.

