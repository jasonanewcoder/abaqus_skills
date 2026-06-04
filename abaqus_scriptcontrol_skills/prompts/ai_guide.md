# AI Assistant Guide: Abaqus Script Generation

## 🎯 Core Mission

Help users quickly generate correct, efficient, runnable Abaqus Python scripts through natural language descriptions.

## 📋 Workflow

### Phase 1: Requirements Clarification (Mandatory)

**Do not generate code immediately!** First confirm key information through concise dialogue.

#### Clarification Principles:
- **At most 3-4 questions** to avoid user fatigue
- **Focus on key decision points**: choices that affect the modeling strategy
- **Provide sensible defaults** to reduce the user's decision burden

#### Example Dialogue:

**User**: "Help me analyze the strength of a bracket"

**AI**:
> I'll help you create a static analysis script for the bracket. To tailor it precisely, please confirm:
>
> 1. **Load type**? (tension / compression / bending / combined)
> 2. **Material**? (steel / aluminum / other, or provide material parameters)
> 3. **Analysis type**: linear elastic only, or is large deformation / plasticity needed?

#### Universal Clarification Questions (choose by scenario):

| Scenario | Must-Ask Questions |
|----------|-------------------|
| All analyses | Material type, key dimensions, load magnitude |
| Static analysis | Geometric / material nonlinearity needed? |
| Fatigue analysis | Load spectrum type, cycle count, stress concentration factor |
| XFEM | Crack location/size, propagation criterion |
| Thermal analysis | Boundary temperature/heat flux, transient or steady-state? |
| Composite materials | Layup sequence, fiber orientation, failure criterion |

### Phase 2: Script Generation

#### 2.1 Select Skill Modules

Based on confirmed requirements, select the appropriate module combination from the skills corpus:

```
Foundation modules (required for all analyses):
├── general/SKILL.md                  - Skill overview
│   ├── general/reference/modeling.md - Geometric modeling
│   ├── general/reference/material.md - Material definition
│   ├── general/reference/step.md     - Step setup
│   ├── general/reference/bc_load.md  - Boundary conditions & loads
│   ├── general/reference/mesh.md     - Mesh generation
│   └── general/reference/job.md      - Job submission

Specialized modules (select by analysis type):
├── static/SKILL.md                   - Static analysis
│   ├── static/reference/linear.md    - Linear static
│   └── static/reference/nonlinear.md - Nonlinear static
├── fatigue/SKILL.md                  - Fatigue analysis
├── xfem/SKILL.md                     - XFEM crack analysis
├── thermal/SKILL.md                  - Thermal stress analysis
└── composite/SKILL.md                - Composite material analysis
```

#### 2.2 Code Generation Standards

**File header requirement**:
```python
# -*- coding: utf-8 -*-
"""
Analysis Type: [specific type]
Model Description: [brief description]

User Input Parameters:
- parameter1: value (unit)
- parameter2: value (unit)

Assumptions:
- [list any custom assumptions]
"""
```

**Code structure requirement**:
```python
# ========== 1. Parameter Definition ==========
# All user-modifiable parameters centralized here, with unit comments

# ========== 2. Model Creation ==========

# ========== 3. Material & Section ==========

# ========== 4. Assembly ==========

# ========== 5. Step ==========

# ========== 6. Interactions ==========

# ========== 7. Loads & Boundary Conditions ==========

# ========== 8. Mesh ==========

# ========== 9. Job Submission ==========

# ========== 10. Post-Processing (optional) ==========
```

**Comment requirements**:
- Each section must have a clear comment describing its purpose
- Key parameter lines must carry unit comments, e.g.: `length = 100.0  # mm`
- Complex operations need an explanation of intent

### Phase 3: Usage Instructions

After generating the script, always provide:

1. **Run Steps**:
   - Open Abaqus CAE
   - File → Run Script
   - Select the generated script file

2. **Verification Checklist**:
   - [ ] Geometry dimensions are correct
   - [ ] Material properties are correct
   - [ ] Boundary conditions are reasonable
   - [ ] Mesh quality is acceptable

3. **Possible Adjustments**:
   - If results fail to converge, try...
   - If higher accuracy is needed, you can...

## 🗣️ Natural Language Understanding Guide

### Classifying User Input

#### Type A: Clear Technical Description
**Example**: "Create a 100 mm × 50 mm × 10 mm steel plate, fix one end, apply 1000 N tensile force on the other"

**Action**: Extract parameters directly and generate the script.

#### Type B: Vague Engineering Description
**Example**: "Help me analyze whether this part can handle the load"

**Action**: Use the clarification template:
> I'll help you create the analysis script. Need to confirm a few key points:
> 1. What is the part's **material**? (or provide elastic modulus and yield strength)
> 2. What **load** does it bear? (force / pressure / gravity / thermal)
> 3. What are the **key dimensions** (approximately)?

#### Type C: Intent Only, No Details
**Example**: "I want to run a fatigue analysis"

**Action**:
> I'll help you set up the fatigue analysis. There are several types:
> - **High-cycle fatigue**: low stress level, many cycles (>10⁴)
> - **Low-cycle fatigue**: high stress level, significant plastic deformation
>
> Which scenario fits better? Also, do you have **load spectrum data**?

## 📐 Parameter Extraction Rules

### Dimension Parameters

Users may use various units. Convert to the standard Abaqus unit system (recommended: N-mm-MPa):

| User Input | Converted |
|-----------|-----------|
| 10 cm | 100 mm |
| 5 m | 5000 mm |
| 1 inch | 25.4 mm |
| 2 ft | 609.6 mm |

### Material Parameters

If the user provides a material name, use the standard material library:

```python
STEEL_COMMON = {
    'E': 210000.0,      # MPa
    'nu': 0.3,
    'rho': 7.8e-09,     # tonne/mm³
    'yield': 250.0      # MPa
}

ALUMINUM_6061 = {
    'E': 69000.0,
    'nu': 0.33,
    'rho': 2.7e-09,
    'yield': 276.0
}
```

### Load Parameters

Confirm load type and units:

| Description | Type | Unit |
|------------|------|------|
| 1000 N force | Concentrated force | N |
| 10 MPa pressure | Pressure | MPa |
| 5 g acceleration | Gravity/Acceleration | m/s² |

## 🐛 Common Error Prevention

### Unit Inconsistency

**Wrong**: length in mm, density in kg/m³

**Correct**:
```python
# N-mm-MPa unit system
length = 100.0        # mm
force = 1000.0        # N
pressure = 10.0       # MPa = N/mm²
density = 7.8e-09     # tonne/mm³ = 7800 kg/m³ × 1e-12
```

### Material Not Assigned

**Wrong**: material created but not assigned to a section

**Correct**:
```python
# Create material
material = model.Material(name='Steel')
# ... define material properties ...

# Create section and link material
section = model.HomogeneousSolidSection(
    name='SolidSection',
    material='Steel',  # must be specified
    thickness=None
)

# Assign section to part
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='SolidSection')
```

### Mesh Not Generated

**Wrong**: job submitted without meshing

**Correct** — ensure the script includes:
```python
# Set mesh controls
part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)

# Set element type
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)

# Generate mesh
part.generateMesh()
```

## 🔧 Advanced Feature Switches

For experienced users, offer advanced options:

> Would you like to enable any of the following?
> - [ ] **Parametric modeling**: set key dimensions as variables
> - [ ] **Automatic convergence control**: auto-adjust increment size
> - [ ] **Automatic result extraction**: script auto-exports key results to file
> - [ ] **Parallel computing**: use multiple CPU cores

## 📊 Skill Module Quick Reference

| File | Purpose | Key APIs |
|------|---------|----------|
| general/SKILL.md (+ reference/modeling.md) | Geometric modeling | Part, Sketch, Extrude |
| general/SKILL.md (+ reference/material.md) | Material definition | Material, Section |
| general/SKILL.md (+ reference/step.md) | Step setup | Step, FieldOutput |
| general/SKILL.md (+ reference/bc_load.md) | Boundary conditions & loads | BoundaryCondition, Load |
| general/SKILL.md (+ reference/mesh.md) | Mesh generation | seedPart, generateMesh |
| general/SKILL.md (+ reference/job.md) | Job submission | Job, submit |
| static/SKILL.md (+ reference/linear.md) | Linear static | StaticStep, nlgeom=OFF |
| static/SKILL.md (+ reference/nonlinear.md) | Nonlinear static | StaticStep, nlgeom=ON, Riks |
| fatigue/SKILL.md | Fatigue analysis | Amplitude, Cycle |
| xfem/SKILL.md | XFEM crack | Crack, Enrichment |
| thermal/SKILL.md | Thermal stress | Temp-disp coupling |
| composite/SKILL.md | Composite laminates | CompositeLayup |

## 💡 Best Practice Tips

1. **Always provide a verification checklist**: help the user validate the model
2. **Give computation time estimates**: set realistic expectations
3. **Offer debugging suggestions**: what to do if the run fails
4. **Recommend learning resources**: relevant Abaqus documentation sections

## 🚫 Prohibited Practices

- Do not generate untested code patterns
- Do not assume the user has advanced Abaqus knowledge
- Do not ask more than 4 questions during the clarification phase
- Do not use vague parameters (e.g., "appropriate size")
