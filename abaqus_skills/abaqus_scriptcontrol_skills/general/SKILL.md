# Abaqus General Skills

## Overview

This skill module provides core general skills for Abaqus Python scripting development, including geometric modeling, material definition, step setup, boundary conditions and loads, mesh generation, and job submission. These skills form the foundation for any type of Abaqus analysis.

## Skills List

### 1. Geometric Modeling (`skill_modeling`)

Create geometric parts in Abaqus models, including sketch-based extrusion, revolution, sweep, and other modeling methods.

**Core Functions:**
- Basic geometry creation (blocks, cylinders, tubes, spheres, etc.)
- Sketch drawing (points, lines, circles, arcs, polygons)
- Geometry operations (cutting, filleting, chamfering, shelling, mirroring, patterning)

**Code Snippet:**

```python
# Create 3D solid part
model = mdb.Model(name='Model-1')
part = model.Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# Create sketch and extrude
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part.BaseSolidExtrude(sketch=sketch, depth=height)
```

**Detailed Documentation:** [`reference/modeling.md`](reference/modeling.md)

---

### 2. Material Definition (`skill_material`)

Define material properties and create section properties, assigning materials to geometric parts.

**Core Functions:**
- Linear elastic material definition
- Plastic material (ideal elastic-plastic, bilinear hardening)
- Hyperelastic material (Mooney-Rivlin)
- Orthotropic material
- Shell/Beam sections
- Thermal properties

**Code Snippet:**

```python
# Create isotropic linear elastic material
material = model.Material(name='Steel')
material.Elastic(table=((210000.0, 0.3),))  # E, nu
material.Density(table=((7.85e-09),))       # tonne/mm³

# Create section and assign
section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')
```

**Detailed Documentation:** [`reference/material.md`](reference/material.md)

---

### 3. Step Setup (`skill_step`)

Define step types, output requests, solver controls, etc.

**Core Functions:**
- Static steps (linear/nonlinear)
- Buckling steps
- Modal steps
- Transient dynamic steps
- Heat transfer steps
- Field output/History output requests

**Code Snippet:**

```python
# Create static step
model.StaticStep(
    name='Static-Step',
    previous='Initial',
    initialInc=0.1,
    maxInc=0.5,
    nlgeom=ON
)

# Set field output
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Step',
    variables=('S', 'E', 'U', 'RF', 'MISES')
)
```

**Detailed Documentation:** [`reference/step.md`](reference/step.md)

---

### 4. Boundary Conditions and Loads (`skill_bc_load`)

Define boundary conditions (displacement constraints) and external loads (forces, pressures, temperatures, etc.).

**Core Functions:**
- Fixed constraints, symmetry constraints, specified displacements
- Concentrated forces, distributed pressures
- Gravity/Acceleration loads
- Temperature loads
- Bolt pretension
- Amplitude curves

**Code Snippet:**

```python
# Create fixed constraint
fixed_faces = instance.faces.findAt(((0.0, 25.0, 10.0),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0, u2=0.0, u3=0.0
)

# Create pressure load
model.Pressure(
    name='Load-Pressure',
    createStepName='Step-1',
    region=region,
    magnitude=10.0
)
```

**Detailed Documentation:** [`reference/bc_load.md`](reference/bc_load.md)

---

### 5. Mesh Generation (`skill_mesh`)

Define mesh control parameters, set element types, and generate finite element mesh.

**Core Functions:**
- Automatic/Structured/Sweep/Free mesh
- Local mesh refinement
- Element type selection (solid/shell/beam)
- Mesh quality check

**Code Snippet:**

```python
# Set mesh control (hexahedral)
part.setMeshControls(
    regions=(part.cells,),
    elemShape=HEX,
    technique=STRUCTURED
)

# Set seeds and element type
part.seedPart(size=5.0)
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))

# Generate mesh
part.generateMesh()
```

**Detailed Documentation:** [`reference/mesh.md`](reference/mesh.md)

---

### 6. Job Submission (`skill_job`)

Create analysis jobs, set solver parameters, submit calculations, and monitor job status.

**Core Functions:**
- Basic job submission
- Parallel computation setup
- Memory optimization
- Restart analysis
- Submodel analysis
- Job monitoring and diagnostics

**Code Snippet:**

```python
# Create and submit job
job = mdb.Job(
    name='Analysis-Job',
    model='Model-1',
    numCpus=4,
    numDomains=4
)
job.submit()
job.waitForCompletion()

# Check status
if job.status == COMPLETED:
    print("Analysis completed successfully!")
```

**Detailed Documentation:** [`reference/job.md`](reference/job.md)

---

## Quick Reference

### Common Unit System (N-mm-MPa)

| Physical Quantity | Unit |
|------------------|------|
| Length | mm |
| Force | N |
| Stress | MPa |
| Elastic Modulus | MPa |
| Density | tonne/mm³ |
| Gravitational Acceleration | 9800 mm/s² |

### Common Material Parameters

| Material | E (MPa) | ν | Density (tonne/mm³) | Yield Strength (MPa) |
|----------|---------|---|---------------------|---------------------|
| Q235 Steel | 210000 | 0.3 | 7.85e-09 | 235 |
| Q345 Steel | 210000 | 0.3 | 7.85e-09 | 345 |
| Aluminum 6061 | 69000 | 0.33 | 2.70e-09 | 276 |

### Common Element Types

| Element Code | Description | Applicable Scenario |
|-------------|-------------|---------------------|
| C3D8R | Hexahedral linear reduced integration | General solid analysis |
| C3D10 | Tetrahedral second order | Complex geometry free mesh |
| S4R | Reduced integration shell | General shell analysis |
| B31 | Linear beam | Beam structure analysis |

---

## Usage Suggestions

1. **Modular Construction**: Use skill modules from this library to build complete scripts
2. **Parametric Design**: Set geometric dimensions and material parameters as variables
3. **Verify Before Running**: Generate input file first to check for errors before submitting
4. **Result Check**: After calculation, check msg and dat files to confirm no errors

## Related Skills

- [Static Analysis](../static/SKILL.md)
- [Fatigue Analysis](../fatigue/SKILL.md)
- [XFEM Crack Analysis](../xfem/SKILL.md)
- [Thermal Stress Analysis](../thermal/SKILL.md)
- [Composite Material Analysis](../composite/SKILL.md)
