# Abaqus Fatigue Analysis Skills

## Overview

This skill module provides specialized skills for Abaqus fatigue analysis, including high-cycle fatigue and low-cycle fatigue analysis. Fatigue analysis is used to predict the fatigue life of structures under cyclic loading.

## Skills List

### 1. High-Cycle Fatigue Analysis (`skill_fatigue_high_cycle`)

High-cycle fatigue life prediction based on S-N curves, applicable for cyclic loads with stress levels below yield strength.

**Applicable Scenarios:**
- Stress level σ_max < σ_y (yield strength)
- Number of cycles N > 10^4 ~ 10^6
- Fatigue problems dominated by elastic deformation

**Code Snippet:**

```python
# S-N curve parameters
Sf_prime = 1000.0    # Fatigue strength coefficient (MPa)
b = -0.085          # Fatigue strength exponent
Se = 200.0          # Fatigue limit (MPa)

# Basquin's equation for life calculation
# S = Sf * (2N)^b
log_2N = (log_S - log_Sf) / b
cycles_to_failure = int(10**log_2N / 2)
```

**Detailed Documentation:** [`reference/high_cycle.md`](reference/high_cycle.md)

---

## Quick Reference

### S-N Curve Parameters (Typical Values)

| Material | Sf' (MPa) | b | Se (MPa) |
|----------|-----------|---|----------|
| Steel | 1000 | -0.085 | 200 |
| Aluminum Alloy | 500 | -0.110 | 150 |

### Influencing Factors

| Factor | Effect |
|--------|--------|
| Surface Roughness | Reduces fatigue strength |
| Size Effect | Larger sizes reduce strength |
| Load Type | Bending > Tension/Compression > Torsion |

## Related Skills

- [General Skills](../general/SKILL.md)
- [Static Analysis](../static/SKILL.md)
