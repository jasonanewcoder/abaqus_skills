# Abaqus Subroutine Skills Library Manual

## Table of Contents

1. [Overview](#overview)
2. [Skill Library Structure](#skill-library-structure)
3. [Usage Guide](#usage-guide)
4. [Example Tutorials](#example-tutorials)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What is the Abaqus Subroutine Skills Library?

This skill library is an AI-assisted programming guide specifically designed for Abaqus user subroutine development. It provides standardized Fortran code templates, detailed theoretical explanations, and complete engineering examples to help users quickly and accurately develop custom subroutines.

### Skill Library Coverage

| Subroutine Type | Function | Analysis Type |
|-----------------|----------|---------------|
| UMAT | Custom material constitutive | Standard (Implicit) |
| VUMAT | Custom material constitutive | Explicit |
| DLOAD | Distributed load definition | Standard |
| VDLOAD | Distributed load definition | Explicit |
| DISP | Custom displacement boundary | Standard |
| VDISP | Custom displacement boundary | Explicit |
| USDFLD | Custom field variables | General |
| SIGINI | Initial stress definition | General |
| SDVINI | Initial state variables | General |
| FRIC | Custom friction | Standard |
| VRIC | Custom friction | Explicit |
| HETVAL | Heat generation | Thermal analysis |
| FILM | Custom convection | Thermal analysis |
| UEL | Custom element | Standard |
| VUEL | Custom element | Explicit |

### Skill Library Features

1. **Legality Guarantee**: All code strictly follows Abaqus subroutine interface specifications
2. **Correctness Verification**: Each template has been theoretically verified and numerically tested
3. **Layered Design**: Progressive from entry-level to advanced
4. **Ready to Use**: Code can be directly copied and used, only parameters need modification
5. **Theoretical Support**: Includes complete mathematical formulas and physical background

---

## Skill Library Structure

```
abaqus_subroutine_skills/
├── SKILL.md                     # Main skill file (Claude Code format)
├── manual.md                    # This manual (English default)
├── manual_zh.md                 # Chinese version manual
├── README.md                    # Bilingual README
├── README_zh.md                 # Chinese README
├── reference/                   # Reference documentation
│   ├── material/
│   │   ├── umat_elastic.md     # Linear elastic UMAT
│   │   ├── umat_plasticity.md  # Elastoplastic UMAT
│   │   └── vumat_elastic.md    # Linear elastic VUMAT
│   ├── load/
│   │   └── dload_moving.md     # Moving load
│   ├── boundary/
│   │   └── disp_control.md     # Custom displacement
│   ├── field/
│   │   └── usdfld_spatial.md   # Spatial field variables
│   ├── initial/
│   │   └── sigini_stress.md    # Initial stress
│   ├── thermal/
│   │   └── hetval_heat.md      # Heat generation
│   ├── friction/
│   │   └── fric_contact.md     # Custom friction
│   └── element/
│       └── uel_spring.md      # Nonlinear spring
└── official_examples/           # Official Abaqus examples
    ├── umat/
    ├── vumat/
    ├── dload/
    └── ...
```

---

## Usage Guide

### Step 1: Determine Requirements

Before using the skill library, clarify:

1. **Analysis Type**: Implicit (Standard) or Explicit?
2. **Physical Phenomenon**: What material behavior or boundary condition needs simulation?
3. **Coupling Requirements**: Do multiple subroutines need to work together?
4. **Complexity**: Linear or highly nonlinear problem?

### Step 2: Select Skill File

Based on requirements, select the corresponding skill file:

| Your Requirement | Recommended Skill File |
|-----------------|----------------------|
| Custom material model | `reference/material/umat_*.md` |
| Moving/variable load | `reference/load/dload_moving.md` |
| Vibration/displacement control | `reference/boundary/disp_control.md` |
| Spatially inhomogeneous material | `reference/field/usdfld_spatial.md` |
| Geostress/residual stress | `reference/initial/sigini_stress.md` |
| Tribology problems | `reference/friction/fric_contact.md` |
| Thermal-mechanical coupling | `reference/thermal/hetval_heat.md` + UMAT |
| Special connection elements | `reference/element/uel_spring.md` |

### Step 3: Read Skill File

Each skill file contains:

1. **Skill Description**: Applicable scenarios and main functions
2. **Theoretical Formulas**: Mathematical basis and physical models
3. **Interface Definition**: Detailed subroutine parameter descriptions
4. **Code Template**: Complete, ready-to-use Fortran code
5. **Input File Example**: Abaqus keyword reference
6. **Verification Methods**: How to verify implementation correctness
7. **Extension Suggestions**: Directions for further development

### Step 4: Modify and Adapt

Modify the code for your specific problem:

```fortran
C  Modify material parameter section
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      E  = PROPS(1)    ! Modify to your parameter name
      NU = PROPS(2)
      YOUR_PARAM = PROPS(3)  ! Add new parameter
```

### Step 5: Compile and Test

#### Compilation Commands

```bash
# Windows environment
abaqus make library=your_subroutine.f

# Or run job directly
abaqus job=your_job user=your_subroutine.f interactive
```

#### Testing Recommendations

1. **Single Element Test**: Verify constitutive relationship correctness
2. **Simple Boundary Condition Test**: Verify subroutine is correctly called
3. **Benchmark Comparison**: Verify numerical accuracy
4. **Convergence Test**: Verify Jacobian matrix correctness

### Step 6: Debug and Optimize

#### Common Debugging Methods

```fortran
C  Add debug output (note: affects performance)
      WRITE(*,*) 'DEBUG: NOEL=', NOEL, ' STRESS=', STRESS(1)
```

#### Using Abaqus/Viewer to Check Results

```python
# Python script to check state variables
from odbAccess import openOdb
odb = openOdb(path='your_job.odb')
lastFrame = odb.steps['your_step'].frames[-1]
sdv = lastFrame.fieldOutputs['SDV1']
print('Max SDV1:', max([v.data for v in sdv.values]))
```

---

## Example Tutorials

### Example 1: Linear Elastic UMAT (Entry Level)

**Objective**: Create the simplest UMAT to verify interface correctness

**File**: `reference/material/umat_elastic.md`

**Target Audience**: First-time Abaqus subroutine users

**Key Learning Points**:
- UMAT interface structure
- Fortran fixed format rules
- Jacobian matrix assembly
- Stress update algorithm

**Expected Result**: Consistent with Abaqus built-in elastic material

**Difficulty**: ★☆☆☆☆

### Example 2: Moving Wheel Load (Intermediate)

**Objective**: Simulate moving wheel load on bridge deck

**File**: `reference/load/dload_moving.md`

**Target Audience**: Engineers needing to simulate moving loads

**Key Learning Points**:
- DLOAD subroutine working mechanism
- Comprehensive use of time and coordinates
- Spatial distributed load definition
- Dynamic analysis setup

**Expected Result**: Bridge deck produces dynamic response varying with vehicle position

**Difficulty**: ★★★☆☆

### Example 3: Thermal-Mechanical Coupling Analysis (Advanced)

**Objective**: Implement multi-physics coupling for composite curing process

**File**: `reference/thermal/hetval_heat.md` + UMAT

**Target Audience**: Researchers needing multi-physics coupling analysis

**Key Learning Points**:
- Multiple subroutine coordination
- State variable transfer between subroutines
- Thermal-mechanical coupling analysis setup
- Complex physical process simulation

**Expected Result**: Coupled evolution of temperature, cure degree, and stress fields

**Difficulty**: ★★★★★

---

## Best Practices

### Code Standards

1. **Use Fixed-Format Fortran**:
   - Columns 1-5: Statement labels
   - Column 6: Continuation character (non-zero)
   - Columns 7-72: Code body
   - After column 73: Ignored

2. **Variable Declaration**:
```fortran
      REAL*8 E, NU, STRESS(6)    ! Use REAL*8 instead of REAL
      INTEGER I, J, NDI          ! Explicitly declare all variables
```

3. **Constant Definition**:
```fortran
      REAL*8 PI
      PARAMETER(PI=3.141592653589793D0)  ! Use D0 for double precision
```

4. **Error Checking**:
```fortran
C  Parameter range check
      IF (E .LE. 0.0D0) THEN
        WRITE(*,*) 'ERROR: Young modulus must be positive'
        CALL XIT    ! Terminate analysis
      END IF
```

### Performance Optimization

1. **Vectorization for Explicit Subroutines**:
   - VUMAT/VUEL use block loops
   - Avoid scalar operations

2. **Minimize State Variables**:
   - Only store necessary history variables
   - Clean up unused variables promptly

3. **Optimize Matrix Operations**:
   - Utilize matrix symmetry
   - Avoid redundant calculations

### Subroutine Selection Guide

| Problem Type | Recommended Solution | Alternative |
|--------------|---------------------|-------------|
| New constitutive model | UMAT/VUMAT | Built-in material + field variables |
| Moving load | DLOAD/VDLOAD | Multi-node concentrated forces |
| Complex boundary | DISP/VDISP | MPC constraints |
| Non-uniform material | USDFLD+UMAT | Multi-layer material |
| Initial stress | SIGINI | *Initial Conditions |
| Special element | UEL/VUEL | Multi-node connectors |

---

## Troubleshooting

### Compilation Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Unexpected end of file" | Continuation format error | Check column 6 continuation character |
| "Undefined variable" | Variable not declared | Add type declaration |
| "Type mismatch" | Type inconsistency | Use REAL*8 instead of REAL |
| "Dimension mismatch" | Array dimension error | Check array declaration and access |

### Runtime Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Too many attempts" | Non-convergence | Check Jacobian matrix |
| "Negative eigenvalues" | Stiffness matrix not positive definite | Check material stability |
| "Zero pivot" | Insufficient constraints | Check boundary conditions |
| "NaN in stress" | Numerical overflow | Check division by zero and exponential operations |

### Result Anomalies

| Symptom | Possible Cause | Check Point |
|---------|----------------|-------------|
| Zero stress | STRESS not updated | Check stress update statements |
| Excessive displacement | Stiffness too small | Check material parameter units |
| Non-convergence | Inconsistent Jacobian | Verify DDSDDE derivation |
| Hourglass modes | Reduced integration | Add hourglass control |

### Debugging Tips

1. **Output Intermediate Results**:
```fortran
      IF (NOEL .EQ. 1 .AND. NPT .EQ. 1) THEN
        WRITE(*,*) 'Step:', KSTEP, 'Inc:', KINC
        WRITE(*,*) 'Stress:', (STRESS(I), I=1,6)
      END IF
```

2. **Single Step Analysis**:
```abaqus
*Step, name=Debug
*Static
1.0, 1.0, 1.0e-5, 1.0
```

3. **Comparison Testing**:
   - Compare with built-in materials
   - Compare with theoretical solutions
   - Compare with literature results

---

## Reference Resources

### Abaqus Official Documentation

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26
- Abaqus Example Problems Guide

### Recommended Books

1. Simo & Hughes, "Computational Inelasticity"
2. Dunne & Petrinic, "Introduction to Computational Plasticity"
3. Belytschko et al., "Nonlinear Finite Elements"

### Online Resources

- Abaqus Learning Community
- SIMULIA Knowledge Base

---

## Version Information

- Skill Library Version: 1.0
- Compatible Abaqus Version: 2020 and above
- Fortran Compiler: Intel Fortran 19.0+ or GNU Fortran 9.0+
- Last Updated: 2026-03-20

---

## Contributions and Feedback

Contributions are welcome through:
- Submitting new skill files
- Reporting code errors
- Providing improvement suggestions
- Sharing usage experience

---

**Note**: Please ensure you are familiar with basic Abaqus operations and Fortran programming basics before using this skill library. For complex problems, it is recommended to first verify subroutine correctness on small-scale models.
