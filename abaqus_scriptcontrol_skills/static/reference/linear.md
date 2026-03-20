# Linear Static Analysis Detailed Reference

## Overview

Linear static analysis is the most basic and commonly used analysis method in Abaqus, applicable for small deformation, linear elastic materials, and structural analysis where boundary conditions do not change with deformation.

## Applicable Scenarios

- Small deformation structural analysis (deformation < 5% of characteristic dimension)
- Linear elastic materials (stress < yield strength)
- Stiffness calculation, strength verification
- Displacement and reaction force calculation

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Linear Static Analysis
Description: Stress and deformation analysis within linear elastic range
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometric parameters
length = 100.0       # mm
width = 50.0         # mm
height = 10.0        # mm

# Material parameters (Steel_Q235)
E = 210000.0         # MPa
nu = 0.3
rho = 7.85e-09

# Load parameters
load_magnitude = 1000.0  # N

# Mesh parameters
element_size = 2.0

# ========== 2. Create Model ==========
model_name = 'Linear-Static-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create part
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']

# ========== 3. Material and Section ==========
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='Section-1')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 5. Step ==========
model.StaticStep(
    name='Static-Step',
    previous='Initial',
    description='Linear static analysis',
    timePeriod=1.0,
    initialInc=1.0,
    minInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF
)

model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Step',
    variables=('S', 'E', 'U', 'RF', 'MISES'),
    frequency=1
)

# ========== 6. Boundary Conditions ==========
fixed_faces = instance.faces.findAt(((0.0, width/2, height/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0, u2=0.0, u3=0.0
)

# ========== 7. Load ==========
load_faces = instance.faces.findAt(((length, width/2, height/2),))
region = assembly.Set(name='Load-End', faces=load_faces)
model.ConcentratedForce(
    name='Load-Force',
    createStepName='Static-Step',
    region=region,
    cf3=-load_magnitude
)

# ========== 8. Mesh ==========
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=element_size, deviationFactor=0.1)

elem_type = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 9. Job Submission ==========
job_name = 'Linear-Static-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    numCpus=4,
    numDomains=4
)

job.submit(consistencyChecking=OFF)
job.waitForCompletion()

print("Linear static analysis completed!")
```

## Key Parameter Description

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| nlgeom | Geometric nonlinearity | OFF |
| initialInc | Initial increment | 1.0 |
| maxInc | Maximum increment | 1.0 |
| maxNumInc | Maximum number of increments | 1 |
| elemCode | Element type | C3D8 or C3D8R |

## Result Interpretation

### Viewing Results

```python
from odbAccess import openOdb

odb = openOdb(path='Linear-Static-Job.odb')
last_step = odb.steps.values()[-1]
last_frame = last_step.frames[-1]

# Get stress
stress_field = last_frame.fieldOutputs['S']
max_stress = max([v.mises for v in stress_field.values])
print(f"Maximum Mises stress: {max_stress:.2f} MPa")

# Get displacement
u_field = last_frame.fieldOutputs['U']
max_disp = max([v.magnitude for v in u_field.values])
print(f"Maximum displacement: {max_disp:.4f} mm")

odb.close()
```

## Verification Checklist

- [ ] Stress value < material yield strength
- [ ] Maximum deformation < 5% of characteristic dimension
- [ ] Mesh is sufficiently refined
- [ ] Boundary conditions provide sufficient constraint
- [ ] Load direction is correct
