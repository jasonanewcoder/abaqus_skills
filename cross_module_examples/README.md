# Cross-Module Integration Examples

This directory contains examples that combine both **script control** (Python) and **user subroutine** (Fortran) skills — the typical real-world engineering workflow where a Python script sets up the Abaqus model and one or more Fortran subroutines provide custom physics.

## Examples

| Example | Modules Combined | Description |
|---------|-----------------|-------------|
| [`umat_cantilever_beam/`](umat_cantilever_beam/) | `general/` + `static/` + UMAT | Cantilever beam with a custom linear elastic UMAT — demonstrates the complete Python+Fortran workflow |
| [`dload_moving_load/`](dload_moving_load/) | `general/` + `static/` + DLOAD | Bridge deck under moving wheel load — demonstrates coordinated DLOAD subroutine with Python model setup |
| [`usdfld_composite/`](usdfld_composite/) | `general/` + `static/` + USDFLD | Plate with spatially-varying elastic modulus — demonstrates field variable subroutine + Python model |

## How to Use

Each example contains:
- `README.md` — step-by-step instructions
- `model_setup.py` — Python script that creates the Abaqus model
- `<subroutine>.f` — Fortran user subroutine source code

### Workflow

```bash
# 1. Run the Python script in Abaqus CAE or with abaqus python
abaqus cae noGUI=model_setup.py

# 2. The script generates an input file (.inp)
# 3. Submit with the user subroutine
abaqus job=job_name user=subroutine.f cpus=4

# 4. View results in Abaqus/Viewer
abaqus viewer database=job_name.odb
```
