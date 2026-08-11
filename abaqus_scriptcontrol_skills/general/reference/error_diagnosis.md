# Error Diagnosis — Detailed Reference

## Overview

Decision tables for the most common Abaqus Standard/Explicit failures. An agent should:
**read the symptom → match the row → apply the fix → re-run**. Most structural issues
are caused by 5 root causes: increment control, constraints/BCs, material data, mesh
quality, or contact definition.

> 中文提示：先看 `.sta`（收敛过程）和 `.msg`（诊断信息）再判断错误类型；
> 不要盲目减小增量步——先排除边界条件与网格问题。

## Decision Tree (top-down)

```
Job fails or stalls?
│
├─ .lck remains / process hangs → terminate job, check .msg tail, disk space
├─ "Too many attempts" / cutbacks in .sta
│   ├─ Was initialInc already tiny?  → model problem (contact/BC/material), not increment
│   ├─ Contact in model?             → contact diagnosis (below)
│   ├─ nlgeom=ON and buckling?       → add stabilization or use Riks
│   └─ Else                          → reduce initialInc/minInc, check material stiffness
├─ "Zero pivot" / "Numerical singularity"
│   ├─ Rigid body mode?              → add BCs/constraints, check parts are constrained
│   ├─ Under-constrained contact?    → check contact initialization, overclosure tolerance
│   └─ UEL/UMAT tangent wrong?       → verify DDSDDE
├─ "Negative eigenvalue"
│   ├─ First increment, static?      → likely rigid body mode / instability — stabilize or constrain
│   └─ During loading?               → physical instability (buckling); use Riks/static stabilization
├─ "Element distorted excessively"
│   ├─ Large deformation with C3D8R? → refine mesh, use ALE/remeshing, hourglass control
│   └─ Distortion near contact?      → refine contact region, adjust contact algorithm
├─ NaN / overflow in .msg
│   ├─ UMAT/VUMAT?                   → check division by zero, EXP overflow, units (E too big/small)
│   └─ Material?                     → check property magnitudes (MPa vs Pa), density
└─ Job "completes" but results wrong
    ├─ Units mismatch (Pa vs MPa)    → verify material/load magnitudes
    ├─ Mesh too coarse               → mesh convergence (verification.md)
    └─ Wrong BC/load region          → inspect .dat echo of sets
```

## Symptom → Cause → Fix Tables

### A. Convergence Problems (Standard, static steps)

| Symptom in `.sta` / `.msg` | Cause | Fix |
|----------------------------|-------|-----|
| Increment cutbacks from the very first increment | Contact not established / initial overclosure / unstable start | `initialInc` smaller; check contact clearance; add `stabilization`; use `STEP` amplitude |
| Cutbacks later during loading | Load path instability (snap-through), softening material | Use Riks (`StaticRiksStep`) or add viscous stabilization (`stabilizationMethod=...`) |
| 16+ iterations per increment, barely converging | Hard nonlinearity (plasticity, contact) | Reduce `initialInc`; `solutionTechnique=FULL_NEWTON`; check `convertSDI` |
| `MAX PLASTIC STRAIN INCREMENT` exceeded | Large plastic strain per increment | Reduce increment size; check hardening data |
| `TIME INCREMENT IS LESS THAN THE MINIMUM SPECIFIED` | Cannot converge at all | Not an increment problem — fix root cause (contact/BC/material/mesh) |
| `NEGATIVE EIGENVALUE` with rigid body motion | Missing constraint or contact | Fix BCs; do not just reduce increment |
| Divergence in temperature (thermal) | Bad thermal data / delta-T too large | Check `deltmx`; reduce `deltmx`; check thermal properties and units |

### B. Constraints & Boundary Conditions

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ZERO PIVOT` at a node | Node not constrained (rigid body mode) | Add BC or tie/coupling; check coincident nodes |
| `SOLVER PROBLEM - ZERO PIVOT` in contact | Contact surface not generating enough constraint | Check contact pair definition, surface normals, `interference` |
| Over-constrained (pinching) | Too many BCs/constraints | Remove redundant constraints; use MPC properly |
| Movement at supposedly fixed node | BC applied to wrong set/step | Verify set names in `.dat` echo; check BC step activation |
| `NUMERICAL SINGULARITY` after contact opens | Parts separate, lose constraint | Add contact with `allow separation` handled, or tie |

### C. Contact & Interactions

| Symptom | Cause | Fix |
|---------|-------|-----|
| Initial overclosure warnings | Surfaces overlap initially | Adjust positions, or accept small overclosure (`interferenceFit`) |
| Contact never engages | Surface normals wrong | Check element orientation (normals point INTO the slave/master?); flip with `instance.flipNormals` |
| Chattering / oscillations | Contact stiffness too high/low, small increments | Use penalty with reasonable stiffness; increase increment size; add damping |
| Sliding difficulties, no convergence | Friction coefficient too high | Reduce μ or use smooth friction (`frictionCoeff=...`, exponential decay) |
| General contact not applied | Missing general contact assignment | `model.rootAssembly.instances[...]` — assign `InteractionProperty` + `ContactStd`/`ContactExp` on all surfaces |

### D. Mesh & Elements

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ELEMENT DISTORTED EXCESSIVELY` | Extreme deformation on solid elements | Refine; use adaptive remeshing (`ALE`) or C3D10; check element type |
| Hourglassing (check ALLAE) | C3D8R under bending | Switch to C3D8I/C3D20R or add hourglass control |
| Locking (too stiff) | Fully integrated linear elements in bending | Use C3D8R with enhanced hourglass or C3D8I |
| `NEGATIVE JACOBIAN` | Badly inverted elements | Check mesh (invert by `part.verifyMesh()`), refine, avoid high aspect ratio |
| Volumetric locking (plasticity) | C3D8 with incompressible plasticity | Use C3D8R/C3D20R, or reduced-integration hybrid |
| Shear locking | C3D8 in bending | Use incompatible modes (C3D8I) or quadratic |

### E. Material & Units

| Symptom | Cause | Fix |
|---------|-------|-----|
| Displacements absurdly small/large | Unit mismatch (Pa vs MPa, kg/m³ vs tonne/mm³) | Use `scripts/unit_converter.py`; verify all inputs |
| `STRESS LEVELS ARE HIGHER THAN ...` warnings | High stress / singularity | Check load magnitude, stress concentration, mesh |
| NaN early in a UMAT run | Division by zero in subroutine | Add guards; check `SMISES`/`q` zero; check PROPS read |
| Yield never reached | Yield stress too high or units | Check yield stress units (MPa) |
| `TOO MUCH PLASTIC STRAIN` | Material too soft / hardening wrong | Check plastic data (first point plastic strain = 0) |

### F. Explicit Analyses

| Symptom | Cause | Fix |
|---------|-------|-----|
| `TIME INCREMENT IS TOO SMALL` | Stable time step collapsed (elements tiny / material stiff) | Check smallest element; check material (E too high, density too low); use mass scaling carefully |
| Excessive kinetic energy | Loading too fast for quasi-static claim | Slow the load or verify dynamic intent |
| Elements deleted unexpectedly | Damage/failure criterion reached | Intended or not? Check SDV/damage parameters |
| Hourglass energy > 5% internal | Reduced integration elements | Improve mesh, use hourglass control, or fully integrated |

## Fix Recipes (copy-paste)

### Recipe 1 — Static step that refuses to converge

```python
model.StaticStep(
    name='Fix-1',
    previous='Initial',
    nlgeom=ON,
    initialInc=0.001,        # much smaller start
    minInc=1e-08,
    maxInc=0.01,             # cap the growth
    maxNumInc=100000,
    stabilizationMethod=DAMPING_FACTOR,   # add stabilization
    stabilizationMagnitude=0.0002         # then decrease it once converged
)
```

### Recipe 2 — Riks for snap-through / buckling

```python
model.StaticRiksStep(
    name='Riks-1',
    previous='Initial',
    nlgeom=ON,
    initialArcInc=0.01,
    minArcInc=1e-06,
    maxArcInc=0.1,
    maxNumInc=100000
)
```

### Recipe 3 — Contact convergence relief

```python
# Lower initial increment + allow automatic overclosure adjustment
model.StaticStep(name='Contact-Step', previous='Initial',
                 nlgeom=ON, initialInc=0.005, minInc=1e-08, maxInc=0.05,
                 maxNumInc=100000, stabilizationMagnitude=0.0005)

# Contact property: penalty (not augmented Lagrange) for easier convergence
model.ContactProperty(name='IntProp')
model.interactionProperties['IntProp'].TangentialBehavior(formulation=PENALTY,
                                                         frictionCoeff=0.3)
model.interactionProperties['IntProp'].NormalBehavior(allowSeparation=ON)
```

### Recipe 4 — Explicit stability check

```python
# From the ODB after the run (or analytical estimate before):
# stable_time_step ≈ charLength / waveSpeed
# waveSpeed = sqrt((lambda + 2*mu)/rho)  (P-wave)
# If stableDt is tiny: coarsen the finest elements or increase density (mass scaling)
```

## Diagnostic Log Locations Recap

| Where to look | What it tells you |
|---------------|-------------------|
| `Job-1.sta` | Increment-level convergence (cutbacks, iterations) |
| `Job-1.msg` | Per-iteration residuals, eigenvalue info, contact status |
| `Job-1.dat` | Input echo, `***ERROR` blocks, some `***WARNING` |
| `Job-1.log` | Job lifecycle (started/aborted/completed) |
| `Job-1.odb` | Energy diagnostics (ALLIE/ALLAE/ALLKE...) |

## Related

- `headless_execution.md` — where the files live and how to parse them
- `verification.md` — confirm results are physically correct after fixing convergence
- `scripts/inp_checker.py` — catch input problems before submitting
