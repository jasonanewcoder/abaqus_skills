# Composite Failure Analysis — Detailed Reference

## Overview

Composite failure analysis uses damage initiation criteria (Hashin, Puck, LaRC) and damage evolution laws to predict laminate failure and progressive damage. This is essential for designing safe and weight-efficient composite structures.

## Failure Criteria Comparison

| Criteria | Modes Distinguished | Input Complexity | Accuracy |
|----------|-------------------|------------------|----------|
| Hashin | Fiber tension/compression, Matrix tension/compression | Medium (strength values) | Good for initial sizing |
| Puck | Fiber + 3 matrix modes (angle-dependent) | High (requires fracture angles) | Better for matrix failure |
| LaRC03/04 | Fiber + matrix with in-situ effects | High | Best for academic research |

## Hashin Failure Criteria

### Fiber Failure (σ₁₁ > 0, tension)
```
(σ₁₁ / X_T)² + α(τ₁₂ / S_L)² ≥ 1
```

### Fiber Failure (σ₁₁ < 0, compression)
```
|σ₁₁| ≥ X_C
```

### Matrix Failure (σ₂₂ > 0, tension)
```
(σ₂₂ / Y_T)² + (τ₁₂ / S_L)² ≥ 1
```

### Matrix Failure (σ₂₂ < 0, compression)
```
(σ₂₂ / 2S_T)² + [(Y_C / 2S_T)² - 1](σ₂₂ / Y_C) + (τ₁₂ / S_L)² ≥ 1
```

| Symbol | Meaning |
|--------|---------|
| X_T | Longitudinal tensile strength (MPa) |
| X_C | Longitudinal compressive strength (MPa) |
| Y_T | Transverse tensile strength (MPa) |
| Y_C | Transverse compressive strength (MPa) |
| S_L | Longitudinal shear strength (MPa) |
| S_T | Transverse shear strength (MPa) |

## Complete Script Template — Hashin Failure

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Composite Failure Analysis with Hashin Criteria
Description: Progressive damage analysis of composite laminate
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry (same as layup example)
plate_length = 200.0
plate_width = 100.0

# Material: T300/5208 Carbon/Epoxy (per ply)
E1 = 135000.0    # MPa
E2 = 9500.0      # MPa
nu12 = 0.30
G12 = 4900.0     # MPa
G13 = 4900.0     # MPa
G23 = 3200.0     # MPa

# Strengths for Hashin
Xt = 1500.0      # MPa, longitudinal tensile
Xc = 1200.0      # MPa, longitudinal compressive
Yt = 50.0        # MPa, transverse tensile
Yc = 200.0       # MPa, transverse compressive
Sl = 85.0        # MPa, longitudinal shear
St = 85.0        # MPa, transverse shear

# Fracture energies (for damage evolution)
G_ft = 80.0      # N/mm, fiber tensile fracture energy
G_fc = 60.0      # N/mm, fiber compressive fracture energy
G_mt = 1.0       # N/mm, matrix tensile fracture energy
G_mc = 2.0       # N/mm, matrix compressive fracture energy

ply_thickness = 0.125  # mm
layup_angles = [0, 90, 45, -45, -45, 45, 90, 0]

# ========== 2. Create Model ==========
model_name = 'Composite-Failure'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create shell part
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = model.Part(name='Laminate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseShell(sketch=sketch)
del model.sketches['__profile__']

# ========== 3. Material with Hashin Damage ==========
material = model.Material(name='T300-5208')

# Elastic (LAMINA)
material.Elastic(
    type=LAMINA,
    table=((E1, E2, nu12, G12, G13, G23),)
)

# Hashin damage initiation
material.HashinDamageInitiation(
    table=((
        Xt,   # Longitudinal tensile strength
        Xc,   # Longitudinal compressive strength
        Yt,   # Transverse tensile strength
        Yc,   # Transverse compressive strength
        Sl,   # Longitudinal shear strength
        St,   # Transverse shear strength
    ),)
)

# Damage evolution (energy-based, separate for each mode)
material.hashinDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    mixedModeBehavior=POWER_LAW,
    power=1.0,
    table=((G_ft, G_fc, G_mt, G_mc),)
)

# Viscous regularization for convergence
material.hashinDamageInitiation.DamageStabilizationCohesion(
    viscosity=1e-05  # Smaller = less artificial but harder to converge
)

# Section with composite layup
face = part.faces[0]
layup_region = regionToolset.Region(faces=face)

composite_layup = part.CompositeLayup(
    name='CompositeLayup-1',
    description='[0/90/±45]s with Hashin failure',
    elementType=SHELL,
    symmetric=False
)

for i, angle in enumerate(layup_angles):
    composite_layup.CompositePly(
        region=layup_region,
        material='T300-5208',
        thicknessType=SPECIFY_THICKNESS,
        thickness=ply_thickness,
        orientationType=SPECIFY_ORIENT,
        orientationValue=angle,
        axis=AXIS_3,
        angle=0.0,
        numIntPoints=3
    )

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Laminate-1', part=part, dependent=ON)

# ========== 5. Step (Nonlinear for progressive damage) ==========
model.StaticStep(
    name='Failure-Step',
    previous='Initial',
    nlgeom=ON,
    initialInc=0.05,
    minInc=1e-10,
    maxInc=0.1,
    maxNumInc=10000
)

model.FieldOutputRequest(
    name='Failure-Output',
    createStepName='Failure-Step',
    variables=(
        'S', 'E', 'U', 'RF',
        'HSNFTCRT',    # Hashin fiber tension criterion
        'HSNFCCRT',    # Hashin fiber compression criterion
        'HSNMTCRT',    # Hashin matrix tension criterion
        'HSNMCCRT',    # Hashin matrix compression criterion
        'DAMAGEFT',    # Fiber tensile damage variable
        'DAMAGEFC',    # Fiber compressive damage variable
        'DAMAGEMT',    # Matrix tensile damage variable
        'DAMAGEMC',    # Matrix compressive damage variable
        'STATUS'       # Element status (0=failed, 1=active)
    ),
    frequency=10
)

# ========== 6. Boundary Conditions ==========
# Clamp one edge
clamped_edge = instance.edges.findAt(((0.0, plate_width/2, 0.0),))
clamped_region = assembly.Set(name='Clamped', edges=clamped_edge)
model.EncastreBC(name='BC-Clamped', createStepName='Initial', region=clamped_region)

# ========== 7. Load (Displacement Control for Post-Failure) ==========
loaded_edge = instance.edges.findAt(
    ((plate_length, plate_width/2, 0.0),)
)
loaded_region = assembly.Set(name='Loaded-Edge', edges=loaded_edge)
model.DisplacementBC(
    name='BC-Displacement',
    createStepName='Failure-Step',
    region=loaded_region,
    u3=-5.0  # 5 mm downward displacement
)

# ========== 8. Mesh ==========
face_region = part.faces
part.setMeshControls(
    regions=face_region, elemShape=QUAD, technique=STRUCTURED
)
part.seedPart(size=5.0)

elem_type = mesh.ElemType(
    elemCode=S4R,
    elemLibrary=STANDARD
)
part.setElementType(regions=(face_region,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 9. Job Submission ==========
job_name = 'Composite-Failure-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=8)
job.submit()
job.waitForCompletion()

print("Composite failure analysis completed!")
```

## Interpreting Failure Indices

```python
from odbAccess import openOdb

odb = openOdb(path='Composite-Failure-Job.odb')
last_frame = odb.steps['Failure-Step'].frames[-1]

# Hashin criteria (1.0 = failure initiation)
criteria_map = {
    'HSNFTCRT': 'Fiber Tension',
    'HSNFCCRT': 'Fiber Compression',
    'HSNMTCRT': 'Matrix Tension',
    'HSNMCCRT': 'Matrix Compression',
}

for field_name, description in criteria_map.items():
    field = last_frame.fieldOutputs[field_name]
    max_value = max(v.data for v in field.values)
    if max_value >= 1.0:
        print(f"⚠️  {description} FAILURE: max criterion = {max_value:.3f}")
    else:
        print(f"✓  {description}: max criterion = {max_value:.3f}")

# Damage variables (0=undamaged, 1=fully damaged)
damage_map = {
    'DAMAGEFT': 'Fiber Tensile Damage',
    'DAMAGEFC': 'Fiber Compressive Damage',
    'DAMAGEMT': 'Matrix Tensile Damage',
    'DAMAGEMC': 'Matrix Compressive Damage',
}

for field_name, description in damage_map.items():
    field = last_frame.fieldOutputs[field_name]
    max_damage = max(v.data for v in field.values)
    if max_damage > 0.0:
        print(f"  {description}: max = {max_damage:.3f}")

odb.close()
```

## Typical Composite Strength Values (MPa)

| Material | X_T | X_C | Y_T | Y_C | S_L |
|----------|-----|-----|-----|-----|-----|
| T300/5208 (CFRP) | 1500 | 1200 | 50 | 200 | 85 |
| AS4/3501-6 (CFRP) | 2100 | 1750 | 60 | 250 | 90 |
| IM7/8552 (CFRP) | 2500 | 1700 | 70 | 280 | 100 |
| E-glass/Epoxy | 1000 | 600 | 30 | 120 | 50 |
| S-glass/Epoxy | 1600 | 700 | 45 | 150 | 65 |

## Progressive Damage Analysis Tips

1. **Use displacement control** — load control will snap through at failure, missing post-failure response
2. **Mesh size sensitivity** — fracture energy-based evolution reduces mesh dependency (characteristic length is used internally)
3. **Viscous regularization** — start with 1e-4, decrease to 1e-5 if convergence allows; check that viscous energy < 5% of total
4. **Monitor each mode** — fiber failure is typically catastrophic; matrix failure may be progressive
5. **Section points** — use ≥ 3 integration points per ply to capture nonlinear stress distribution

## Puck Failure Criterion (Advanced)

```python
# Puck criterion if material data available
material.PuckDamageInitiation(
    table=((
        Xt, Xc,           # Fiber strengths
        0.35, 0.30,       # p_perp_parallel_t, p_perp_parallel_c (slope parameters)
        Yt,               # Transverse tensile strength
        Yc,               # Transverse compressive strength
        Sl,               # In-plane shear strength
        53.0,             # Fracture angle in pure compression (degrees)
    ),)
)
```

## Verification Checklist

- [ ] Failure indices < 1.0 at limit load (no failure at design load)
- [ ] First-ply-failure load is identified
- [ ] Damage evolution produces physically reasonable load drop
- [ ] Viscous energy is small fraction of total energy (< 5%)
- [ ] Failed mode matches expected behavior (fiber vs. matrix)
- [ ] Mesh refinement study confirms results are mesh-converged

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| No failure even at high load | Missing Hashin material definition | Add HashinDamageInitiation |
| Job crashes at failure onset | Unstable damage propagation | Add viscous regularization (1e-4) |
| All elements fail instantly | Too-large load/displacement step | Reduce initial increment |
| Wrong failure mode predicted | Incorrect strength values | Verify X_T, X_C, Y_T, Y_C, S_L |
