# Step Setup Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus step setup.

## Core API

### Creating Steps

```python
# Static step
model.StaticStep(
    name='Step-1',
    previous='Initial',
    initialInc=0.1,
    maxInc=0.5,
    nlgeom=ON
)

# Dynamic step
model.DynamicImplicitStep(
    name='Dynamic-Step',
    previous='Initial',
    timePeriod=1.0,
    initialInc=0.01
)

# Modal step
model.FrequencyStep(
    name='Modal-Step',
    previous='Initial',
    numEigen=10
)

# Buckling step
model.BuckleStep(
    name='Buckle-Step',
    previous='Preload',
    numEigen=10
)

# Heat transfer step
model.HeatTransferStep(
    name='Thermal-Step',
    previous='Initial',
    response=STEADY_STATE
)
```

### Output Requests

```python
# Field output request
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Step-1',
    variables=('S', 'E', 'U', 'RF'),
    frequency=1
)

# History output request
model.HistoryOutputRequest(
    name='H-Output-1',
    createStepName='Step-1',
    variables=('RF1', 'U1')
)
```

## Code Templates

### Template 1: General Static Step

```python
step_name = 'Static-Step'
initial_inc = 0.1
max_inc = 0.5
min_inc = 1e-05
max_num_inc = 100
nlgeom = ON

model = mdb.models['Model-1']

model.StaticStep(
    name=step_name,
    previous='Initial',
    description='Static analysis step',
    timePeriod=1.0,
    initialInc=initial_inc,
    minInc=min_inc,
    maxInc=max_inc,
    maxNumInc=max_num_inc,
    nlgeom=nlgeom,
    amplitude=RAMP
)
```

### Template 2: Linear Static Step

```python
model.StaticStep(
    name='Linear-Static',
    previous='Initial',
    description='Linear static analysis',
    timePeriod=1.0,
    initialInc=1.0,
    minInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF,
    amplitude=RAMP
)

# Set solver
model.steps['Linear-Static'].setValues(
    solutionTechnique=FULL_NEWTON,
    matrixStorage=UNSYMMETRIC
)
```

### Template 3: Nonlinear Static Step

```python
model.StaticStep(
    name='Contact-Step',
    previous='Initial',
    description='Static analysis with contact',
    timePeriod=1.0,
    initialInc=0.01,
    minInc=1e-08,
    maxInc=0.1,
    maxNumInc=10000,
    nlgeom=ON,
    amplitude=STEP
)

# Set convergence control
model.steps['Contact-Step'].setValues(
    solutionTechnique=FULL_NEWTON,
    convertSDI=CONVERT_SDI_OFF,
    matrixSolver=DIRECT,
    matrixStorage=UNSYMMETRIC
)
```

### Template 4: Buckling Step

```python
# Preload step
model.StaticStep(
    name='Preload',
    previous='Initial',
    nlgeom=OFF
)

# Buckling analysis step
model.BuckleStep(
    name='Buckle-Step',
    previous='Preload',
    numEigen=10,
    vectors=16,
    maxIterations=50
)
```

### Template 5: Modal Analysis Step

```python
num_modes = 10
min_frequency = 0.0
max_frequency = 10000.0

model.FrequencyStep(
    name='Modal-Step',
    previous='Initial',
    description='Natural frequency extraction',
    eigenSolver=LANCZOS,
    numEigen=num_modes,
    minEigen=min_frequency,
    maxEigen=max_frequency,
    vectors=20,
    maxIterations=100
)
```

### Template 6: Transient Dynamic Analysis

```python
time_period = 1.0
initial_inc = 0.001

model.DynamicImplicitStep(
    name='Transient-Step',
    previous='Initial',
    description='Transient dynamic analysis',
    timePeriod=time_period,
    initialInc=initial_inc,
    minInc=1e-08,
    maxInc=0.01,
    maxNumInc=100000,
    nlgeom=ON,
    application=MODERATE_DISSIPATION,
    amplitude=RAMP
)
```

### Template 7: Heat Transfer Step

```python
# Steady-state heat transfer
model.HeatTransferStep(
    name='Steady-Thermal',
    previous='Initial',
    description='Steady state heat transfer',
    response=STEADY_STATE,
    maxNumInc=1000,
    initialInc=1.0,
    minInc=1e-05,
    maxInc=1.0,
    deltmx=100.0
)

# Transient heat transfer
model.HeatTransferStep(
    name='Transient-Thermal',
    previous='Initial',
    description='Transient heat transfer',
    response=TRANSIENT,
    timePeriod=3600.0,
    maxNumInc=10000,
    initialInc=60.0,
    minInc=0.01,
    maxInc=300.0,
    deltmx=50.0
)
```

### Template 8: Coupled Thermal-Stress Step

```python
model.CoupledTempDisplacementStep(
    name='Thermal-Stress',
    previous='Initial',
    description='Coupled thermal-stress analysis',
    timePeriod=1.0,
    maxNumInc=10000,
    initialInc=0.1,
    minInc=1e-08,
    maxInc=0.5,
    deltmx=10.0,
    cetol=0.001,
    nlgeom=ON
)
```

## Field Output Requests

### Common Output Variables

```python
# Full output
full_variables = (
    'S', 'E', 'PE', 'PEEQ', 'PEEQT',
    'LE', 'U', 'V', 'A',
    'RF', 'CF', 'P', 'CSTRESS', 'CDISP',
    'NT', 'TEMP', 'HFL',
    'ENER', 'ELEN', 'EVOL', 'EMASS'
)

# Standard output
standard_variables = ('S', 'E', 'U', 'RF', 'PEEQ')

# Minimal output
minimal_variables = ('S', 'U')
```

### Setting Field Output

```python
# Create field output request
model.FieldOutputRequest(
    name='Field-Output',
    createStepName='Step-1',
    variables=('S', 'E', 'U', 'RF', 'PEEQ'),
    frequency=LAST_INCREMENT,
    region=MODEL,
    sectionPoints=DEFAULT,
    rebar=EXCLUDE
)

# Output every N increments
model.FieldOutputRequest(
    name='Field-Output-Freq',
    createStepName='Step-1',
    variables=('S', 'U'),
    frequency=10
)

# Specified time output
model.FieldOutputRequest(
    name='Field-Output-Time',
    createStepName='Step-1',
    variables=('S', 'U'),
    timeInterval=0.1
)
```

## History Output Requests

```python
# Create set
assembly = model.rootAssembly
region = assembly.Set(name='Monitor-Node', nodes=((instance.nodes[0],)))

# Create history output
model.HistoryOutputRequest(
    name='History-Output',
    createStepName='Step-1',
    variables=('U1', 'U2', 'U3', 'RF1', 'RF2', 'RF3'),
    region=region,
    frequency=1
)
```

## Solver Controls

```python
step_obj = model.steps['Step-1']

# Set solution technique
step_obj.setValues(
    solutionTechnique=FULL_NEWTON,
    convertSDI=CONVERT_SDI_OFF,
    matrixSolver=DIRECT,
    matrixStorage=SYMMETRIC,
    matrixStorageFreq=1
)

# Set convergence control
step_obj.setValues(
    initialInc=0.1,
    minInc=1e-08,
    maxInc=0.5,
    maxNumInc=1000,
    maxLineSearchIterations=20,
    extrapolation=LINEAR
)
```

## Best Practices

1. **Initial Increment Selection**:
   - Linear analysis: initialInc = 1.0
   - Simple nonlinearity: initialInc = 0.1
   - Complex contact: initialInc = 0.01

2. **Nonlinear Diagnostics**:
   - Reduce initialInc when convergence is difficult
   - Use automatic stabilization
   - Consider step-by-step loading

3. **Output Control**:
   - Large models: reduce output variables, increase output interval
   - Debugging phase: increase output frequency

4. **Unit Check**:
   - timePeriod and increment units should be consistent with time-dependent loads
