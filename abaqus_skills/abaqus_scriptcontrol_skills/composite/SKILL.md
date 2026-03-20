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

**Detailed Documentation:** [`reference/shell.md`](reference/shell.md)

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

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
