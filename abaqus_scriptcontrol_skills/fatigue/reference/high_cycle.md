# High-Cycle Fatigue Analysis — Detailed Reference

## Overview

High-cycle fatigue analysis predicts fatigue life for structures under cyclic loading where stress levels remain below the material yield strength (typically N > 10⁴ cycles). Based on the S-N curve (Wöhler curve) approach.

## Applicable Scenarios

- Stress amplitude σ_a < yield strength σ_y (elastic-dominated)
- Number of cycles to failure N_f > 10⁴
- Constant or variable amplitude loading
- Rotating machinery, bridges, aircraft structures

## Theoretical Foundation

### Basquin's Equation (S-N Curve)

```
σ_a = σ_f' × (2N_f)^b
```

| Symbol | Meaning | Unit |
|--------|---------|------|
| σ_a | Stress amplitude | MPa |
| σ_f' | Fatigue strength coefficient | MPa |
| N_f | Cycles to failure | — |
| b | Fatigue strength exponent | — |

### Mean Stress Correction

**Goodman correction:**
```
σ_a / σ_ar + σ_m / σ_u = 1
```

**Gerber correction:**
```
σ_a / σ_ar + (σ_m / σ_u)² = 1
```

**Soderberg correction:**
```
σ_a / σ_ar + σ_m / σ_y = 1
```

Where σ_m = mean stress, σ_ar = fully-reversed fatigue strength, σ_u = ultimate tensile strength.

### Miner's Rule (Cumulative Damage)

```
D = Σ (n_i / N_fi)
```

Failure occurs when D ≥ 1.0.

## Complete Script Template

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: High-Cycle Fatigue Analysis
Description: S-N curve based fatigue life prediction with mean stress correction
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# Geometry
length = 100.0       # mm
width = 20.0         # mm
thickness = 5.0      # mm

# Material (Aluminum 6061-T6)
E = 69000.0          # MPa
nu = 0.33

# Fatigue parameters
Sf_prime = 900.0     # MPa, fatigue strength coefficient
b = -0.11            # fatigue strength exponent
Su = 310.0           # MPa, ultimate tensile strength
Sy = 276.0           # MPa, yield strength

# Loading
sigma_max = 150.0    # MPa, maximum applied stress
sigma_min = 0.0      # MPa, minimum applied stress
R = sigma_min / sigma_max  # stress ratio

# ========== 2. Create Model ==========
model_name = 'Fatigue-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# Create specimen geometry
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part = model.Part(name='Specimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=thickness)
del model.sketches['__profile__']

# ========== 3. Material & Section ==========
material = model.Material(name='Al6061-T6')
material.Elastic(table=((E, nu),))

section = model.HomogeneousSolidSection(name='Section-1', material='Al6061-T6')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Specimen-1', part=part, dependent=ON)

# ========== 5. Step ==========
model.StaticStep(
    name='Static-Load',
    previous='Initial',
    nlgeom=OFF,
    initialInc=1.0,
    maxInc=1.0
)

model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Load',
    variables=('S', 'E', 'U', 'MISES')
)

# ========== 6. Boundary Conditions ==========
# Fix left end
fixed_face = instance.faces.findAt(((0.0, width/2, thickness/2),))
fixed_region = assembly.Set(name='Fixed-End', faces=fixed_face)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=fixed_region)

# ========== 7. Load ==========
# Apply reference stress on right end
load_face = instance.faces.findAt(((length, width/2, thickness/2),))
load_region = assembly.Set(name='Load-End', faces=load_face)

# Reference area and force
area = width * thickness  # mm²
force = sigma_max * area  # N

model.ConcentratedForce(
    name='Load-Tensile',
    createStepName='Static-Load',
    region=load_region,
    cf1=force
)

# ========== 8. Mesh ==========
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=2.0)
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 9. Job Submission ==========
job_name = 'Fatigue-Job'
job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit()
job.waitForCompletion()

# ========== 10. Fatigue Life Calculation ==========
import math

# Extract maximum stress from results
# (In practice, use odbAccess to read actual stress)
sigma_max_actual = sigma_max  # Replace with actual FEA result

# Calculate stress amplitude and mean stress
sigma_a = (sigma_max_actual - sigma_min) / 2.0
sigma_m = (sigma_max_actual + sigma_min) / 2.0

# Goodman mean stress correction
sigma_ar = sigma_a / (1.0 - sigma_m / Su)

# Basquin's equation: N_f = 0.5 * (sigma_ar / Sf_prime)^(1/b)
if sigma_ar > 0 and sigma_ar < Sf_prime:
    N_f = 0.5 * (sigma_ar / Sf_prime) ** (1.0 / b)
    print(f"Predicted fatigue life: {N_f:.0f} cycles")
    print(f"Stress amplitude (corrected): {sigma_ar:.2f} MPa")
elif sigma_ar >= Sf_prime:
    print("Stress exceeds fatigue strength — low-cycle fatigue regime")
    N_f = 0.5 * (sigma_ar / Sf_prime) ** (1.0 / b)
else:
    print("Infinite life (stress below fatigue limit)")
    N_f = float('inf')

print("Fatigue analysis completed!")
```

## S-N Curve Data (Typical Values)

| Material | σ_f' (MPa) | b | Endurance Limit (MPa) | Cycles at Endurance |
|----------|-----------|-----|----------------------|---------------------|
| Steel (Q235) | 1000 | -0.085 | 200 | 10⁶ |
| Steel (Q345) | 1100 | -0.085 | 250 | 10⁶ |
| Aluminum 6061 | 900 | -0.110 | 150 | 5×10⁸ |
| Titanium Ti-6Al-4V | 1400 | -0.095 | 500 | 10⁷ |

## Stress Concentration Factors

```python
# Stress concentration factor K_t lookup
STRESS_CONC_FACTORS = {
    'hole_in_plate': 3.0,     # Circular hole in wide plate
    'shoulder_fillet': 2.5,   # Stepped shaft with fillet
    'notch_v': 4.0,           # Sharp V-notch
    'groove_u': 2.0,          # U-shaped circumferential groove
}

# Notch sensitivity (Peterson's formula)
def notch_sensitivity(r, Su):
    """r = notch radius (mm), Su = ultimate strength (MPa)"""
    a = 0.0254 * (2070.0 / Su) ** 1.8  # Peterson's constant
    q = 1.0 / (1.0 + a / r)
    return q

# Fatigue notch factor
# K_f = 1 + q * (K_t - 1)
```

## Variable Amplitude Loading — Rainflow Counting

```python
def rainflow_counting(stress_history):
    """
    Simplified rainflow counting for stress history.
    stress_history: list of (max, min) tuples for each cycle.
    Returns list of (amplitude, mean, cycles).
    """
    cycles = []
    for smax, smin in stress_history:
        amplitude = (smax - smin) / 2.0
        mean = (smax + smin) / 2.0
        cycles.append((amplitude, mean, 1))
    return cycles

def miner_damage(rainflow_results, Sf_prime, b, Su):
    """Calculate cumulative damage using Miner's rule."""
    total_damage = 0.0
    for amplitude, mean, n in rainflow_results:
        # Goodman correction
        amplitude_corrected = amplitude / (1.0 - mean / Su)
        N_f = 0.5 * (amplitude_corrected / Sf_prime) ** (1.0 / b)
        total_damage += n / N_f
    return total_damage
```

## Influencing Factors

| Factor | Effect on Fatigue Strength | Correction Approach |
|--------|---------------------------|---------------------|
| Surface roughness | Reduces strength (mirror → rough: up to 50% reduction) | Surface factor k_a |
| Size effect | Larger parts have lower strength | Size factor k_b |
| Loading type | Bending > Axial > Torsion | Load factor k_c |
| Temperature | Elevated temperature reduces strength | Temperature factor k_d |
| Reliability | Higher reliability requires lower stress | Reliability factor k_e |
| Notch effect | Stress concentration reduces life | K_f (fatigue notch factor) |

## Verification Checklist

- [ ] Stress amplitude < yield strength (high-cycle regime)
- [ ] S-N curve data matches material grade and heat treatment
- [ ] Mean stress correction method selected appropriately
- [ ] Stress concentration factors accounted for
- [ ] Surface finish and environment considered
- [ ] Cumulative damage < 1.0 for required service life

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Fatigue life too short | Stress concentration not modeled | Refine mesh at notches, apply K_f |
| Unrealistic infinite life | Mean stress effect ignored | Apply Goodman/Gerber correction |
| Scatter in predictions | Natural variability of fatigue data | Use reliability factors (e.g., 95% survival) |
| Wrong fatigue regime | Stress above yield strength | Use low-cycle fatigue (ε-N) approach |

## References

- Stephens, Fatemi, Stephens & Fuchs, "Metal Fatigue in Engineering"
- Dowling, "Mechanical Behavior of Materials"
- Abaqus Analysis User's Guide — Fatigue Analysis
