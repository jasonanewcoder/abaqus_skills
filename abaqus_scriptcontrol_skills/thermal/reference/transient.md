# Transient Heat Transfer & Thermal-Stress Coupling — Detailed Reference

## Overview

Transient heat transfer analysis calculates time-varying temperature fields. Combined with thermal stress analysis (sequential coupling), this enables simulation of thermal stresses during heating/cooling processes.

## Applicable Scenarios

- Welding thermal cycles and residual stress
- Casting solidification
- Heat treatment (quenching, annealing)
- Thermal shock events
- Electronic device thermal cycling

## Theoretical Foundation

### Transient Heat Conduction Equation

```
ρc_p (∂T/∂t) = ∇ · (k ∇T) + Q
```

| Symbol | Meaning | Abaqus Unit |
|--------|---------|-------------|
| ρ | Density | tonne/mm³ |
| c_p | Specific heat | mJ/(tonne·K) |
| k | Thermal conductivity | mW/(mm·K) |
| ∂T/∂t | Temperature rate | K/s |
| Q | Internal heat generation | mW/mm³ |

### Sequential Thermal-Stress Coupling

1. **Step 1**: Run transient heat transfer analysis → save temperature history to .odb
2. **Step 2**: Run static stress analysis with temperature imported from thermal .odb
3. **Result**: Thermal stress = stress caused by constrained thermal expansion

## Complete Script Template — Sequential Coupling

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Transient Thermal + Thermal-Stress Sequential Coupling
Description: Temperature field and resulting thermal stress during heating
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry
block_length = 100.0   # mm
block_width = 20.0     # mm
block_height = 10.0    # mm

# Thermal properties (Steel)
k = 45.0               # W/(m·K) — thermal conductivity
cp = 460.0             # J/(kg·K) — specific heat
rho = 7.85e-09         # tonne/mm³ — density
cp_abaqus = cp * 1e9   # mJ/(tonne·K) — Abaqus unit

# Mechanical properties
E = 210000.0           # MPa
nu = 0.3
alpha = 1.2e-05        # /°C — thermal expansion coefficient
yield_stress = 235.0   # MPa

# Thermal BC
temp_initial = 20.0    # °C, initial temperature
temp_hot = 500.0       # °C, applied temperature
h_conv = 15e-6         # mW/(mm²·K) — natural convection

# Time parameters
total_time = 600.0     # s, total heating time
initial_inc = 10.0     # s, initial time increment

# ========== 2. Create Models ==========
# Thermal model
thermal_model_name = 'Thermal-Transient'
if thermal_model_name in mdb.models.keys():
    del mdb.models[thermal_model_name]
thermal_model = mdb.Model(name=thermal_model_name)

# Stress model (will be created after thermal analysis)
stress_model_name = 'Thermal-Stress'
if stress_model_name in mdb.models.keys():
    del mdb.models[stress_model_name]

# ========== Create Parts (same geometry for both) ==========
# Thermal part
sketch = thermal_model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(block_length, block_width))
thermal_part = thermal_model.Part(
    name='Block', dimensionality=THREE_D, type=DEFORMABLE_BODY
)
thermal_part.BaseSolidExtrude(sketch=sketch, depth=block_height)
del thermal_model.sketches['__profile__']

# ========== 3. Thermal Material ==========
therm_mat = thermal_model.Material(name='Steel-Thermal')
therm_mat.Conductivity(table=((k,),))
therm_mat.SpecificHeat(table=((cp_abaqus,),))
therm_mat.Density(table=((rho,),))
therm_mat.Expansion(table=((alpha,),))

thermal_section = thermal_model.HomogeneousSolidSection(
    name='Thermal-Section', material='Steel-Thermal'
)
thermal_part.SectionAssignment(
    region=(thermal_part.cells,), sectionName='Thermal-Section'
)

# ========== 4. Assembly ==========
thermal_assembly = thermal_model.rootAssembly
thermal_instance = thermal_assembly.Instance(
    name='Block-1', part=thermal_part, dependent=ON
)

# ========== 5. Transient Heat Transfer Step ==========
thermal_model.HeatTransferStep(
    name='Heating-Transient',
    previous='Initial',
    description='Transient heating analysis',
    response=TRANSIENT,
    timePeriod=total_time,
    maxNumInc=10000,
    initialInc=initial_inc,
    minInc=0.01,
    maxInc=60.0,
    deltmx=50.0  # Max temperature change per increment
)

thermal_model.FieldOutputRequest(
    name='Thermal-Output',
    createStepName='Heating-Transient',
    variables=('NT', 'TEMP', 'HFL'),
    frequency=10  # Every 10 increments
)

thermal_model.HistoryOutputRequest(
    name='Temp-History',
    createStepName='Heating-Transient',
    variables=('NT11',),
    region=thermal_model.rootAssembly.sets['Monitor-Point'],
    frequency=1
)

# ========== 6. Initial Temperature & BCs ==========
# Initial temperature (predefined field)
all_cells_region = thermal_assembly.Set(
    name='All-Cells', cells=thermal_instance.cells
)
thermal_model.Temperature(
    name='Initial-Temp',
    createStepName='Initial',
    region=all_cells_region,
    distributionType=UNIFORM,
    magnitudes=(temp_initial,)
)

# Fixed temperature on one end
hot_face = thermal_instance.faces.findAt(
    ((0.0, block_width/2, block_height/2),)
)
hot_region = thermal_assembly.Set(name='Hot-End', faces=hot_face)
thermal_model.TemperatureBC(
    name='BC-Hot',
    createStepName='Heating-Transient',
    region=hot_region,
    magnitude=temp_hot
)

# Convection on exposed faces
exposed_faces = thermal_instance.faces.findAt(
    ((block_length/2, block_width/2, block_height),),   # top
    ((block_length/2, block_width/2, 0.0),),             # bottom
    ((block_length/2, block_width, block_height/2),),     # front
    ((block_length/2, 0.0, block_height/2),),             # back
)
conv_surface = thermal_assembly.Surface(
    name='Conv-Surf', side1Faces=exposed_faces
)
thermal_model.FilmCondition(
    name='Conv-Natural',
    createStepName='Heating-Transient',
    surface=conv_surface,
    definition=EMBEDDED_COEFF,
    filmCoeff=h_conv,
    sinkTemperature=temp_initial
)

# Monitor point
monitor_vertex = thermal_instance.vertices.findAt(
    ((block_length, block_width/2, block_height/2),)
)
thermal_assembly.Set(name='Monitor-Point', vertices=monitor_vertex)

# ========== 7. Mesh (Thermal) ==========
thermal_part.setMeshControls(
    regions=thermal_part.cells, elemShape=HEX, technique=STRUCTURED
)
thermal_part.seedPart(size=5.0)

therm_elem = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)
thermal_part.setElementType(
    regions=(thermal_part.cells,), elemTypes=(therm_elem,)
)
thermal_part.generateMesh()

# ========== 8. Submit Thermal Job ==========
thermal_job_name = 'Thermal-Transient-Job'
thermal_job = mdb.Job(
    name=thermal_job_name, model=thermal_model_name, numCpus=4
)
thermal_job.submit()
thermal_job.waitForCompletion()

print("Thermal analysis completed!")
print(f"Results saved to: {thermal_job_name}.odb")

# ========== 9. Thermal-Stress Analysis (Sequential Coupling) ==========
print("Starting thermal-stress analysis...")

# Create stress model by copying geometry and adding mechanical properties
stress_model = mdb.Model(name=stress_model_name)

# Create mechanical part (same geometry)
sketch2 = stress_model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch2.rectangle(point1=(0.0, 0.0), point2=(block_length, block_width))
stress_part = stress_model.Part(
    name='Block', dimensionality=THREE_D, type=DEFORMABLE_BODY
)
stress_part.BaseSolidExtrude(sketch=sketch2, depth=block_height)
del stress_model.sketches['__profile__']

# Mechanical material
mech_mat = stress_model.Material(name='Steel-Mech')
mech_mat.Elastic(table=((E, nu),))
mech_mat.Expansion(table=((alpha,),))
mech_mat.Density(table=((rho,),))
# Optional: temperature-dependent plasticity
mech_mat.Plastic(table=((yield_stress, 0.0),))

mech_section = stress_model.HomogeneousSolidSection(
    name='Mech-Section', material='Steel-Mech'
)
stress_part.SectionAssignment(
    region=(stress_part.cells,), sectionName='Mech-Section'
)

# Assembly
stress_assembly = stress_model.rootAssembly
stress_instance = stress_assembly.Instance(
    name='Block-1', part=stress_part, dependent=ON
)

# Static step for thermal stress
stress_model.StaticStep(
    name='Thermal-Stress',
    previous='Initial',
    description='Thermal stress from temperature field',
    timePeriod=1.0,
    initialInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF
)

stress_model.FieldOutputRequest(
    name='Stress-Output',
    createStepName='Thermal-Stress',
    variables=('S', 'E', 'U', 'MISES', 'TEMP')
)

# Boundary conditions (prevent rigid body motion)
fixed_face = stress_instance.faces.findAt(
    ((0.0, block_width/2, block_height/2),)
)
fixed_region = stress_assembly.Set(name='Fixed-End', faces=fixed_face)
stress_model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=fixed_region,
    u1=0.0, u2=0.0, u3=0.0
)

# Import temperature from thermal ODB
all_cells_stress = stress_assembly.Set(
    name='All-Cells', cells=stress_instance.cells
)
stress_model.Temperature(
    name='Import-Temp',
    createStepName='Thermal-Stress',
    region=all_cells_stress,
    distributionType=FROM_FILE,
    fileName=f'{thermal_job_name}.odb',
    beginStep=LAST_STEP,
    beginIncrement=LAST_INCREMENT,
    endStep=LAST_STEP,
    endIncrement=LAST_INCREMENT,
    interpolate=ON
)

# Mesh (mechanical)
stress_part.setMeshControls(
    regions=stress_part.cells, elemShape=HEX, technique=STRUCTURED
)
stress_part.seedPart(size=5.0)

mech_elem = mesh.ElemType(
    elemCode=C3D8T,  # Coupled temperature-displacement element
    elemLibrary=STANDARD
)
stress_part.setElementType(
    regions=(stress_part.cells,), elemTypes=(mech_elem,)
)
stress_part.generateMesh()

# Submit stress job
stress_job_name = 'Thermal-Stress-Job'
stress_job = mdb.Job(
    name=stress_job_name, model=stress_model_name, numCpus=4
)
stress_job.submit()
stress_job.waitForCompletion()

print("Thermal-stress analysis completed!")
```

## Fully-Coupled vs. Sequential Coupling

| Aspect | Sequential | Fully-Coupled |
|--------|-----------|---------------|
| Steps | 2 separate analyses | 1 analysis |
| Element type | DC3D8 (thermal) + C3D8 (mech) | C3D8T |
| Step type | HeatTransfer + Static | CoupledTempDisplacement |
| When to use | Weak coupling, one-way | Strong coupling, two-way |
| Computation cost | Lower | Higher |
| Temperature feedback | No (T determined first) | Yes (deformation affects T) |

## Fully-Coupled Step Setup

```python
model.CoupledTempDisplacementStep(
    name='Coupled-Thermal-Stress',
    previous='Initial',
    description='Fully coupled thermal-stress analysis',
    timePeriod=600.0,
    maxNumInc=10000,
    initialInc=10.0,
    minInc=0.01,
    maxInc=60.0,
    deltmx=50.0,
    cetol=0.001,
    nlgeom=ON
)
```

## Verification Checklist

- [ ] Specific heat uses correct Abaqus units (× 10⁹ conversion)
- [ ] Time increment is small enough to capture thermal transients
- [ ] Temperature field is physically reasonable before stress analysis
- [ ] Boundary conditions prevent rigid body motion without over-constraining thermal expansion
- [ ] Mesh is identical between thermal and stress models for accurate temperature mapping

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "No temperature data found" | ODB file path incorrect | Verify thermal job completed and .odb exists |
| Stress too high at fixed end | Over-constrained expansion | Allow expansion in one direction |
| Non-convergence in thermal step | Too large deltmx or time increment | Reduce deltmx to 20-50°C |
| Zero thermal stress | Missing expansion coefficient | Add Expansion property to material |
