# DFLUX Welding Example — Cross-Module Task

## Goal

Run a complete **welding thermal analysis** end-to-end: build the model with Python,
apply a Goldak double-ellipsoid moving heat source via the `DFLUX` user subroutine,
run it headless, and verify the thermal cycle.

## What this demonstrates

| Step | Skill used | File |
|------|-----------|------|
| Model/mesh/job scripting | `abaqus_scriptcontrol_skills/general/SKILL.md` | `model_setup.py` |
| Thermal step & BCs | `thermal/SKILL.md` → `reference/transient.md` | `model_setup.py` |
| Moving heat source | `abaqus_subroutine_skills/reference/thermal/dflux_welding.md` | `dflux_welding.f` |
| Headless run & monitoring | `general/reference/headless_execution.md` | `scripts/job_monitor.sh` |
| Result verification | `general/reference/postprocess_odb.md` + `verification.md` | manual |

## Run it

```bash
# 1. Build + submit (model_setup.py also submits and waits)
abaqus cae noGUI=model_setup.py

# 2. Or run steps separately:
abaqus cae noGUI=model_setup.py        # writes Weld-Thermal.inp, submits
scripts/job_monitor.sh Weld-Thermal cpus=4

# 3. Extract results
abaqus python scripts/odb_extract.py Weld-Thermal.odb --field NT --max
```

## Expected results (steel plate 200×50×10 mm, 25 s weld at 4 mm/s)

- Peak temperature 1400–1800 °C along the weld path (above steel melting point ~1500 °C)
- Temperature gradient steep across the heat source (2–3 elements)
- Mid-weld thermal cycle: fast rise, slow cool
- HFL field concentrated on the weld line

## Verification checklist

- [ ] `.sta` completes with no cutback storms
- [ ] Peak NT ≈ 1400–1800 °C (physical)
- [ ] No `TIME INCREMENT IS LESS THAN THE MINIMUM` errors
- [ ] Total heat input ≈ EFF·V·I·t = 0.8·24·180·25 = 86400 J ≈ 8.64e7 N·mm
- [ ] Cool-down continues after the heat source passes

## Extending to residual stress (sequential coupling)

1. Copy the model; switch the material to mechanical (E, ν, α, plasticity)
2. Add `model.Temperature(..., distributionType=FROM_FILE,
   fileName='Weld-Thermal.odb')` in the mechanical step
3. Run the static step (see `thermal/reference/transient.md` sequential coupling)
