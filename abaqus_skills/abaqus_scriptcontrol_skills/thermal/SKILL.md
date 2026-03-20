# Abaqus Thermal Stress Analysis Skills

## Overview

This skill module provides specialized skills for Abaqus thermal stress analysis to analyze thermal stress and deformation caused by temperature changes. Includes steady-state heat transfer, transient heat transfer, and thermal-mechanical coupling analysis.

## Skills List

### 1. Thermal Stress Analysis (`skill_thermal_stress`)

Analyze thermal stress and deformation caused by temperature changes, including sequential coupling and fully coupled methods.

**Applicable Scenarios:**
- Welding residual stress analysis
- Thermo-mechanical coupled loads
- Deformation caused by temperature gradients
- Thermal shock analysis

**Code Snippet:**

```python
# Heat transfer step
model.HeatTransferStep(
    name='Steady-State',
    previous='Initial',
    response=STEADY_STATE
)

# Thermal expansion material
material.Expansion(table=((expansion_coeff,),))

# Import temperature field from ODB
model.Temperature(
    name='Temp-From-ODB',
    createStepName='Thermal-Stress-Step',
    region=region,
    distributionType=FROM_FILE,
    fileName='thermal_results.odb'
)
```

**Detailed Documentation:** [`reference/stress.md`](reference/stress.md)

---

## Quick Reference

### Unit Conversion

| Physical Quantity | Original Unit | Abaqus Unit |
|------------------|---------------|-------------|
| Thermal Conductivity | W/(m·K) | W/(m·K) |
| Specific Heat | J/(kg·K) | mJ/(tonne·K) × 10^9 |
| Thermal Expansion Coefficient | /°C | /°C |

### Coupling Methods

1. **Sequential Coupling**: Thermal analysis first → Stress analysis second
2. **Fully Coupled**: Simultaneously solve temperature and displacement

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
