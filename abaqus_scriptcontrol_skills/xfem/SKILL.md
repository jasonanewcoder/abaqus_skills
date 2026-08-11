---
name: abaqus-script-control-xfem
description: >-
  Abaqus XFEM fracture analysis: crack initiation and propagation without
  remeshing (MAXPS/MAXPE/QUADS damage initiation, energy/displacement damage
  evolution), plus VCCT crack growth along predefined interfaces (delamination,
  adhesive) with energy release rates and B-K criterion. Use when the task
  mentions: XFEM, crack analysis, crack propagation, crack initiation, fracture,
  damage evolution, VCCT, delamination, stress intensity factor, 裂纹分析,
  裂纹扩展, 断裂分析, 分层. Requires abaqus-script-control-general as foundation.
version: "1.1"
capabilities:
  - xfem_crack_initiation
  - crack_propagation
  - damage_evolution
  - fracture_energy_analysis
triggers:
  - "XFEM"
  - "crack analysis"
  - "crack propagation"
  - "fracture"
  - "damage evolution"
  - "裂纹分析"
  - "裂纹扩展"
  - "断裂分析"
constraints:
  - "Requires general/SKILL.md and static/SKILL.md as foundation"
  - "Reference docs: crack_initiation.md (XFEM) + vcct_fracture.md (VCCT)"
  - "XFEM requires careful damage initiation criteria selection"
---

# Abaqus XFEM Crack Analysis Skills

## Overview

This skill module provides specialized skills for Abaqus Extended Finite Element Method (XFEM) for simulating crack initiation and propagation. XFEM technology allows cracks to propagate through the mesh without requiring the mesh to conform to the crack surface.

## Skills List

### 1. XFEM Crack Analysis (`skill_xfem_crack`)

Simulate crack initiation and propagation using the Extended Finite Element Method.

**Applicable Scenarios:**
- Unknown crack initiation location
- Complex crack propagation paths
- Dynamic crack propagation
- Avoid complex crack meshing

**Code Snippet:**

```python
# Create XFEM crack domain
xfem_region = regionToolset.Region(cells=part.cells)

mdb.models[model_name].XFEMCrack(
    name='Crack-1',
    crackDomain=xfem_region,
    crackLocation=xfem_region,
    allowSelfHealing=OFF
)

# Define damage initiation criteria
material.MaxpsDamageInitiation(
    table=((crack_initiation_stress,),),
    definition=VALUE
)

# Damage evolution
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    table=((fracture_energy,),)
)
```

---

## Quick Reference

### Damage Initiation Criteria

| Criteria | Applicable Scenario |
|----------|---------------------|
| MaxpsDamage | Brittle fracture, tension-dominated |
| MaxpeDamage | Ductile materials |
| QuadsDamage | Shear fracture |

### Damage Evolution Types

- ENERGY (Based on fracture energy)
- DISPLACEMENT (Based on displacement)

## Detailed Reference

- [Crack Initiation & Propagation](reference/crack_initiation.md) — MAXPS/MAXPE/QUADS criteria, energy/displacement-based damage evolution, initial defects, convergence troubleshooting
- [VCCT Crack Growth](reference/vcct_fracture.md) — pre-defined crack paths, energy release rates, B-K mixed-mode criterion, delamination

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
