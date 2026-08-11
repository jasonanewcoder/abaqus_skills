---
name: abaqus-script-control-thermal
description: >-
  Abaqus thermal analysis: steady-state and transient heat transfer, convection,
  radiation, and sequential / fully-coupled thermal-mechanical (thermal stress)
  analysis, including welding heat input. Use when the task mentions: thermal
  analysis, heat transfer, thermal stress, temperature field, thermal-mechanical
  coupling, welding simulation, conduction, convection, 热分析, 热应力, 温度场.
  Requires abaqus-script-control-general as foundation. Note N-mm-MPa unit
  conversions (specific heat ×1e6).
version: "1.1"
capabilities:
  - steady_state_heat_transfer
  - transient_heat_transfer
  - thermal_mechanical_coupling
  - sequential_coupling
  - fully_coupled_analysis
triggers:
  - "thermal analysis"
  - "heat transfer"
  - "thermal stress"
  - "temperature field"
  - "thermal-mechanical"
  - "welding simulation"
  - "热分析"
  - "热应力"
  - "温度场"
constraints:
  - "Requires general/SKILL.md as foundation"
  - "Thermal properties require unit conversion (specific heat: J/(kg·K) → N·mm/(tonne·K) × 10^6)"
  - "Reference docs: steady_state.md + transient.md (incl. welding)"
---

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

---

## Quick Reference

### Unit Conversion

| Physical Quantity | Original Unit | Abaqus Unit |
|------------------|---------------|-------------|
| Thermal Conductivity | W/(m·K) | W/(m·K) |
| Specific Heat | J/(kg·K) | N·mm/(tonne·K) × 10^6 |
| Thermal Expansion Coefficient | /°C | /°C |

### Coupling Methods

1. **Sequential Coupling**: Thermal analysis first → Stress analysis second
2. **Fully Coupled**: Simultaneously solve temperature and displacement

## Detailed Reference

- [Steady-State Heat Transfer](reference/steady_state.md) — Thermal equilibrium, conduction, convection, radiation BCs
- [Transient Heat Transfer & Thermal-Stress Coupling](reference/transient.md) — Time-varying temperature, sequential and fully-coupled analysis

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
