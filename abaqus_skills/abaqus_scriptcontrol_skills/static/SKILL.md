# Abaqus Static Analysis Skills

## Overview

This skill module provides specialized skills for Abaqus static analysis, including linear static analysis and nonlinear static analysis. Static analysis is the most commonly used analysis method in engineering to calculate stress, strain, and displacement of structures under static loads.

## Skills List

### 1. Linear Static Analysis (`skill_static_linear`)

Perform linear elastic small-deformation static analysis for stress, strain, and deformation calculation.

**Applicable Scenarios:**
- Small deformation structural analysis (deformation < 5% of characteristic dimension)
- Linear elastic materials (stress < yield strength)
- Stiffness calculation, strength verification
- Displacement and reaction force calculation

**Code Snippet:**

```python
# Create linear static step
model.StaticStep(
    name='Static-Step',
    previous='Initial',
    nlgeom=OFF,           # Disable geometric nonlinearity
    initialInc=1.0,
    maxInc=1.0
)

# Set field output
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Step',
    variables=('S', 'E', 'U', 'RF', 'MISES')
)
```

**Detailed Documentation:** [`reference/linear.md`](reference/linear.md)

---

### 2. Nonlinear Static Analysis (`skill_static_nl`)

Handle complex static problems including geometric nonlinearity, material nonlinearity, and contact nonlinearity.

**Applicable Scenarios:**
- Large deformation analysis (deformation > 5% of characteristic dimension)
- Material plastic analysis
- Contact problems
- Post-buckling analysis

**Code Snippet:**

```python
# Create nonlinear static step
model.StaticStep(
    name='Nonlinear-Step',
    previous='Initial',
    nlgeom=ON,            # Enable geometric nonlinearity
    initialInc=0.05,      # Small initial increment
    minInc=1e-08,
    maxInc=0.1
)

# Set field output (including plastic strain)
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Nonlinear-Step',
    variables=('S', 'E', 'PE', 'PEEQ', 'U', 'RF')
)
```

**Detailed Documentation:** [`reference/nonlinear.md`](reference/nonlinear.md)

---

## Linear vs Nonlinear Static Analysis

| Characteristic | Linear Static Analysis | Nonlinear Static Analysis |
|----------------|------------------------|---------------------------|
| Geometric Nonlinearity | OFF | ON |
| Material Nonlinearity | Elastic | Plastic/Hyperelastic |
| Contact | Tied | Allow relative sliding |
| Incremental Steps | Usually 1 step | Multiple iterative steps |
| Computation Time | Fast | Slower |

## Typical Applications

### Linear Static Analysis Applications

- Structural stiffness analysis
- Simple part strength verification
- Stress concentration analysis
- Symmetric model analysis

### Nonlinear Static Analysis Applications

- Large deformation structures (e.g., rubber seals)
- Plastic forming simulation
- Post-buckling behavior
- Contact problem analysis

## Quick Reference

### Linear Analysis Parameters

| Parameter | Recommended Value |
|-----------|-------------------|
| nlgeom | OFF |
| initialInc | 1.0 |
| maxInc | 1.0 |
| maxNumInc | 1 |

### Nonlinear Analysis Parameters

| Parameter | Recommended Value |
|-----------|-------------------|
| nlgeom | ON |
| initialInc | 0.01 - 0.1 |
| minInc | 1e-08 - 1e-05 |
| maxInc | 0.1 - 0.5 |
| maxNumInc | 100 - 10000 |

### Common Element Types

| Element | Application |
|---------|-------------|
| C3D8R | General solid |
| C3D8I | Bending problems |
| C3D10 | Complex geometry |

## Related Skills

- [General Skills](../general/SKILL.md)
- [Fatigue Analysis](../fatigue/SKILL.md)
- [XFEM Crack Analysis](../xfem/SKILL.md)
- [Thermal Stress Analysis](../thermal/SKILL.md)
