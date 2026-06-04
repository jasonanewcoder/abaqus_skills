# -*- coding: utf-8 -*-
"""
Cross-Module Example: Bridge Deck Under Moving Wheel Load
Demonstrates Python script + DLOAD subroutine workflow

Skills used:
  - general/SKILL.md + reference/modeling.md, material.md, bc_load.md, mesh.md, job.md
  - subroutine_skills/reference/load/dload_moving.md
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Bridge deck geometry
deck_length = 10000.0   # mm (10 m span)
deck_width = 3000.0     # mm (3 m wide)
deck_thickness = 200.0  # mm

# Material (Concrete C30)
E = 30000.0            # MPa
nu = 0.2
rho = 2.50e-09         # tonne/mm³

# Vehicle parameters
axle_load = 100000.0   # N (per axle)
vehicle_speed = 15000.0  # mm/s (= 54 km/h)
total_time = deck_length / vehicle_speed  # s to cross

# Mesh
element_size = 200.0   # mm

# ========== 2. Create Model ==========
model_name = 'Bridge-DLOAD'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create bridge deck (solid extrusion)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=5000.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(deck_length, deck_width))
part = model.Part(name='Deck', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=deck_thickness)
del model.sketches['__profile__']

# ========== 3. Material & Section ==========
material = model.Material(name='Concrete-C30')
material.Elastic(table=((E, nu),))
material.Density(table=((rho,),))

section = model.HomogeneousSolidSection(
    name='DeckSection', material='Concrete-C30'
)
part.SectionAssignment(region=(part.cells,), sectionName='DeckSection')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Deck-1', part=part, dependent=ON)

# ========== 5. Steps ==========
# Static step with many increments for moving load resolution
model.StaticStep(
    name='Vehicle-Passage',
    previous='Initial',
    description='Moving vehicle load across bridge deck',
    timePeriod=total_time,
    initialInc=total_time / 100.0,
    minInc=total_time / 1000.0,
    maxInc=total_time / 20.0,
    maxNumInc=10000,
    nlgeom=OFF
)

# Field output at regular intervals
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Vehicle-Passage',
    variables=('S', 'E', 'U', 'RF', 'MISES'),
    frequency=10  # Every 10 increments
)

# ========== 6. Boundary Conditions ==========
# Simply supported: fix one end, roller at the other

# Left support (Z=0): pin support (U1=U2=U3=0)
left_edge = instance.edges.findAt(((0.0, 0.0, deck_thickness/2),))
left_region = assembly.Set(name='Left-Support', edges=left_edge)
model.DisplacementBC(
    name='BC-Left',
    createStepName='Initial',
    region=left_region,
    u1=0.0, u2=0.0, u3=0.0
)

# Right support (Z=deck_length): roller (U1=U2=0, U3 free)
right_edge = instance.edges.findAt(
    ((deck_length, 0.0, deck_thickness/2),)
)
right_region = assembly.Set(name='Right-Support', edges=right_edge)
model.DisplacementBC(
    name='BC-Right',
    createStepName='Initial',
    region=right_region,
    u1=0.0, u2=0.0
)

# ========== 7. Load Surface (DLOAD will define the pressure) ==========
# Define the top surface where DLOAD applies the moving load
top_face = instance.faces.findAt(
    ((deck_length/2, deck_width/2, deck_thickness),)
)
load_surface = assembly.Surface(
    name='Deck-Top', side1Faces=top_face
)

# Define distributed load (DLOAD subroutine controls the actual pressure)
model.Pressure(
    name='Moving-Wheel',
    createStepName='Vehicle-Passage',
    region=load_surface,
    distributionType=USER_DEFINED,  # ← Triggers DLOAD call
    magnitude=1.0  # Amplitude multiplier passed to DLOAD
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
    elemCode=C3D8R,
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

print(f"Mesh: {len(part.elements)} elements, {len(part.nodes)} nodes")

# ========== 9. Job Submission with DLOAD ==========
job_name = 'Bridge-DLOAD'

if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Bridge deck under moving load (DLOAD subroutine)',
    numCpus=4,
    userSubroutine='dload_moving.f'  # ← DLOAD subroutine file
)

job.writeInput(consistencyChecking=OFF)
print(f"Input file: {job_name}.inp")

job.submit()
job.waitForCompletion()

if job.status == COMPLETED:
    print(f"\n✓ Job {job_name} completed!")
    print(f"  Open {job_name}.odb to view time-varying deflection")
else:
    print(f"\n✗ Job status: {job.status}")
    print(f"  Check {job_name}.msg for details")
