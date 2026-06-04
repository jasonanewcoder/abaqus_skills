# Example: Bridge Deck Under Moving Wheel Load (DLOAD)

## Goal

Simulate a moving wheel load traversing a bridge deck using a Python setup script and a DLOAD user subroutine. The DLOAD subroutine applies a Gaussian pressure distribution that moves with time.

## Skills Used

| Module | File | Role |
|--------|------|------|
| Script Control — General | `general/SKILL.md` | Modeling, Material, BCs, Mesh, Job |
| Script Control — Static | `static/SKILL.md` | Step setup (could use dynamic for transient) |
| Subroutine — DLOAD | `reference/load/dload_moving.md` | Moving distributed load |

## Files

- `model_setup.py` — Python script that builds the bridge deck model
- `dload_moving.f` — DLOAD subroutine for moving distributed load

## Quick Start

```bash
# 1. Generate input file
abaqus cae noGUI=model_setup.py

# 2. Run with DLOAD subroutine
abaqus job=Bridge-DLOAD input=Bridge-DLOAD.inp user=dload_moving.f cpus=4

# 3. View results
abaqus viewer database=Bridge-DLOAD.odb
```

## Key Learning Points

1. **DLOAD is called at each integration point** — use totalTime to compute moving load position
2. **Distributed load definition** — `*Dsload` keyword in input file
3. **Python sets up geometry, BCs, mesh** — Fortran provides the specialized loading
4. **Verification** — check that maximum deflection occurs when load is at mid-span

## Expected Results

- Time-varying deflection as load traverses the deck
- Maximum deflection when load is at mid-span
- Reaction forces sum to the applied axle load
