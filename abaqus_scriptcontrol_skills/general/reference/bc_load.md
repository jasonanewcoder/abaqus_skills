# Boundary Conditions and Loads Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus boundary condition and load definitions.

## Core API

```python
# Create boundary condition
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0, u2=0.0, u3=0.0
)

# Create concentrated force
model.ConcentratedForce(
    name='Load-Force',
    createStepName='Step-1',
    region=region,
    cf2=-1000.0
)

# Create pressure
model.Pressure(
    name='Load-Pressure',
    createStepName='Step-1',
    region=region,
    magnitude=10.0
)

# Create body force
model.BodyForce(
    name='Load-Gravity',
    createStepName='Step-1',
    region=region,
    comp3=-9800.0
)
```

## Code Templates

### Template 1: Fixed Constraint (Full Constraint)

```python
assembly = model.rootAssembly
instance = assembly.instances['Part-1-1']

# Select face by coordinate
fixed_faces = instance.faces.findAt(((0.0, 25.0, 10.0),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)

# Create fixed constraint
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0,
    u2=0.0,
    u3=0.0,
    ur1=UNSET,
    ur2=UNSET,
    ur3=UNSET,
    amplitude=UNSET,
    fixed=OFF,
    distributionType=UNIFORM
)
```

### Template 2: Symmetry Constraints

```python
# X-Y plane symmetry (Z=0 plane)
sym_faces = instance.faces.findAt(((50.0, 25.0, 0.0),))
region = assembly.Set(name='Symmetry-XY', faces=sym_faces)

model.DisplacementBC(
    name='BC-Symmetry-XY',
    createStepName='Initial',
    region=region,
    u1=UNSET,
    u2=UNSET,
    u3=0.0,
    ur1=0.0,
    ur2=0.0,
    ur3=UNSET
)

# X-Z plane symmetry (Y=0 plane)
region = assembly.Set(
    name='Symmetry-XZ',
    faces=instance.faces.findAt(((50.0, 0.0, 10.0),))
)
model.DisplacementBC(
    name='BC-Symmetry-XZ',
    createStepName='Initial',
    region=region,
    u1=UNSET,
    u2=0.0,
    u3=UNSET,
    ur1=0.0,
    ur2=UNSET,
    ur3=0.0
)

# Y-Z plane symmetry (X=0 plane)
region = assembly.Set(
    name='Symmetry-YZ',
    faces=instance.faces.findAt(((0.0, 25.0, 10.0),))
)
model.DisplacementBC(
    name='BC-Symmetry-YZ',
    createStepName='Initial',
    region=region,
    u1=0.0,
    u2=UNSET,
    u3=UNSET,
    ur1=UNSET,
    ur2=0.0,
    ur3=0.0
)
```

### Template 3: Specified Displacement

```python
loaded_faces = instance.faces.findAt(((100.0, 25.0, 10.0),))
region = assembly.Set(name='Loaded-End', faces=loaded_faces)

model.DisplacementBC(
    name='BC-Displacement',
    createStepName='Step-1',
    region=region,
    u1=0.0,
    u2=10.0,
    u3=0.0,
    ur1=UNSET,
    ur2=UNSET,
    ur3=UNSET
)
```

### Template 4: Concentrated Force

```python
# Apply concentrated force on node
load_node = instance.nodes[10]
region = assembly.Set(name='Load-Node', nodes=(load_node,))

model.ConcentratedForce(
    name='Load-Force',
    createStepName='Step-1',
    region=region,
    cf1=0.0,
    cf2=-1000.0,
    cf3=0.0
)

# Concentrated force on multiple nodes
load_nodes = (instance.nodes[10], instance.nodes[11], instance.nodes[12])
region = assembly.Set(name='Load-Nodes', nodes=load_nodes)
model.ConcentratedForce(
    name='Load-Forces',
    createStepName='Step-1',
    region=region,
    cf2=-500.0
)
```

### Template 5: Pressure Load

```python
# Uniform pressure
pressure_faces = instance.faces.findAt(((50.0, 50.0, 10.0),))
region = assembly.Surface(name='Pressure-Surf', side1Faces=pressure_faces)

model.Pressure(
    name='Load-Pressure',
    createStepName='Step-1',
    region=region,
    distributionType=UNIFORM,
    magnitude=10.0
)

# Distributed pressure (using analytical field)
model.AnalyticalField(
    name='Varying-Pressure',
    description='Linearly varying pressure',
    expression='10.0 + 0.1 * X'
)

model.Pressure(
    name='Load-Varying-Pressure',
    createStepName='Step-1',
    region=region,
    distributionType=FIELD,
    field='Varying-Pressure',
    magnitude=1.0
)
```

### Template 6: Gravity/Acceleration

```python
# Entire model
all_cells = instance.cells
region = assembly.Set(name='Whole-Body', cells=all_cells)

# Method 1: Using body force
gravity = 9800.0  # mm/s²
model.BodyForce(
    name='Load-Gravity',
    createStepName='Step-1',
    region=region,
    comp1=0.0,
    comp2=-gravity,
    comp3=0.0
)

# Method 2: Using gravity load
model.Gravity(
    name='Load-Gravity',
    createStepName='Step-1',
    comp1=0.0,
    comp2=-1.0,
    comp3=0.0
)
```

### Template 7: Centrifugal Force

```python
# Rotate around Z-axis, 1000 RPM
omega = 1000.0 * 2.0 * 3.14159 / 60.0  # rad/s

model.RotationalBodyForce(
    name='Load-Centrifugal',
    createStepName='Step-1',
    region=region,
    magnitude=omega**2,
    centrifugal=ON,
    rotaryAcceleration=OFF,
    point1=(0.0, 0.0, 0.0),
    point2=(0.0, 0.0, 100.0)
)
```

### Template 8: Temperature Load

```python
# Initial temperature field
model.Temperature(
    name='Predefined-Field',
    createStepName='Initial',
    region=region,
    distributionType=UNIFORM,
    magnitudes=(20.0,)
)

# Temperature change
model.Temperature(
    name='Temp-Change',
    createStepName='Step-1',
    region=region,
    distributionType=UNIFORM,
    magnitudes=(100.0,)
)

# Import temperature field from results file
model.Temperature(
    name='Temp-From-ODB',
    createStepName='Step-1',
    region=region,
    distributionType=FROM_FILE,
    fileName='thermal_results.odb',
    beginStep=0,
    beginIncrement=0,
    endStep=LAST_STEP,
    endIncrement=LAST_INCREMENT,
    interpolate=ON
)
```

### Template 9: Bolt Pretension

```python
# Create bolt loading surface
bolt_faces = instance.faces.findAt(((50.0, 0.0, 10.0),))
region = assembly.Surface(name='Bolt-Surf', side1Faces=bolt_faces)

# Pretension (step 1)
model.BoltLoad(
    name='Bolt-Pretension',
    createStepName='Step-1',
    region=region,
    magnitude=10000.0,
    boltMethod=APPLY_FORCE,
    amplitude=UNSET,
    preloadType=DEPENDENT
)

# Fix bolt length (subsequent steps)
model.BoltLoad(
    name='Bolt-Fix',
    createStepName='Step-2',
    region=region,
    boltMethod=FIX_LENGTH
)
```

### Template 10: Amplitude Curves

```python
# Tabular amplitude
model.TabularAmplitude(
    name='Ramp-Amplitude',
    timeSpan=STEP,
    smooth=SOLVER_DEFAULT,
    data=((0.0, 0.0), (0.5, 0.5), (1.0, 1.0))
)

# Apply amplitude
model.Pressure(
    name='Load-With-Amplitude',
    createStepName='Step-1',
    region=region,
    magnitude=10.0,
    amplitude='Ramp-Amplitude'
)

# Smooth step amplitude
model.SmoothStepAmplitude(
    name='Smooth-Amp',
    timeSpan=STEP,
    data=((0.0, 0.0), (1.0, 1.0))
)
```

## Boundary Condition Management

```python
# Suppress boundary condition
model.boundaryConditions['BC-Fixed'].deactivate('Step-2')

# Reactivate
model.boundaryConditions['BC-Fixed'].activate('Step-3')

# Modify boundary condition
model.boundaryConditions['BC-Displacement'].setValuesInStep(
    stepName='Step-2',
    u2=20.0
)
```

## Best Practices

1. **Constraint Check**:
   - Ensure sufficient constraints to avoid rigid body displacement
   - Use symmetry constraints to simplify models

2. **Load Application**:
   - Concentrated forces should be applied on nodes
   - Check pressure direction (arrow points toward face)

3. **Unit Consistency**:
   - Force: N
   - Pressure: MPa (N/mm²)
   - Acceleration: mm/s²

4. **Increment Control**:
   - Use STEP amplitude for sudden loads
   - Use RAMP amplitude for gradual loads
