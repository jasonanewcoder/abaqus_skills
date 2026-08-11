# -*- coding: utf-8 -*-
"""
Cross-Module Example: Plate with Spatially-Varying Elastic Modulus
Demonstrates Python script + USDFLD subroutine workflow

Skills used:
  - general/SKILL.md + reference/modeling.md, material.md, bc_load.md, mesh.md, job.md
  - static/SKILL.md + reference/linear.md
  - subroutine_skills/reference/field/usdfld_spatial.md
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry
plate_length = 100.0   # mm (X-direction)
plate_width = 50.0     # mm (Y-direction)
plate_thickness = 5.0  # mm

# Material (base values — will be modified by USDFLD)
E_left = 210000.0      # MPa, stiff end (X=0)
E_right = 70000.0      # MPa, soft end (X=plate_length)
nu = 0.3
E_ref_values = (E_left, E_right)  # Reference values for USDFLD

# Load
tensile_stress = 100.0  # MPa (uniform tensile stress at right end)

# Mesh
element_size = 2.0     # mm

# ========== 2. Create Model ==========
model_name = 'FGM-Plate'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create plate
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del model.sketches['__profile__']

# ========== 3. Material with Field Variable Dependency ==========
material = model.Material(name='FGM-Material')

# Elastic modulus depends on FIELD(1)
# USDFLD sets FIELD(1) based on X-coordinate
# Table format: (E, nu, TEMP, FIELD1)
# When field=0 → E=210000; when field=1 → E=70000
material.Elastic(
    type=ISOTROPIC,
    temperatureDependency=OFF,
    dependencies=1,  # Depends on 1 field variable
    table=(
        (210000.0, nu, 0.0),   # FIELD(1)=0: E=E_left
        (70000.0,  nu, 1.0),  # FIELD(1)=1: E=E_right
    )
)

# The material has a User Defined Field via USDFLD
# *Depvar is needed to store the field variable
material.Depvar(n=1)  # 1 state variable to hold FIELD(1)

# Section
section = model.HomogeneousSolidSection(
    name='PlateSection', material='FGM-Material'
)
part.SectionAssignment(region=(part.cells,), sectionName='PlateSection')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 5. Step ==========
model.StaticStep(
    name='Tensile-Step',
    previous='Initial',
    description='Tension test on FGM plate',
    timePeriod=1.0,
    initialInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF
)

model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Tensile-Step',
    variables=('S', 'E', 'U', 'RF', 'FV'),
    frequency=1
)

# ========== 6. Boundary Conditions ==========
# Fix left end (X=0)
left_face = instance.faces.findAt(((0.0, plate_width/2, plate_thickness/2),))
left_region = assembly.Set(name='Fixed-End', faces=left_face)
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=left_region,
    u1=0.0, u2=0.0, u3=0.0
)

# ========== 7. Load ==========
# Apply tensile stress on right end (X=plate_length)
right_face = instance.faces.findAt(
    ((plate_length, plate_width/2, plate_thickness/2),)
)
load_region = assembly.Surface(
    name='Loaded-End', side1Faces=right_face
)

# Uniform tensile pressure
model.Pressure(
    name='Tensile-Stress',
    createStepName='Tensile-Step',
    region=load_region,
    distributionType=UNIFORM,
    magnitude=-tensile_stress  # Negative = tension (pulling outward)
)

# ========== 8. Mesh ==========
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED
)
part.seedPart(size=element_size)

elem_type = mesh.ElemType(
    elemCode=C3D8,
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

print(f"Mesh: {len(part.elements)} elements, {len(part.nodes)} nodes")

# ========== 9. Job with USDFLD ==========
job_name = 'FGM-Plate'

if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    description='FGM plate — spatially varying E via USDFLD',
    numCpus=4,
    userSubroutine='usdfld_spatial.f'  # ← USDFLD subroutine
)

job.writeInput(consistencyChecking=OFF)
print(f"Input file: {job_name}.inp")

job.submit()
job.waitForCompletion()

if job.status == COMPLETED:
    print(f"\n✓ Job {job_name} completed!")
    print(f"  Stiff end (X=0): E = {E_left} MPa — lower strain")
    print(f"  Soft end (X={plate_length}): E = {E_right} MPa — higher strain")
else:
    print(f"\n✗ Job status: {job.status}")
    print(f"  Check {job_name}.msg for details")
