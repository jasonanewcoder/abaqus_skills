---
name: abaqus-script-control-composite
description: >-
  Abaqus composite analysis: laminated shell (S4R) and continuum shell (SC8R)
  layups, classical laminate theory, Hashin/Puck/LaRC failure criteria,
  progressive damage, Tsai-Wu interactive failure index, per-ply post-processing.
  Use when the task mentions: composite analysis, laminate, layup, ply, Hashin
  failure, Tsai-Wu, fiber failure, matrix failure, delamination, 复合材料,
  层合板, 铺层. Requires abaqus-script-control-general as foundation.
version: "1.1"
capabilities:
  - composite_layup_definition
  - laminate_stiffness_analysis
  - hashin_failure_criteria
  - progressive_damage
  - fiber_matrix_failure
triggers:
  - "composite analysis"
  - "laminate"
  - "layup"
  - "Hashin failure"
  - "fiber failure"
  - "matrix failure"
  - "composite material"
  - "复合材料"
  - "层合板"
  - "铺层"
constraints:
  - "Requires general/SKILL.md as foundation"
  - "Reference docs: layup_definition.md, failure_analysis.md, tsaiwu_continuum_shell.md"
  - "Composite analysis requires orthotropic material properties (LAMINA type)"
---

# Abaqus Composite Material Analysis Skills

## Overview

This skill module provides specialized skills for Abaqus composite material analysis, including laminated plate structure analysis, failure criteria, and progressive damage simulation.

## Skills List

### 1. Composite Laminate Analysis (`skill_composite_shell`)

Analyze the stiffness, strength, and failure of multi-layer composite laminates using Classical Laminate Theory (CLT).

**Applicable Scenarios:**
- Aircraft structures (wings, fuselage)
- Wind turbine blades
- Automotive body panels
- Marine structures

**Code Snippet:**

```python
# Layup definition: (angle°, thicknessmm)
layup = [
    (0, 0.25), (45, 0.25), (-45, 0.25), (90, 0.25),
    (90, 0.25), (-45, 0.25), (45, 0.25), (0, 0.25),
]

# Orthotropic material
material.Elastic(
    type=LAMINA,
    table=((E1, E2, nu12, G12, G13, G23),)
)

# Create composite layup
compositeLayup = part.CompositeLayup(...)

for i, (angle, thickness) in enumerate(layup):
    compositeLayup.CompositePly(
        name=f'Ply-{i+1}',
        region=region,
        material='T300-5208',
        thicknessType=SPECIFY_THICKNESS,
        thickness=thickness,
        orientationType=SPECIFY_ORIENT,
        orientationValue=angle
    )
```

---

## Quick Reference

### Layup Angles

| Angle | Direction | Application |
|-------|-----------|-------------|
| 0° | Along reference direction | Axial load bearing |
| 90° | Perpendicular to reference direction | Transverse stiffness |
| ±45° | Bias | Shear stiffness |

### Failure Criteria

| Criteria | Description |
|----------|-------------|
| Hashin | Distinguishes fiber and matrix failure |
| Puck | Considers angular effects |
| LaRC | More accurate but complex |

### Failure Indices

- HSNFTCRT > 1: Fiber tension failure
- HSNFCCRT > 1: Fiber compression failure
- HSNMTCRT > 1: Matrix tension failure
- HSNMCCRT > 1: Matrix compression failure

## Detailed Reference

- [Laminate Layup Definition](reference/layup_definition.md) — Classical Laminate Theory, orthotropic lamina properties, programmatic layup creation, per-ply post-processing
- [Failure Analysis](reference/failure_analysis.md) — Hashin/Puck/LaRC criteria, progressive damage, damage variable interpretation, strength data
- [Tsai-Wu & Continuum Shells](reference/tsaiwu_continuum_shell.md) — interactive failure index, SC8R layups, per-ply Tsai-Wu post-processing

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
