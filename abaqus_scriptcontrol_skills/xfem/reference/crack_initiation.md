# XFEM Crack Initiation & Propagation — Detailed Reference

## Overview

The eXtended Finite Element Method (XFEM) in Abaqus enables crack simulation without requiring the mesh to conform to crack geometry. Cracks can propagate through elements, with enrichment functions capturing the displacement discontinuity.

## Applicable Scenarios

- Unknown crack initiation location
- Complex, branching crack paths
- Dynamic crack propagation
- Multi-crack interaction
- Avoiding remeshing for crack growth

## Theoretical Foundation

### XFEM Displacement Approximation

```
u(x) = Σ N_i(x) u_i + Σ N_j(x) H(x) a_j + Σ N_k(x) Σ F_α(x) b_k^α
```

- First term: standard FEM displacement
- Second term: Heaviside enrichment (crack surface discontinuity)
- Third term: crack-tip enrichment (asymptotic near-tip fields)

### Damage Initiation Criteria

| Criteria | Type | When to Use |
|----------|------|-------------|
| MAXPS | Maximum principal stress | Brittle fracture, tension-dominated |
| MAXPE | Maximum principal strain | Ductile materials |
| QUADS | Quadratic principal stress | Mixed-mode brittle |
| MAXS | Maximum nominal stress (traction-separation) | Cohesive zone modeling |
| QUADE | Quadratic nominal strain | Mixed-mode cohesive |

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: XFEM Crack Analysis
Description: Crack initiation and propagation using XFEM with MAXPS damage
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset

# ========== 1. Parameter Definition ==========
# Geometry
plate_length = 100.0   # mm
plate_width = 50.0     # mm
plate_thickness = 2.0  # mm

# Hole (stress raiser for crack initiation)
hole_radius = 5.0      # mm
hole_x = plate_length / 4.0
hole_y = plate_width / 2.0

# Material (brittle)
E = 210000.0           # MPa
nu = 0.3

# Damage initiation (MAXPS — maximum principal stress)
crack_initiation_stress = 400.0  # MPa

# Damage evolution (energy-based)
fracture_energy = 50.0  # N/mm (kJ/m²)

# Loading
displacement_max = 2.0  # mm

# ========== 2. Create Model ==========
model_name = 'XFEM-Crack-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create plate with hole
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
# Draw hole
sketch.CircleByCenterPerimeter(
    center=(hole_x, hole_y), point1=(hole_x + hole_radius, hole_y)
)
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del model.sketches['__profile__']

# ========== 3. Material with XFEM Damage ==========
material = model.Material(name='Brittle-Steel')
material.Elastic(table=((E, nu),))

# MAXPS damage initiation
material.MaxpsDamageInitiation(
    table=((crack_initiation_stress,),),  # MPa
    definition=VALUE,
    tolerance=0.05,
    frequency=1
)

# Damage evolution (energy-based, linear softening)
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    mixedModeBehavior=POWER_LAW,
    power=1.0,
    table=((fracture_energy,),)
)

# Stabilization for convergence
material.maxpsDamageInitiation.DamageStabilizationCohesion(
    viscosity=1e-05
)

# Section
section = model.HomogeneousSolidSection(name='Section-1', material='Brittle-Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 5. Define XFEM Crack Domain ==========
# Select all cells as potential crack domain
crack_cells = instance.cells
xfem_region = regionToolset.Region(cells=crack_cells)

# Create XFEM crack
model.XFEMCrack(
    name='Crack-1',
    crackDomain=xfem_region,
    crackLocation=xfem_region,
    allowSelfHealing=OFF,
    interaction=ON,
    contact=OFF
)

# ========== 6. Step (Nonlinear with XFEM) ==========
model.StaticStep(
    name='Crack-Propagation',
    previous='Initial',
    description='XFEM crack propagation analysis',
    timePeriod=1.0,
    initialInc=0.01,
    minInc=1e-10,
    maxInc=0.05,
    maxNumInc=10000,
    nlgeom=ON,
    amplitude=RAMP,
    stabilizationMethod=DAMPING_FACTOR,
    stabilizationMagnitude=0.0002
)

# Field output
model.FieldOutputRequest(
    name='XFEM-Output',
    createStepName='Crack-Propagation',
    variables=(
        'S', 'E', 'U', 'RF',
        'PHILSM',     # Level set: signed distance to crack
        'STATUSXFEM',  # Element status (0=cracked, 1=uncracked)
        'ENRRTXFEM'   # Crack tip enrichment radius
    ),
    frequency=1
)

# ========== 7. Boundary Conditions ==========
# Fix left edge
left_edge = instance.faces.findAt(((0.0, plate_width/2, plate_thickness/2),))
left_region = assembly.Set(name='Fixed-End', faces=left_edge)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=left_region)

# ========== 8. Load (Displacement-controlled) ==========
# Apply displacement on right edge
right_edge = instance.faces.findAt(
    ((plate_length, plate_width/2, plate_thickness/2),)
)
right_region = assembly.Set(name='Loaded-End', faces=right_edge)
model.DisplacementBC(
    name='BC-Displacement',
    createStepName='Crack-Propagation',
    region=right_region,
    u1=displacement_max,
    u2=0.0,
    u3=0.0
)

# ========== 9. Mesh ==========
all_cells = part.cells

# Partition around hole for better mesh quality
# (simplified — in practice, create radial partitions around the hole)

# Mesh with refinement near expected crack path
part.setMeshControls(
    regions=all_cells,
    elemShape=TET,        # Tetrahedral for complex geometry
    technique=FREE,
    algorithm=ADVANCING_FRONT
)

# Global seeds
part.seedPart(size=3.0, deviationFactor=0.1, minSizeFactor=0.1)

# Local refinement near hole
hole_edges = part.edges.getByBoundingCylinder(
    (hole_x, hole_y, 0.0), (hole_x, hole_y, plate_thickness), hole_radius * 1.5
)
if hole_edges:
    part.seedEdgeBySize(edges=hole_edges, size=1.0)

# Element type
elem_type = mesh.ElemType(
    elemCode=C3D10,       # Quadratic tet for XFEM
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

print(f"Mesh: {len(part.elements)} elements, {len(part.nodes)} nodes")

# ========== 10. Job Submission ==========
job_name = 'XFEM-Crack-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=8)
job.submit()
job.waitForCompletion()

print("XFEM crack analysis completed!")
```

## Damage Evolution Options

```python
# 1. Energy-based (linear softening)
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    table=((fracture_energy,),)
)

# 2. Energy-based (exponential softening)
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=EXPONENTIAL,
    table=((fracture_energy,),)
)

# 3. Displacement-based
material.maxpsDamageInitiation.DamageEvolution(
    type=DISPLACEMENT,
    softening=LINEAR,
    table=((effective_displacement_at_failure,),)
)

# 4. Mixed-mode fracture energy (BK law)
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    mixedModeBehavior=BK,
    power=2.284,  # BK exponent
    table=((G_Ic, G_IIc, G_IIIc),)  # Mode I, II, III fracture energies
)
```

## Crack with Initial Defect

```python
# Define initial crack as a surface
# Create datum plane at crack location
crack_plane = part.DatumPlaneByPrincipalPlane(
    principalPlane=XZPLANE, offset=hole_y
)

# Partition part by crack plane
part.PartitionCellByDatumPlane(datumPlane=crack_plane, cells=part.cells)

# Select crack face (half-face for initial crack)
crack_face = part.faces.findAt(((hole_x + hole_radius, hole_y, plate_thickness/2),))
crack_region = regionToolset.Region(faces=crack_face)

# Create contour integral for SIF calculation
model.ContourIntegral(
    name='SIF-Crack',
    crackFront=crack_region,
    crackTip=crack_region,
    crackName='Crack-1',
    type=STRESS_INTENS_FACTORS,
    numContours=5
)
```

## Post-Processing — Crack Visualization

```python
from odbAccess import openOdb

odb = openOdb(path='XFEM-Crack-Job.odb')

# Get last frame
last_step = odb.steps['Crack-Propagation']
last_frame = last_step.frames[-1]

# Check which elements cracked
status_field = last_frame.fieldOutputs['STATUSXFEM']
cracked = [v for v in status_field.values if v.data < 1.0]
print(f"Cracked elements: {len(cracked)}")

# PHILSM = signed distance from crack surface
philsm = last_frame.fieldOutputs['PHILSM']
print(f"Max level set value: {max(v.data for v in philsm.values):.3f}")

# Reaction force (for load-displacement curve)
history = odb.steps['Crack-Propagation'].historyRegions
# Access history output for load-displacement curve

odb.close()
```

## Troubleshooting XFEM Convergence

| Problem | Cause | Solution |
|---------|-------|----------|
| Increment cutbacks at initiation | Unstable crack onset | Add viscous stabilization (1e-5 to 1e-4) |
| No crack propagation | Damage initiation stress too high | Reduce MAXPS value or check BCs |
| Elements all crack at once | Unstable snap-through | Use displacement control, refine mesh |
| Excessive hourglass modes | Under-integrated elements | Use fully-integrated elements (C3D8 not C3D8R) |
| Job aborts with errors | XFEM incompatible with some features | Remove tie constraints in crack domain |

## Element Selection for XFEM

| Element | Recommendation | Notes |
|---------|---------------|-------|
| C3D8 | ✓ Good | Fully integrated linear hex |
| C3D10 | ✓ Best for complex geometry | Quadratic tet |
| C3D8R | ✗ Avoid | Reduced integration + XFEM = severe hourglassing |
| C3D20R | ✓ Good (expensive) | Quadratic hex, reduced integration OK |
| S4R | ✓ For shells | XFEM supported for shell elements |

## Verification Checklist

- [ ] Mesh is adequately refined in expected crack path
- [ ] Viscous stabilization energy < 5% of total energy
- [ ] Crack path is physically reasonable (validate against known fracture mechanics)
- [ ] Mass scaling (if used) does not artificially increase kinetic energy
- [ ] Boundary conditions do not constrain crack opening
