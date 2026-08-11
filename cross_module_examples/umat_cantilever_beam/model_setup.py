# -*- coding: utf-8 -*-
"""
Cross-Module Example: Cantilever Beam with Custom UMAT
Demonstrates Python script + Fortran UMAT workflow

Skills used:
  - general/SKILL.md + reference/modeling.md, material.md, bc_load.md, mesh.md, job.md
  - static/SKILL.md + reference/linear.md
  - subroutine_skills/reference/material/umat_elastic.md
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry (cantilever beam)
beam_length = 1000.0   # mm
beam_width = 50.0      # mm
beam_height = 100.0    # mm

# Material parameters (passed to UMAT via *User Material)
E = 210000.0           # MPa — Young's modulus
nu = 0.3               # Poisson's ratio

# UMAT needs exactly 2 material constants: E, nu
# These are read as PROPS(1) and PROPS(2) in the subroutine

# Load
tip_force = -5000.0    # N (negative = downward)

# Mesh
element_size = 20.0    # mm

# ========== 2. Create Model ==========
model_name = 'Cantilever-UMAT'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create beam (extrude rectangle)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(beam_width, beam_height))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=beam_length)
del model.sketches['__profile__']

# ========== 3. Material with User Material (UMAT) ==========
material = model.Material(name='Steel-UMAT')

# Define user material constants (read by UMAT as PROPS array)
# PROPS(1) = E, PROPS(2) = nu
material.UserMaterial(mechanicalConstants=(E, nu))

# Required: number of solution-dependent state variables
# Even though linear elastic UMAT uses 0 SDVs,
# Abaqus requires this line if *Depvar is in the input
# material.Depvar(n=0)  # Uncomment if your UMAT uses SDVs

# Note: Density is NOT defined here for static analysis,
# but MUST be defined for dynamic or gravity loads

# Create solid section
section = model.HomogeneousSolidSection(
    name='BeamSection',
    material='Steel-UMAT',
    thickness=None
)

# Assign section to part
part.SectionAssignment(
    region=(part.cells,),
    sectionName='BeamSection'
)

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 5. Step ==========
model.StaticStep(
    name='Static-Load',
    previous='Initial',
    description='Cantilever beam bending with UMAT',
    timePeriod=1.0,
    initialInc=1.0,
    minInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF
)

# Field output
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Load',
    variables=('S', 'E', 'U', 'RF'),
    frequency=1
)

# ========== 6. Boundary Conditions (Fixed End) ==========
# Fix the face at Z=0
fixed_face = instance.faces.findAt(((beam_width/2, beam_height/2, 0.0),))
fixed_region = assembly.Set(name='Fixed-End', faces=fixed_face)
model.EncastreBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=fixed_region
)

# ========== 7. Load (Tip Force) ==========
# Apply concentrated force at Z=beam_length (free end)
# Using a coupling constraint for distributed load on the tip surface
tip_face = instance.faces.findAt(
    ((beam_width/2, beam_height/2, beam_length),)
)
tip_region = assembly.Set(name='Tip-Face', faces=tip_face)

# Create reference point for load application
ref_point = assembly.ReferencePoint(
    point=(beam_width/2, beam_height/2, beam_length)
)
ref_point_id = ref_point.id

# Couple tip face to reference point
model.Coupling(
    name='Tip-Coupling',
    controlPoint=assembly.referencePoints[ref_point_id],
    surface=assembly.Surface(name='Tip-Surf', side1Faces=tip_face),
    influenceRadius=WHOLE_SURFACE,
    couplingType=KINEMATIC,
    u1=ON, u2=ON, u3=ON,
    ur1=ON, ur2=ON, ur3=ON
)

# Apply force at reference point
rp_region = assembly.Set(
    name='Load-Point',
    referencePoints=(assembly.referencePoints[ref_point_id],)
)
model.ConcentratedForce(
    name='Tip-Force',
    createStepName='Static-Load',
    region=rp_region,
    cf2=tip_force  # Y-direction (vertical)
)

# ========== 8. Mesh ==========
all_cells = part.cells

# Structured hex mesh
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED
)

# Seed and element type
part.seedPart(size=element_size, deviationFactor=0.1)

elem_type = mesh.ElemType(
    elemCode=C3D8,  # Fully integrated (better for bending with UMAT)
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

print(f"Mesh generated: {len(part.elements)} elements, {len(part.nodes)} nodes")

# ========== 9. Job Submission with User Subroutine ==========
job_name = 'Cantilever-UMAT'

# Delete existing job if present
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

# Create job WITH user subroutine
job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Cantilever beam with custom linear elastic UMAT',
    type=ANALYSIS,
    numCpus=4,
    numDomains=4,
    userSubroutine='umat_elastic.f'  # ← Key: references the Fortran file
)

# Write input file first (for inspection)
job.writeInput(consistencyChecking=OFF)
print(f"Input file written: {job_name}.inp")

# Submit job
job.submit(consistencyChecking=OFF)
print(f"Job {job_name} submitted with UMAT...")

# Wait for completion
job.waitForCompletion()

# ========== 10. Check Results ==========
if job.status == COMPLETED:
    print(f"\n✓ Job {job_name} completed successfully!")
    print(f"  Check {job_name}.odb for results")
    print(f"  Expected max deflection: ~2.86 mm (beam theory)")
    print(f"  Expected max bending stress: ~30 MPa")
else:
    print(f"\n✗ Job status: {job.status}")
    print(f"  Check {job_name}.msg and {job_name}.dat for errors")

# ========== Verification Notes ==========
print("""
Verification Checklist:
  [ ] Maximum tip displacement ≈ 2.86 mm (FL³/(3EI))
  [ ] Maximum bending stress σ_b ≈ 30 MPa (M·y/I)
  [ ] Results match Abaqus built-in elastic material
  [ ] No warnings about Jacobian or convergence
  [ ] .msg file shows quadratic convergence (1-2 iterations per increment)
""")
