# Example: Cantilever Beam with Custom UMAT

## Goal

Demonstrate the complete Python + Fortran workflow: a Python script creates the model and submits the job with a custom linear elastic UMAT subroutine.

## Skills Used

| Module | File | Role |
|--------|------|------|
| Script Control — General | `general/SKILL.md` | Modeling, Material, BCs, Mesh, Job |
| Script Control — Static | `static/SKILL.md` | Linear static step setup |
| Subroutine — UMAT | `reference/material/umat_elastic.md` | Custom elastic material |

## Files

- `model_setup.py` — Python script that builds the model and submits the job
- `umat_elastic.f` — Linear elastic UMAT subroutine (see subroutine reference)

## Quick Start

```bash
# Run the Python script
abaqus cae noGUI=model_setup.py

# Or submit directly with the subroutine
abaqus job=Cantilever-UMAT input=Cantilever-UMAT.inp user=umat_elastic.f cpus=4

# View results
abaqus viewer database=Cantilever-UMAT.odb
```

## Key Learning Points

1. **`*User Material` keyword** — how the Python script defines material constants that are read by the UMAT via `PROPS` array
2. **`*Depvar`** — must match `NSTATV` in the UMAT
3. **Job submission with subroutine** — `userSubroutine` parameter in `mdb.Job()`
4. **Verification** — compare UMAT results with Abaqus built-in elastic material

## Expected Results

- Maximum tip deflection: ~2.86 mm (matches beam theory)
- Maximum bending stress: ~30 MPa
- Results identical to Abaqus built-in elastic material
