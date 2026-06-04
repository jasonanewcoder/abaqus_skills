# Composite Laminate Layup Definition — Detailed Reference

## Overview

Composite material analysis in Abaqus uses shell or continuum shell elements with layered section definitions. Each ply has its own material, thickness, and fiber orientation. Classical Laminate Theory (CLT) calculates the coupled stiffness response.

## Applicable Scenarios

- Aerospace structures (wing skins, fuselage panels)
- Wind turbine blades
- Automotive body panels (carbon fiber)
- Marine hulls
- Sporting goods (bicycle frames, tennis rackets)

## Theoretical Foundation

### Classical Laminate Theory (CLT)

The laminate constitutive relation:

```
[N]   [A  B] [ε⁰]
[M] = [B  D] [κ ]
```

| Matrix | Meaning |
|--------|---------|
| A | Extensional stiffness (in-plane) |
| B | Coupling stiffness (extension-bending) |
| D | Bending stiffness |
| N | Force resultants (N/mm) |
| M | Moment resultants (N·mm/mm) |
| ε⁰ | Mid-plane strains |
| κ | Curvatures |

### Orthotropic Lamina Properties

Each ply (lamina) requires orthotropic elastic constants:

| Constant | Meaning | Typical CFRP Values |
|----------|---------|---------------------|
| E₁ | Longitudinal modulus | 120-180 GPa |
| E₂ | Transverse modulus | 8-12 GPa |
| ν₁₂ | Major Poisson's ratio | 0.25-0.35 |
| G₁₂ | In-plane shear modulus | 4-6 GPa |
| G₁₃ | Transverse shear modulus | 4-6 GPa |
| G₂₃ | Transverse shear modulus | 3-5 GPa |

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Composite Laminate Static Analysis
Description: Multi-layer composite plate with symmetric layup under bending
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry
plate_length = 200.0   # mm
plate_width = 100.0    # mm

# Material: T300/5208 Carbon/Epoxy (per ply)
E1 = 135000.0          # MPa, longitudinal
E2 = 9500.0            # MPa, transverse
nu12 = 0.30
G12 = 4900.0           # MPa
G13 = 4900.0           # MPa
G23 = 3200.0           # MPa
ply_thickness = 0.125  # mm

# Layup: [0/90/±45]s (8 plies, symmetric)
# Odd plies listed from bottom to top
layup_angles = [0, 90, 45, -45, -45, 45, 90, 0]

# Loading
pressure_load = 0.1    # MPa

# ========== 2. Create Model ==========
model_name = 'Composite-Laminate'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create shell planar part (shells use 2D geometry)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = model.Part(
    name='Laminate', dimensionality=THREE_D, type=DEFORMABLE_BODY
)
part.BaseShell(sketch=sketch)
del model.sketches['__profile__']

# ========== 3. Material Definition ==========
# Orthotropic lamina material
material = model.Material(name='T300-5208')
material.Elastic(
    type=LAMINA,
    table=((E1, E2, nu12, G12, G13, G23),)
)

# Density
rho = 1.58e-09  # tonne/mm³ (1580 kg/m³)
material.Density(table=((rho,),))

# ========== 4. Composite Layup ==========
# Create composite layup
composite_layup = part.CompositeLayup(
    name='CompositeLayup-1',
    description='[0/90/±45]s symmetric laminate',
    elementType=SHELL,
    symmetric=False  # We'll define all plies explicitly
)

# Select shell face for layup
face = part.faces[0]
region = part.Set(name='Laminate-Region', faces=face)
layup_region = regionToolset.Region(faces=face)

# Define each ply
for i, angle in enumerate(layup_angles):
    ply_name = f'Ply-{i+1}_{angle}deg'
    composite_layup.CompositePly(
        region=layup_region,
        material='T300-5208',
        thicknessType=SPECIFY_THICKNESS,
        thickness=ply_thickness,
        orientationType=SPECIFY_ORIENT,
        orientationValue=angle,
        axis=AXIS_3,         # Normal direction
        angle=0.0,           # Additional rotation
        numIntPoints=3       # Integration points through ply thickness
    )

# Alternatively, use reference surface definition:
# part.compositeLayups['CompositeLayup-1'].ReferenceSurface(
#     surface=layup_region
# )

# ========== 5. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Laminate-1', part=part, dependent=ON)

# ========== 6. Step ==========
model.StaticStep(
    name='Bending-Step',
    previous='Initial',
    nlgeom=OFF,
    initialInc=1.0,
    maxInc=1.0
)

model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Bending-Step',
    variables=('S', 'E', 'U', 'RF', 'MISES'),
    frequency=1
)

# ========== 7. Boundary Conditions ==========
# Simply supported: fix edges
# Fix left edge (U1=U2=U3=0)
left_edge = instance.edges.findAt(((0.0, plate_width/2, 0.0),))
left_region = assembly.Set(name='Left-Edge', edges=left_edge)
model.DisplacementBC(
    name='BC-Left',
    createStepName='Initial',
    region=left_region,
    u1=0.0, u2=0.0, u3=0.0
)

# Fix right edge (U2=U3=0, allow U1)
right_edge = instance.edges.findAt(
    ((plate_length, plate_width/2, 0.0),)
)
right_region = assembly.Set(name='Right-Edge', edges=right_edge)
model.DisplacementBC(
    name='BC-Right',
    createStepName='Initial',
    region=right_region,
    u2=0.0, u3=0.0
)

# ========== 8. Load ==========
# Uniform pressure on top surface
top_surface = assembly.Surface(
    name='Top-Surface',
    side1Faces=instance.faces
)
model.Pressure(
    name='Bending-Pressure',
    createStepName='Bending-Step',
    region=top_surface,
    magnitude=pressure_load
)

# ========== 9. Mesh ==========
face_region = part.faces
part.setMeshControls(
    regions=face_region,
    elemShape=QUAD,
    technique=STRUCTURED
)
part.seedPart(size=5.0)

# Shell element type for composites
elem_type = mesh.ElemType(
    elemCode=S4R,
    elemLibrary=STANDARD,
    hourglassControl=DEFAULT
)
part.setElementType(regions=(face_region,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 10. Job Submission ==========
job_name = 'Composite-Laminate-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit()
job.waitForCompletion()

print("Composite laminate analysis completed!")
```

## Common Layup Configurations

```python
# 1. Symmetric layup (no B matrix coupling) - defined as half
symmetric_layup = [(0, 0.25), (90, 0.25), (45, 0.25), (-45, 0.25)]

# 2. Quasi-isotropic layup [0/±45/90]s
quasi_iso = [(0, 0.125), (45, 0.125), (-45, 0.125), (90, 0.125)]

# 3. Cross-ply [0/90]ns
cross_ply_4 = [(0, 0.25), (90, 0.25)] * 2  # 4 plies

# 4. Angle-ply [±θ]ns
angle_ply = [(30, 0.25), (-30, 0.25)] * 3  # 6 plies

# 5. Hybrid (mixed materials)
hybrid_layup = [
    (0, 0.3, 'CFRP-T800'),      # Carbon fiber outer plies
    (45, 0.3, 'CFRP-T800'),
    (0, 0.5, 'GFRP-Eglass'),    # Glass fiber core for cost/toughness
    (45, 0.3, 'CFRP-T800'),
    (0, 0.3, 'CFRP-T800'),
]
```

## Creating Layup Programmatically

```python
def create_layup(part, region, layup_definition, material_name, default_thickness=0.125):
    """
    Create composite layup from list of (angle, thickness) or (angle, thickness, material) tuples.

    Args:
        part: Abaqus part object
        region: Region for layup application
        layup_definition: List of (angle, thickness) or (angle, thickness, material_name)
        material_name: Default material name
        default_thickness: Default ply thickness (mm)
    """
    composite_layup = part.CompositeLayup(
        name='CompositeLayup-1',
        description='Programmatically defined layup',
        elementType=SHELL,
        symmetric=False
    )

    for i, ply_spec in enumerate(layup_definition):
        if len(ply_spec) == 2:
            angle, thickness = ply_spec
            mat_name = material_name
        else:
            angle, thickness, mat_name = ply_spec

        ply_label = f'Ply-{i+1}_{angle}deg'
        composite_layup.CompositePly(
            region=region,
            material=mat_name,
            thicknessType=SPECIFY_THICKNESS,
            thickness=thickness,
            orientationType=SPECIFY_ORIENT,
            orientationValue=angle,
            axis=AXIS_3,
            angle=0.0,
            numIntPoints=3
        )

    return composite_layup

# Usage
layup_def = [(0, 0.125), (90, 0.125), (45, 0.125), (-45, 0.125)] * 2
create_layup(part, layup_region, layup_def, 'T300-5208')
```

## Post-Processing — Per-Ply Results

```python
from odbAccess import openOdb

odb = openOdb(path='Composite-Laminate-Job.odb')
last_frame = odb.steps['Bending-Step'].frames[-1]

# Access stress for specific ply
stress_field = last_frame.fieldOutputs['S']

# Each integration point corresponds to a ply
# Use sectionPoint to filter by ply
for ply_idx in range(len(layup_angles)):
    # Access stress at specific section point
    sp = stress_field.getSubset(sectionPoint=ply_idx + 1)
    # sp contains stress for this ply only
    print(f"Ply {ply_idx+1} ({layup_angles[ply_idx]}°): "
          f"max S11 = {max(v.data[0] for v in sp.values):.1f} MPa")

odb.close()
```

## Ply Stacking Sequence Best Practices

| Rule | Reason | Violation Effect |
|------|--------|-----------------|
| Symmetric layup (B=0) | Eliminates curing warpage | Thermal distortion |
| Balanced layup (+θ = -θ count) | Eliminates shear coupling | Unexpected twist under tension |
| ≤ 4 plies of same angle adjacent | Prevent matrix cracking | Transverse micro-cracking |
| ±45° outer plies | Improve damage tolerance | Delamination susceptibility |
| 10% rule (min each direction) | Ensure multi-directional strength | Poisson's effect cracking |

## Verification Checklist

- [ ] Material properties are in LAMINA engineering constants format
- [ ] Ply angles are defined relative to the part coordinate system
- [ ] Numerical integration points per ply ≥ 3 (for nonlinear stress distribution)
- [ ] Symmetric layup for flat panels (prevents curing distortion)
- [ ] Mesh is aligned with primary fiber direction where possible

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Layup not visible in viewer | Section assignment not done | Assign composite layup to region |
| Zero transverse stress | Wrong LAMINA definition order | Check: (E1, E2, nu12, G12, G13, G23) |
| Unrealistic coupling stiffness | Asymmetric layup not intentional | Use symmetric layup or accept B matrix |
| Missing failure indices | No failure criteria defined | Add Hashin or other criteria (see failure_analysis.md) |
