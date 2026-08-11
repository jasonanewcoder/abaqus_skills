# Verification & Validation — Detailed Reference

## Overview

Confirms an analysis is correct BEFORE trusting it. Two levels:
1. **Code-level**: run the same model with the built-in material vs UMAT, or compare to
   an analytical solution (benchmarks below)
2. **Result-level**: energy balance, mesh convergence, load path sanity

> 中文提示：每次给用户「出结果」前，先跑 3 个检查：① 解析解/经验值对照
> （下表可直接用）② 能量平衡（ALLIE/ALLAE/ALLKE）③ 网格收敛性。
> 这能把「看起来对」变成「验证过」。

## Template 0: Single-Element Test (quickest correctness check)

For material models (incl. UMAT), test with ONE C3D8R element under uniaxial stress:

```python
part = model.Part(name='Elem-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=10.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(1.0, 1.0))
part.BaseSolidExtrude(sketch=sketch, depth=1.0)

# one element mesh
part.seedPart(size=1.0)
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=STRUCTURED)
part.generateMesh()
assert len(part.elements) == 1

# uniaxial tension: fix one face, displace the opposite by d
# expected stress = E * (d / L)  (elastic), compare UMAT vs built-in
```

Check: stress matches theory to machine precision; `STATEV` evolves correctly; no
warnings about Jacobian in `.msg`.

## Benchmark 1: Cantilever Beam (bending)

Cantilever length `L`, width `b`, height `h`, tip load `P` (N), E in MPa:

```
Tip deflection:   δ = P·L³ / (3·E·I)          I = b·h³/12
Max bending stress at fixed end (top/bottom): σ = M·c / I = (P·L)·(h/2) / I
```

Use at least 10 elements along the length and 4 through the height; expect agreement
within 1–2% for C3D8R (better with C3D8I/C3D20R).

**Python snippet to compare against ODB:**

```python
P, L, b, h, E = 5000.0, 1000.0, 50.0, 100.0, 210000.0
I = b * h**3 / 12.0
delta_theory = P * L**3 / (3 * E * I)          # mm
sigma_theory = P * L * (h / 2) / I             # MPa
```

## Benchmark 2: Thick-Walled Cylinder (Lame, plane strain)

Internal pressure `p`, inner radius `a`, outer radius `b`:

```
Hoop stress at inner wall:  σ_θ(a) = p·(a² + b²)/(b² − a²)
Radial stress at inner wall: σ_r(a) = −p
```

Check `S11/S22/S33` at the inner surface against these (element coordinate system).

## Benchmark 3: Thermal — 1D Steady Conduction

Plate of thickness `t` (mm), conductivity `k` (mW/(mm·K)), faces at `T1` and `T2` (°C):

```
Heat flux q = k·(T1 − T2)/t           (mW/mm²)
Mid-plane temperature = (T1 + T2)/2
```

## Benchmark 4: Natural Frequency (spring-mass / cantilever)

Cantilever first natural frequency:

```
ω₁ = (1.8751)² · sqrt(E·I/(ρ·A·L⁴))      f₁ = ω₁/(2π)
```

Compare `FrequencyStep` output with `*Frequency` eigenfrequencies.

## Benchmark 5: Plasticity — Uniaxial Stress-Strain

Perfectly plastic (yield `σ_y`): uniaxial stress must plateau at `σ_y` after yield.

Isotropic hardening power law `σ = σ₀ + K·ε̄ⁿ`:
- after the elastic limit, the uniaxial curve must follow
  `σ = σ₀ + K·(ε_total − σ/E)ⁿ` exactly (this validates the UMAT radial return).

## Mesh Convergence Procedure

```python
# Run 3 meshes: coarse → medium → fine (halve element size each time)
# Track the quantity of interest (e.g. max Mises, max deflection)

results = {}   # mesh_size -> value
for size in (20.0, 10.0, 5.0):
    ... build & run ...
    results[size] = max_mises

# Check convergence: |value_fine − value_medium| / value_fine < 2–5%
# If NOT converged: continue refining; if oscillating: suspect singularity or element issue
```

Rule of thumb: the finest mesh change < 5% ⇒ converged for engineering purposes.

## Energy Balance Checks

| Check | Condition | Where |
|-------|-----------|-------|
| Quasi-static (implicit static) | `ALLKE << ALLIE` (kinetic < 1% typically) | ODB history `Assembly ASSEMBLY` |
| Hourglass | `ALLAE < 5% ALLIE` | ODB |
| Stabilization | `ALLVD < 5% ALLIE` | ODB |
| Explicit energy | `ETOTAL ≈ constant` (work in = internal + kinetic + dissipated) | ODB |
| Reaction balance | `Σ RF ≈ applied load` (static equilibrium) | ODB, RF on constrained sets |

## Unit Sanity Check (before running anything)

| Quantity | N-mm-MPa value for "typical" steel beam | Note |
|----------|------------------------------------------|------|
| E | 210000 MPa | NOT 2.1e11 (that's Pa) |
| Density | 7.85e-9 tonne/mm³ | NOT 7850 (kg/m³) |
| Specific heat | 460 × 1e6 = 4.6e8 N·mm/(tonne·K) | NOT 460 × 1e9 |
| Gravity | 9800 mm/s² | NOT 9.81 |
| Thermal conductivity | 45 mW/(mm·K) | value unchanged from W/(m·K) |

Use `scripts/unit_converter.py` for arbitrary conversions.

## Reporting Template (agent → user)

```
Model summary:
  - Geometry/parts, material(s), BCs, loads, mesh (element type, count)
  - Step setup (type, increments)
Key results:
  - Max displacement = X mm (at ...)
  - Max Mises = Y MPa (at ...)
  - Max reaction force = Z N (support check)
Verification:
  - Cantilever benchmark: theory δ = ..., FE δ = ..., diff = 1.2% ✓
  - Energy: ALLKE/ALLIE = 0.4% ✓ ; ALLAE/ALLIE = 2.1% ✓
  - Mesh convergence: 20/10/5 mm → 42.1/43.3/43.5 MPa (converged) ✓
Warnings: [list any solver warnings and whether they matter]
```

## Related

- `postprocess_odb.md` — how to extract the numbers above
- `error_diagnosis.md` — when numbers look wrong, where to look
- `scripts/odb_extract.py` — CLI for extracting max values
