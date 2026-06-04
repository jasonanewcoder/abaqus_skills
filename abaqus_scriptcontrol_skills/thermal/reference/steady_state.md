# Steady-State Heat Transfer Analysis — Detailed Reference

## Overview

Steady-state heat transfer analysis calculates temperature distribution when the system has reached thermal equilibrium — temperatures no longer change with time. This is the foundation for thermal stress analysis.

## Applicable Scenarios

- Electronic component heat dissipation
- Building thermal envelope analysis
- Heat exchanger steady operation
- Pre-step for sequential thermal-stress coupling

## Theoretical Foundation

### Fourier's Law of Heat Conduction (Steady-State)

```
∇ · (k ∇T) + Q = 0
```

| Symbol | Meaning | Unit (N-mm-MPa) |
|--------|---------|------------------|
| k | Thermal conductivity | W/(m·K) or mW/(mm·K) |
| T | Temperature | °C or K |
| Q | Internal heat generation | mW/mm³ |

### Boundary Conditions

| Type | Equation | Abaqus Implementation |
|------|----------|----------------------|
| Fixed temperature | T = T₀ | `model.TemperatureBC(...)` |
| Heat flux | -k(∂T/∂n) = q₀ | `model.SurfaceHeatFlux(...)` |
| Convection | -k(∂T/∂n) = h(T - T_∞) | `model.FilmCondition(...)` |
| Radiation | -k(∂T/∂n) = εσ(T⁴ - T_∞⁴) | `model.Radiation(...)` |

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: Steady-State Heat Transfer
Description: Thermal equilibrium temperature distribution calculation
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry
plate_length = 100.0   # mm
plate_width = 50.0     # mm
plate_thickness = 5.0  # mm

# Thermal properties
k = 45.0               # W/(m·K) — thermal conductivity
specific_heat = 460.0  # J/(kg·K) — for reference

# Boundary conditions
temp_left = 100.0      # °C, fixed temperature on left end
temp_ambient = 20.0    # °C, ambient temperature
h_conv = 15.0          # mW/(mm²·K) — convection coefficient (W/(m²·K) × 10⁻⁶)
q_flux = 0.5           # mW/mm² — heat flux (W/m² × 10⁻⁶)

# ========== 2. Create Model ==========
model_name = 'Thermal-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create plate geometry
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del model.sketches['__profile__']

# ========== 3. Material (Thermal Properties) ==========
material = model.Material(name='Steel-Thermal')
material.Conductivity(table=((k,),))
# Note: Specific heat is NOT needed for steady-state analysis
# material.SpecificHeat(table=((specific_heat * 1e9),))  # mJ/(tonne·K)

# Thermal expansion (for stress analysis later)
expansion_coeff = 1.2e-05  # /°C
material.Expansion(table=((expansion_coeff,),))

# Solid section (required even for thermal-only)
section = model.HomogeneousSolidSection(name='Section-1', material='Steel-Thermal')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 5. Heat Transfer Step ==========
model.HeatTransferStep(
    name='Steady-State',
    previous='Initial',
    description='Steady-state thermal analysis',
    response=STEADY_STATE,
    maxNumInc=1000,
    initialInc=1.0,
    minInc=1e-05,
    maxInc=1.0,
    deltmx=100.0  # Maximum temperature change per increment
)

# Field output — thermal results
model.FieldOutputRequest(
    name='Thermal-Output',
    createStepName='Steady-State',
    variables=('NT', 'HFL', 'TEMP')
)

# ========== 6. Boundary Conditions ==========
# Fixed temperature on left face (100°C)
left_face = instance.faces.findAt(((0.0, plate_width/2, plate_thickness/2),))
region_left = assembly.Set(name='Hot-End', faces=left_face)
model.TemperatureBC(
    name='BC-Temp-Hot',
    createStepName='Steady-State',
    region=region_left,
    magnitude=temp_left
)

# Convection on top and bottom faces
top_face = instance.faces.findAt(((plate_length/2, plate_width/2, plate_thickness),))
bottom_face = instance.faces.findAt(((plate_length/2, plate_width/2, 0.0),))
conv_faces = assembly.Surface(
    name='Conv-Surface',
    side1Faces=(top_face, bottom_face)
)
model.FilmCondition(
    name='Conv-Natural',
    createStepName='Steady-State',
    surface=conv_faces,
    definition=EMBEDDED_COEFF,
    filmCoeff=h_conv,
    filmCoeffAmplitude='',
    sinkTemperature=temp_ambient
)

# Heat flux on right face
right_face = instance.faces.findAt(((plate_length, plate_width/2, plate_thickness/2),))
flux_region = assembly.Surface(name='Flux-Surface', side1Faces=right_face)
model.SurfaceHeatFlux(
    name='Heat-Flux',
    createStepName='Steady-State',
    surface=flux_region,
    magnitude=q_flux
)

# ========== 7. Mesh ==========
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED
)
part.seedPart(size=5.0)

# Heat transfer element type
elem_type = mesh.ElemType(
    elemCode=DC3D8,   # 8-node linear heat transfer brick
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 8. Job Submission ==========
job_name = 'Thermal-Steady-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit()
job.waitForCompletion()

print("Steady-state heat transfer analysis completed!")
```

## Unit Conversion for Thermal Properties

| Property | SI Unit | Abaqus Unit (N-mm-MPa) | Conversion |
|----------|---------|------------------------|------------|
| Thermal conductivity | W/(m·K) | mW/(mm·K) | **Same value** (1:1) |
| Specific heat | J/(kg·K) | mJ/(tonne·K) | **× 10⁹** |
| Convection coefficient | W/(m²·K) | mW/(mm²·K) | **× 10⁻⁶** |
| Heat flux | W/m² | mW/mm² | **× 10⁻⁶** |
| Internal heat generation | W/m³ | mW/mm³ | **× 10⁻⁹** |

## Common Thermal BC Types

```python
# 1. Fixed temperature
model.TemperatureBC(
    name='BC-Temp',
    createStepName='Step-1',
    region=region,
    magnitude=100.0  # °C
)

# 2. Convection (film condition)
model.FilmCondition(
    name='Convection',
    createStepName='Step-1',
    surface=surface,
    definition=EMBEDDED_COEFF,
    filmCoeff=15e-6,       # mW/(mm²·K) — note unit conversion
    sinkTemperature=20.0   # °C
)

# 3. Surface heat flux
model.SurfaceHeatFlux(
    name='Heat-Flux',
    createStepName='Step-1',
    surface=surface,
    magnitude=0.5  # mW/mm²
)

# 4. Body heat flux (internal heat generation)
model.BodyHeatFlux(
    name='Internal-Heat',
    createStepName='Step-1',
    region=region,
    magnitude=1e-3  # mW/mm³
)

# 5. Radiation
model.Radiation(
    name='Radiation',
    createStepName='Step-1',
    surface=surface,
    emissivity=0.85,
    ambientTemperature=20.0
)
```

## Thermal Element Types

| Element Code | Description | Use Case |
|-------------|-------------|----------|
| DC3D8 | Linear heat transfer brick | General 3D |
| DC3D10 | Quadratic heat transfer tetra | Complex geometry |
| DC3D20 | Quadratic heat transfer brick | High accuracy |
| DS4 | Linear heat transfer shell | Thin structures |

## Temperature-Dependent Properties

```python
# Temperature-dependent thermal conductivity
material.Conductivity(
    temperatureDependency=ON,
    table=(
        (45.0, 20.0),    # k=45 at 20°C
        (42.0, 200.0),   # k=42 at 200°C
        (38.0, 400.0),   # k=38 at 400°C
        (32.0, 600.0),   # k=32 at 600°C
    )
)

# Temperature-dependent convection coefficient
model.FilmCondition(
    name='Natural-Conv',
    createStepName='Thermal-Step',
    surface=surface,
    definition=EMBEDDED_COEFF,
    filmCoeff=15e-6,
    filmCoeffAmplitude='',
    sinkTemperature=20.0,
    sinkAmplitude='',
    filmCoeffField='',
    sinkField=''
)
```

## Post-Processing — Result Extraction

```python
from odbAccess import openOdb

odb = openOdb(path='Thermal-Steady-Job.odb')
last_step = odb.steps['Steady-State']
last_frame = last_step.frames[-1]

# Temperature field
temp_field = last_frame.fieldOutputs['NT11']  # Nodal temperature
temps = [v.data for v in temp_field.values]
print(f"Temperature range: {min(temps):.1f} to {max(temps):.1f} °C")

# Heat flux
hfl_field = last_frame.fieldOutputs['HFL']
hfl_magnitudes = [v.magnitude for v in hfl_field.values]
print(f"Max heat flux: {max(hfl_magnitudes):.3f} mW/mm²")

odb.close()
```

## Verification Checklist

- [ ] Temperature range is physically reasonable
- [ ] Heat flux balances (energy in = energy out at steady state)
- [ ] Mesh is adequate for thermal gradients (≥ 3 elements across steep gradient regions)
- [ ] Unit conversions are correct
- [ ] Convection coefficient corresponds to correct heat transfer regime

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Unrealistic temperature spike | Missing boundary condition | Ensure all boundaries have thermal BCs |
| No convergence | Too large deltmx | Reduce deltmx to 10-50°C |
| Heat flux sign wrong | Direction convention incorrect | Check surface normal direction |
| Temperature exceeds melting point | Heat input too high | Verify heat flux magnitudes and units |
