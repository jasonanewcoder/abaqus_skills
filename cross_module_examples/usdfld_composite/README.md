# Example: Plate with Spatially-Varying Elastic Modulus (USDFLD)

## Goal

Simulate a plate where the elastic modulus varies spatially (e.g., functionally graded material) using a USDFLD subroutine. The Python script creates the model, and the USDFLD subroutine defines the spatial field.

## Skills Used

| Module | File | Role |
|--------|------|------|
| Script Control — General | `general/SKILL.md` | Modeling, Material, BCs, Mesh, Job |
| Script Control — Static | `static/SKILL.md` | Step setup |
| Subroutine — USDFLD | `reference/field/usdfld_spatial.md` | Spatially-varying field variable |

## Files

- `model_setup.py` — Python script that builds the model and configures field-variable-dependent material
- `usdfld_spatial.f` — USDFLD subroutine that computes field variable from coordinates

## Quick Start

```bash
# 1. Generate input file
abaqus cae noGUI=model_setup.py

# 2. Run with USDFLD subroutine
abaqus job=FGM-Plate input=FGM-Plate.inp user=usdfld_spatial.f cpus=4

# 3. View results
abaqus viewer database=FGM-Plate.odb
```

## Key Learning Points

1. **USDFLD sets FIELD variables** — accessible in material definitions via field variable index
2. **Material properties depend on field** — elastic modulus varies with FIELD(1)
3. **Python sets up the dependency** — `material.Elastic(..., fieldVariableNumber=1)`
4. **Verification** — check that stress/strain distribution reflects the graded stiffness

## Expected Results

- Stiffer region (high E) shows lower strain under same load
- Softer region shows higher strain
- Smooth transition between regions
