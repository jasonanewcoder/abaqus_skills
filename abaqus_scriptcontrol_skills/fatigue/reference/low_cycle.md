# Low-Cycle Fatigue & Strain-Life — Detailed Reference

## Skill Description

Low-cycle fatigue (LCF): large cyclic plastic strains, life in the range
10²–10⁵ cycles. Predicted with the **Coffin-Manson / Morrow strain-life law** from
strain amplitudes, or with the **energy-based** approach. In Abaqus, LCF work is
typically: run a cyclic elasto-plastic analysis → extract strain amplitudes →
post-process with the strain-life law (or hand the results to fe-safe).

> 中文提示：低周疲劳用应变幅-寿命曲线（Coffin-Manson），需要先做弹塑性
> 循环分析得到局部应变幅。与高周(S-N)法的区别：低周考虑塑性应变，寿命短。

## Theoretical Foundation

### Coffin-Manson (total strain amplitude)

```
ε_a = (σ'f/E)·(2Nf)^b + ε'f·(2Nf)^c
```

| Symbol | Meaning | Typical (steel) |
|--------|---------|-----------------|
| σ'f | Fatigue strength coefficient | 1000 MPa |
| b | Fatigue strength exponent | −0.085 |
| ε'f | Fatigue ductility coefficient | 0.5 |
| c | Fatigue ductility exponent | −0.6 |
| 2Nf | Reversals to failure | — |

Morrow mean-stress correction:

```
ε_a = ((σ'f − σ_m)/E)·(2Nf)^b + ε'f·(2Nf)^c
```

### Neubur / local strain approach (notch)

For notched parts, Neuber: `Kt²·S·e = σ·ε` — solve iteratively for local σ-ε from
the nominal stress range; then apply the strain-life law. Abaqus gives the local
σ-ε directly if the notch is modeled.

## Workflow in Abaqus

1. **Model**: cyclic loading (e.g. displacement or force cycles), elasto-plastic
   material (see `static/reference/nonlinear.md`), refined mesh at the hot spot
2. **Run**: 2–3 full cycles to reach a stabilized hysteresis loop
3. **Extract**: strain components at the hot-spot integration point, per cycle
   (ODB history output — see `postprocess_odb.md`)
4. **Compute**: von Mises equivalent strain range per cycle
5. **Post-process**: Coffin-Manson → life

## Template: Extract Strain Range per Cycle from ODB

```python
from odbAccess import openOdb

odb = openOdb(path='Cyclic-Job.odb', readOnly=True)
region = odb.steps['Cycles'].historyRegions['Element PLATE-1.1 Int Point 1']

# Equivalent total strain (E is the total strain tensor)
E = region.historyOutputs['E']          # if requested as history
# For tensor history output use components: 'E11', 'E22', 'E33', 'E12'...
comps = ['E11', 'E22', 'E33', 'E12', 'E13', 'E23']
data = {c: [d.value for d in region.historyOutputs[c].data] for c in comps}

# Equivalent strain range over the stabilized cycle (max - min per component)
import math
max_eq, min_eq = -1e30, 1e30
for i in range(len(data['E11'])):
    s11, s22, s33 = data['E11'][i], data['E22'][i], data['E33'][i]
    s12, s13, s23 = data['E12'][i], data['E13'][i], data['E23'][i]
    eq = math.sqrt((2.0/9.0) * ((s11-s22)**2 + (s22-s33)**2 + (s33-s11)**2)
                   + (4.0/3.0) * (s12**2 + s13**2 + s23**2))
    max_eq = max(max_eq, eq)
    min_eq = min(min_eq, eq)
deps = max_eq - min_eq                       # strain range per cycle
eps_a = deps / 2.0                           # strain amplitude

# Coffin-Manson: solve for 2Nf
E = 210000.0
sf, b_ = 1000.0, -0.085
ef, c_ = 0.5, -0.6
sig_m = 0.0                                   # mean stress (Morrow)
tol, lo, hi = 1e-9, 1.0, 1e10
while hi - lo > tol:
    mid = (lo + hi) / 2.0
    lhs = (sf - sig_m)/E * mid**b_ + ef * mid**c_
    if lhs > eps_a:
        hi = mid
    else:
        lo = mid
Nf = (lo + hi) / 4.0                          # cycles (2Nf/2)
print(f'Strain amplitude = {eps_a:.6f}, predicted life Nf = {Nf:.0f} cycles')
```

> Note: `E` history output for tensor components requires requesting the tensor
> in history output (`variables=('E', ...)`); component keys like 'E11' appear
> automatically. If not, extract from field output frames instead.

## fe-safe Integration (Abaqus + fe-safe)

fe-safe is Dassault's durability tool — the standard companion for fatigue post-processing:

1. Run the Abaqus job (elastic or elasto-plastic), keep the `.odb`
2. Open fe-safe → load the ODB + material fatigue data (S-N or ε-N curves)
3. Assign load histories (e.g. the cycle time-history from the Abaqus step)
4. Compute life → fe-safe writes a `.odb` with life/usage factor results
5. Import the life ODB back in Abaqus CAE for contour plots

Key settings: surface finish, size factor, reliability, mean-stress correction
(Goodman/Morrow), multiaxial method (Brown-Miller or Sines).

## Step Setup Notes

```python
# Cyclic step: keep the loading slow enough for quasi-static behavior
model.StaticStep(name='Cycle-1', previous='Initial', nlgeom=OFF,
                 initialInc=0.05, minInc=1e-6, maxInc=0.2,
                 maxNumInc=100000)

# History output at the hot spot element (integration point)
model.HistoryOutputRequest(
    name='HotSpot',
    createStepName='Cycle-1',
    region=hot_spot_element_region,     # element set
    variables=('E', 'S', 'PEEQ'),
    frequency=1
)
```

## Quick Parameters (typical values)

| Material | σ'f (MPa) | b | ε'f | c |
|----------|-----------|-----|------|------|
| Medium-carbon steel | 1000 | −0.085 | 0.5 | −0.60 |
| High-strength steel | 1200 | −0.075 | 0.4 | −0.65 |
| Aluminum 2024-T3 | 700 | −0.080 | 0.25 | −0.55 |

## Related

- `high_cycle.md` — S-N approach (high-cycle complement)
- `static/reference/nonlinear.md` — elasto-plastic cyclic analysis
- `postprocess_odb.md` — history/field extraction
- `verification.md` — validating the strain extraction
