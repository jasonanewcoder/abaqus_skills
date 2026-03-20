# Nonlinear Static Analysis Detailed Reference

## Overview

Nonlinear static analysis handles geometric nonlinearity (large deformation), material nonlinearity (plasticity), and contact nonlinearity problems.

## Applicable Scenarios

- Large deformation analysis (deformation > 5% of characteristic dimension)
- Material plastic analysis
- Contact problems
- Post-buckling analysis

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Nonlinear Static Analysis
Description: Static analysis with geometric and material nonlinearity
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== Parameter Definition ==========
length = 100.0
width = 50.0
height = 10.0

E = 210000.0
nu = 0.3
rho = 7.85e-09
yield_stress = 235.0
ultimate_stress = 375.0

load_magnitude = 5000.0

# Nonlinear control parameters
initial_inc = 0.05
min_inc = 1e-08
max_inc = 0.1
max_num_inc = 1000

# ========== Create Model ==========
model_name = 'Nonlinear-Static-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create part
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']

# ========== Material (with plasticity) ==========
material = model.Material(name='Steel-Plastic')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

plastic_data = (
    (yield_stress, 0.0),
    (ultimate_stress, 0.2),
)
material.Plastic(table=plastic_data)

section = model.HomogeneousSolidSection(name='Section-1', material='Steel-Plastic')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== Nonlinear Step ==========
model.StaticStep(
    name='Nonlinear-Step',
    previous='Initial',
    description='Nonlinear static analysis',
    timePeriod=1.0,
    initialInc=initial_inc,
    minInc=min_inc,
    maxInc=max_inc,
    maxNumInc=max_num_inc,
    nlgeom=ON,
    amplitude=RAMP
)

# Field output
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Nonlinear-Step',
    variables=('S', 'E', 'PE', 'PEEQ', 'U', 'RF'),
    frequency=10
)

# ========== Boundary Conditions ==========
fixed_faces = instance.faces.findAt(((0.0, width/2, height/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(name='BC-Fixed', createStepName='Initial', 
                     region=region, u1=0.0, u2=0.0, u3=0.0)

# ========== Load ==========
load_faces = instance.faces.findAt(((length, width/2, height/2),))
region = assembly.Set(name='Load-End', faces=load_faces)
model.ConcentratedForce(
    name='Load-Force',
    createStepName='Nonlinear-Step',
    region=region,
    cf3=-load_magnitude
)

# ========== Mesh ==========
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=2.0, deviationFactor=0.1)

elem_type = mesh.ElemType(
    elemCode=C3D8R,
    elemLibrary=STANDARD,
    hourglassControl=ENHANCED
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== Job Submission ==========
job_name = 'Nonlinear-Static-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit()
job.waitForCompletion()

print("Nonlinear static analysis completed!")
```

## Nonlinear Control Parameters

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| initialInc | Initial increment | 0.01 - 0.1 |
| minInc | Minimum increment | 1e-8 - 1e-5 |
| maxInc | Maximum increment | 0.1 - 0.5 |
| nlgeom | Geometric nonlinearity | ON |
| amplitude | Amplitude type | RAMP or STEP |

## Convergence Diagnostics

### Viewing Status File

```python
with open('Nonlinear-Static-Job.sta', 'r') as f:
    lines = f.readlines()
    for line in lines[-20:]:
        print(line.strip())
```

## Common Problems and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Increment repeatedly reduced | Load too large or insufficient constraint | Reduce initial increment, enable stabilization |
| Maximum increments reached | Convergence too slow | Increase maxNumInc |
| Singular matrix | Rigid body displacement | Check constraints |
| Hourglass mode | Reduced integration element deformation | Enable hourglass control |

## Stabilization Techniques

```python
model.StaticStep(
    name='Stabilized-Step',
    previous='Initial',
    stabilizationMagnitude=0.0002,
    stabilizationMethod=DAMPING_FACTOR,
    continueDampingFactors=False
)
```

## Verification Checklist

- [ ] Check PEEQ (equivalent plastic strain) distribution
- [ ] Confirm deformation is reasonable
- [ ] Check contact status
- [ ] Verify energy balance
- [ ] Check hourglass energy ratio (should be < 5%)
