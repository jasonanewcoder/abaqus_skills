# Abaqus Skills Corpus User Manual

## Table of Contents

1. [Overview](#1-overview)
2. [Usage](#2-usage)
3. [Skill Modules](#3-skill-modules)
4. [Example Tutorials](#4-example-tutorials)

---

## 1. Overview

### 1.1 What is the Abaqus Skills Corpus?

The Abaqus Skills Corpus is a structured Abaqus secondary development knowledge base designed to help users and AI assistants quickly generate high-quality, runnable Abaqus Python scripts. Through modular skill files, users can describe analysis requirements in natural language, and AI automatically combines corresponding skill modules to generate complete code.

### 1.2 Core Functions

| Function Module | Description | Included Skills |
|----------------|-------------|----------------|
| **General Skills** | Basic operations for all analysis types | Modeling, Materials, Boundary Conditions, Mesh, Job Submission |
| **Static Analysis** | Structural response under static loads | Linear Analysis, Large Deformation/Plastic Analysis |
| **Fatigue Analysis** | Life prediction under cyclic loads | High-cycle fatigue (S-N curve), Damage accumulation |
| **XFEM Analysis** | Crack initiation and propagation simulation | Extended Finite Element Method, Damage evolution |
| **Thermal Analysis** | Temperature field and thermal stress calculation | Steady/Transient heat transfer, Thermal-mechanical coupling |
| **Composite Materials** | Laminated plate structure analysis | Layup definition, Failure criteria |

### 1.3 Target Users

- **Engineers**: Quickly generate standard analysis scripts, reduce repetitive work
- **Researchers**: Use as starting templates for complex analyses
- **Students**: Learn best practices for Abaqus scripting
- **AI Assistants**: Provide structured knowledge base for accurate code generation

### 1.4 Key Advantages

1. **Modular Design**: Skills can be freely combined to suit different analysis needs
2. **Ready to Use**: Each skill file contains directly runnable code templates
3. **Best Practices**: Follows Abaqus-recommended modeling procedures and parameter settings
4. **Error Prevention**: Includes common error warnings and solutions
5. **Progressive Learning**: Examples from simple to complex help users master skills gradually

---

## 2. Usage

### 2.1 Using with AI Assistants

#### Step 1: Describe Requirements

Describe your analysis requirements in natural language, for example:

> "I need to analyze a cantilever beam under end load for stress and deformation. Beam length is 1m, cross-section is 50mm x 100mm rectangular, material is Q235 steel, end load is 5000N."

#### Step 2: AI Clarification

Based on the `prompts/ai_guide.md` guide in the skills corpus, AI will confirm key information through concise dialogue:

> Confirm a few questions:
> 1. Is the analysis type linear elastic static analysis?
> 2. What mesh density is needed?
> 3. Which variables need to be saved in the results?

#### Step 3: Generate Script

AI combines corresponding modules from the skills corpus based on confirmed requirements:

- Get modeling code from [`general/SKILL.md`](general/SKILL.md)
- Get material definition from [`general/reference/material.md`](general/reference/material.md)
- Get static analysis settings from [`static/SKILL.md`](static/SKILL.md)

#### Step 4: Run and Verify

Save the generated script as a `.py` file and run it in Abaqus:

```
File → Run Script → Select script file
```

### 2.2 Using Skill Files Directly

#### Method A: Copy Code Templates

1. Open the corresponding skill's SKILL.md file (e.g., [`general/SKILL.md`](general/SKILL.md))
2. Find the required function module
3. View code templates in the [`reference/`](general/reference/) directory
4. Copy to your script and modify parameters

#### Method B: Combine Multiple Skills

```python
# Import Abaqus modules
from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Modeling (reference general/reference/modeling.md) ==========
# ... copy modeling code ...

# ========== 2. Material (reference general/reference/material.md) ==========
# ... copy material code ...

# ========== 3. Step (reference general/reference/step.md) ==========
# ... copy step code ...

# ... other steps ...
```

### 2.3 File Search Quick Reference

| Want to do | Check file |
|------------|------------|
| Create geometric model | [`general/SKILL.md`](general/SKILL.md) → [`reference/modeling.md`](general/reference/modeling.md) |
| Define material properties | [`general/SKILL.md`](general/SKILL.md) → [`reference/material.md`](general/reference/material.md) |
| Set up steps and output | [`general/SKILL.md`](general/SKILL.md) → [`reference/step.md`](general/reference/step.md) |
| Apply boundary conditions and loads | [`general/SKILL.md`](general/SKILL.md) → [`reference/bc_load.md`](general/reference/bc_load.md) |
| Generate mesh | [`general/SKILL.md`](general/SKILL.md) → [`reference/mesh.md`](general/reference/mesh.md) |
| Submit analysis job | [`general/SKILL.md`](general/SKILL.md) → [`reference/job.md`](general/reference/job.md) |
| Static analysis (linear) | [`static/SKILL.md`](static/SKILL.md) → [`reference/linear.md`](static/reference/linear.md) |
| Static analysis (nonlinear) | [`static/SKILL.md`](static/SKILL.md) → [`reference/nonlinear.md`](static/reference/nonlinear.md) |
| Fatigue analysis | [`fatigue/SKILL.md`](fatigue/SKILL.md) |
| Crack analysis (XFEM) | [`xfem/SKILL.md`](xfem/SKILL.md) |
| Thermal stress analysis | [`thermal/SKILL.md`](thermal/SKILL.md) |
| Composite material analysis | [`composite/SKILL.md`](composite/SKILL.md) |

### 2.4 Common Parameters Quick Reference

#### Unit System

| Physical Quantity | N-mm-MPa System |
|-------------------|-----------------|
| Length | mm |
| Force | N |
| Stress | MPa |
| Elastic Modulus | MPa |
| Density | tonne/mm³ |
| Gravitational Acceleration | 9800 mm/s² |

#### Material Parameters (Common)

| Material | E (MPa) | ν | Density (tonne/mm³) | Yield Strength (MPa) |
|----------|---------|---|---------------------|---------------------|
| Q235 Steel | 210000 | 0.3 | 7.85e-09 | 235 |
| Q345 Steel | 210000 | 0.3 | 7.85e-09 | 345 |
| Aluminum 6061 | 69000 | 0.33 | 2.70e-09 | 276 |

---

## 3. Skill Modules

### 3.1 General Skills (general/)

General skills are the foundation for all analysis types:

- **Geometric Modeling** ([`modeling.md`](general/reference/modeling.md)): Create parts, sketch drawing, feature operations
- **Material Definition** ([`material.md`](general/reference/material.md)): Elastic, plastic, hyperelastic materials
- **Step Setup** ([`step.md`](general/reference/step.md)): Static, dynamic, thermal steps
- **Boundary Conditions & Loads** ([`bc_load.md`](general/reference/bc_load.md)): Displacement constraints, forces, pressures, temperature loads
- **Mesh Generation** ([`mesh.md`](general/reference/mesh.md)): Element type selection, mesh controls
- **Job Submission** ([`job.md`](general/reference/job.md)): Job creation, submission, monitoring

### 3.2 Static Analysis (static/)

- **Linear Static Analysis** ([`linear.md`](static/reference/linear.md)): Small deformation, linear elastic
- **Nonlinear Static Analysis** ([`nonlinear.md`](static/reference/nonlinear.md)): Large deformation, plasticity, contact

### 3.3 Fatigue Analysis (fatigue/)

- **High-cycle Fatigue**: Life prediction based on S-N curves

### 3.4 XFEM Crack Analysis (xfem/)

- **Crack Initiation and Propagation**: Extended Finite Element Method, damage criteria

### 3.5 Thermal Stress Analysis (thermal/)

- **Thermal Stress Analysis**: Steady/Transient heat transfer, thermal-mechanical coupling

### 3.6 Composite Material Analysis (composite/)

- **Laminate Analysis**: Layup definition, Hashin failure criteria

---

## 4. Example Tutorials

### Example 1: Simple Cantilever Beam Analysis (Beginner)

**Difficulty**: ⭐ (Simple)  
**Goal**: Master the most basic analysis workflow  
**Skills involved**: Modeling → Material → Boundary conditions → Load → Mesh → Job

#### Scenario Description

A rectangular cross-section cantilever beam, fixed end fully constrained, free end subjected to vertical downward concentrated force. Calculate stress and deformation.

#### Key Parameters

- Beam length: 1000 mm
- Cross-section: 50 mm × 100 mm
- Material: Q235 steel
- Load: 5000 N

#### Complete Script

```python
# -*- coding: utf-8 -*-
"""
Example 1: Simple Cantilever Beam Analysis (Beginner)
Analysis Type: Linear Elastic Static Analysis
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== Parameter Definition ==========
length = 1000.0      # mm
width = 50.0         # mm
height = 100.0       # mm

E = 210000.0         # MPa
nu = 0.3

load = 5000.0        # N

# ========== Create Model ==========
model = mdb.Model(name='Cantilever-Beam')

# Create beam (extrusion)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(width, height))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=length)
del model.sketches['__profile__']

# ========== Material and Section ==========
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
section = model.HomogeneousSolidSection(name='Section', material='Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section')

# ========== Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== Step ==========
model.StaticStep(name='Load-Step', previous='Initial', nlgeom=OFF)

# ========== Boundary Conditions (Fixed End) ==========
fixed_face = instance.faces.findAt(((width/2, height/2, 0.0),))
region = assembly.Set(name='Fixed', faces=fixed_face)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=region)

# ========== Load (Free End Concentrated Force) ==========
load_face = instance.faces.findAt(((width/2, height/2, length),))
region = assembly.Set(name='Load', faces=load_face)
model.ConcentratedForce(name='Force', createStepName='Load-Step',
                        region=region, cf2=-load)

# ========== Mesh ==========
part.seedPart(size=20.0)
part.setMeshControls(regions=(part.cells,), elemShape=HEX)
elem_type = mesh.ElemType(elemCode=C3D8R)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== Job ==========
job = mdb.Job(name='Beam-Job', model='Cantilever-Beam')
job.submit()
job.waitForCompletion()

print("Analysis completed!")
```

#### Theoretical Verification

- Maximum bending stress (theoretical): σ = M·y/I = 30 MPa
- Maximum deflection (theoretical): δ = FL³/(3EI) = 2.86 mm
- Compared with FEM results, error should be < 5%

---

### Example 2: Stress Concentration Analysis of Plate with Hole (Intermediate)

**Difficulty**: ⭐⭐ (Intermediate)  
**Goal**: Learn local mesh refinement, result post-processing  
**Skills involved**: Geometry cutting → Local refinement → Stress extraction → Theoretical comparison

See [examples/example_pressure_vessel.md](examples/example_pressure_vessel.md) for details.

---

### Example 3: Thermal Stress Coupling Analysis of Pressure Vessel (Advanced)

**Difficulty**: ⭐⭐⭐ (Advanced)  
**Goal**: Master multi-physics field coupling analysis, sequential coupling method  
**Skills involved**: Heat transfer → Temperature field transfer → Thermal stress → Result comparison

See [thermal/SKILL.md](thermal/SKILL.md) for details.

---

## 5. CLI Code Skill Format Description

This skills corpus is organized according to Claude Code's Skill format:

### Directory Structure

Each skill category contains:

- **SKILL.md**: Main skill file, including:
  - Skill overview
  - Function list (each function corresponds to detailed documentation in reference)
  - Code snippets
  - Quick reference

- **reference/**: Detailed reference documentation directory, including:
  - Complete API reference
  - Detailed code templates
  - Best practices
  - Common errors and solutions

### Usage Suggestions

1. First view SKILL.md to understand the overall functionality and structure of the skill
2. According to needs, dive into detailed documentation in the reference directory
3. Copy code templates and modify parameters according to specific requirements
4. Follow best practices to avoid common errors
