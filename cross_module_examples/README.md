# Cross-Module Integration Examples

This directory contains examples that combine both **script control** (Python) and **user subroutine** (Fortran) skills — the typical real-world engineering workflow where a Python script sets up the Abaqus model and one or more Fortran subroutines provide custom physics.

## Examples

| Example | Modules Combined | Description |
|---------|-----------------|-------------|
| [`umat_cantilever_beam/`](umat_cantilever_beam/) | `general/` + `static/` + UMAT | Cantilever beam with a custom linear elastic UMAT — demonstrates the complete Python+Fortran workflow |
| [`dload_moving_load/`](dload_moving_load/) | `general/` + `static/` + DLOAD | Bridge deck under moving wheel load — demonstrates coordinated DLOAD subroutine with Python model setup |
| [`usdfld_composite/`](usdfld_composite/) | `general/` + `static/` + USDFLD | Plate with spatially-varying elastic modulus — demonstrates field variable subroutine + Python model |
| [`dflux_welding/`](dflux_welding/) | `general/` + `thermal/` + DFLUX + agent loop | **Full agent-loop task**: welding thermal analysis with a Goldak double-ellipsoid heat source — build → run → verify peak temperature |

## How to Use

Each example contains:
- `README.md` — step-by-step instructions
- `model_setup.py` — Python script that creates the Abaqus model
- `<subroutine>.f` — Fortran user subroutine source code

### Workflow

```bash
# 1. Run the Python script in Abaqus CAE (noGUI) — it also submits the job
abaqus cae noGUI=model_setup.py

# 2. Or run the steps separately:
python3 scripts/../../inp_checker.py Job-1.inp          # static check
scripts/../../job_monitor.sh Job-1 cpus=4               # submit + monitor

# 3. Extract results headlessly
abaqus python scripts/odb_extract.py Job-1.odb --field U --max

# 4. View results interactively (optional)
abaqus viewer database=job_name.odb
```
