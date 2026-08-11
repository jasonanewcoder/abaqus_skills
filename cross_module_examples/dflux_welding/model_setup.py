# -*- coding: utf-8 -*-
"""
Cross-Module Example: Welding Thermal Analysis with DFLUX
=========================================================
Demonstrates the FULL agent loop for a moving-heat-source thermal analysis:

  Python (model + DFLUX + thermal step + job)
  → Fortran (Goldak double-ellipsoid heat source)
  → run headless → verify peak temperature → report

Skills used:
  - general/SKILL.md + reference/{modeling, material, step, bc_load, mesh, job,
    headless_execution, postprocess_odb, verification, error_diagnosis}.md
  - thermal/SKILL.md + reference/transient.md
  - subroutine_skills/SKILL.md + reference/thermal/dflux_welding.md

Units: N-mm-MPa-s  (power mW, length mm, time s, temperature °C)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import mesh

# ========== 1. Parameters ==========
plate_length, plate_width, plate_thick = 200.0, 50.0, 10.0   # mm
weld_start_x = 50.0       # mm
travel_speed = 4.0        # mm/s (keep in sync with dflux_welding.f)
total_time = 25.0         # s (weld bead length = V * t)

# Thermal properties (steel, N-mm-MPa)
k = 45.0                  # mW/(mm·K)  (= W/(m·K), unchanged)
cp = 460.0 * 1e6          # N·mm/(tonne·K)  (J/(kg·K) × 1e6)
rho = 7.85e-9             # tonne/mm³
T0 = 20.0                 # °C initial temperature

# Convection (ambient cooling)
h_conv = 15e-3            # mW/(mm²·K)  (W/(m²·K) × 1e-3)
T_amb = 20.0              # °C

# Mesh
element_size = 2.5        # mm — fine: ≥ 2-3 elements across heat source (2R0≈6mm)

# Job
job_name = 'Weld-Thermal'
model_name = 'Weld-Model'

# ========== 2. Model ==========
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=300.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thick)
del model.sketches['__profile__']

# ========== 3. Thermal material ==========
material = model.Material(name='Steel-Thermal')
material.Conductivity(table=((k,),))
material.SpecificHeat(table=((cp,),))
material.Density(table=((rho,),))

section = model.HomogeneousSolidSection(name='Sec', material='Steel-Thermal')
part.SectionAssignment(region=(part.cells,), sectionName='Sec')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 5. Transient heat transfer step ==========
model.HeatTransferStep(
    name='Weld',
    previous='Initial',
    response=TRANSIENT,
    timePeriod=total_time,
    initialInc=0.05,      # ≤ element_size / travel_speed = 0.625 s — keep small
    minInc=0.001,
    maxInc=0.5,
    maxNumInc=20000,
    deltmx=50.0
)

# ========== 6. Boundary conditions & loads ==========
# Initial temperature field
all_cells = instance.cells
model.Temperature(
    name='Initial-T',
    createStepName='Initial',
    region=assembly.Set(name='All-Cells', cells=all_cells),
    distributionType=UNIFORM,
    magnitudes=(T0,)
)

# Convection on all exposed faces (except the weld top face to avoid double counting)
top_face = instance.faces.getByBoundingBox(
    weld_start_x - 1, 0, plate_thick - 0.5,
    plate_length, plate_width, plate_thick + 0.5)
side_faces = instance.faces.getByBoundingBox(
    -1, -1, -1, plate_length + 1, plate_width + 1, plate_thick - 0.5)
convection_faces = [f for f in side_faces if f not in top_face]
model.FilmCondition(
    name='Convection',
    createStepName='Weld',
    surface=assembly.Surface(name='Cool-Surf', side1Faces=convection_faces),
    definition=EMBEDDED_COEFF,
    filmCoeff=h_conv,
    sinkTemperature=T_amb
)

# ========== 7. Mesh ==========
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=element_size, deviationFactor=0.1)
elem_type = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()
print(f"Mesh: {len(part.elements)} elements, {len(part.nodes)} nodes")

# ========== 8. Output ==========
model.FieldOutputRequest(
    name='F-Out', createStepName='Weld',
    variables=('NT', 'HFL'), frequency=1
)
# History output at a mid-weld point (measure the thermal cycle)
mid_point = (weld_start_x + 100.0, plate_width / 2, plate_thick / 2)
mid_node = instance.nodes.getByBoundingBox(
    mid_point[0] - 1e-3, mid_point[1] - 1e-3, mid_point[2] - 1e-3,
    mid_point[0] + 1e-3, mid_point[1] + 1e-3, mid_point[2] + 1e-3)
if mid_node:
    model.HistoryOutputRequest(
        name='Mid-Point', createStepName='Weld',
        region=assembly.Set(name='Mid-Node', nodes=mid_node),
        variables=('NT1',), frequency=1
    )

# ========== 9. Job with user subroutine ==========
job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Welding thermal analysis with Goldak DFLUX',
    type=ANALYSIS,
    numCpus=4,
    numDomains=4,
    userSubroutine='dflux_welding.f'
)
job.writeInput(consistencyChecking=OFF)
print(f"Input file written: {job_name}.inp")

# ========== 10. Run + verify ==========
job.submit(consistencyChecking=OFF)
job.waitForCompletion()

if job.status == COMPLETED:
    print(f"\n✓ Job {job_name} completed successfully!")
    print("  Verification:")
    print("  - Expected peak temperature: 1400–1800 °C near the weld line")
    print("    (arc welding of steel typically exceeds the melting point)")
    print("  - Thermal cycle at mid-weld point: rise to peak then cool")
    print("  - .sta shows small increments near the heat source, no cutback storm")
    print("  - HFL concentrated within ~2-3 element widths of the weld path")
    print("\n  Next steps (sequential coupling):")
    print("  1. Switch material to mechanical (E, nu, expansion)")
    print("  2. *Predefined Field, type=TEMPERATURE, file=Weld-Thermal.odb")
    print("  3. Static step with T from ODB → residual stress")
else:
    print(f"\n✗ Job status: {job.status}")
    print("  Check Weld-Thermal.msg / .dat; common issues:")
    print("  - 'TIME INCREMENT IS LESS THAN MINIMUM' → reduce deltmx or refine mesh")
    print("  - DFLUX errors → verify dflux_welding.f compiles (abaqus make library=...)")
