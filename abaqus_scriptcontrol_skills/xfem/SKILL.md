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

**Detailed Documentation:** [`reference/crack.md`](reference/crack.md)

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

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
