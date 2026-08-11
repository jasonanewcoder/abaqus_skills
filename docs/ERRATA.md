# Errata & Known Issues — Abaqus Skills Library

This document records **confirmed errors that were fixed**, and **items that could not be
verified without a local Abaqus installation** (static review only). It exists so that
AI agents and users know exactly where the documentation may still deviate from their
specific Abaqus version.

Last reviewed: 2026-08 (Abaqus 2023/2024/2025 era, Python 3.9/3.10)

---

## 1. Confirmed and Fixed (do not reintroduce)

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 1 | `subroutine_skills/reference/material/umat_plasticity.md` | Radial return used wrong plastic multiplier: `DEQPL = (q_trial−σ_y)/(2G + 2H/3)` and `DGAMMA = 1.5·DEQPL`; stress did not return to the yield surface; consistent tangent inconsistent | Rewritten with Newton iteration `Δε̄ ← Δε̄ + R/(3G + H)`, `R = q_trial − 3G·Δε̄ − σ_y(ε̄ₙ+Δε̄)`, official-style tangent `EFFG = EG·σ_y/q`; aligned with `official_examples/umat/umat_mises_plasticity_official.f` |
| 2 | `material.md`, `general/SKILL.md`, `linear.md`, `nonlinear.md` | `Density(table=((x),))` — inner `(x)` is not a tuple; Abaqus requires rows of rows | `Density(table=((x,),))` everywhere |
| 3 | `material.md`, `thermal/SKILL.md`, `transient.md`, `steady_state.md` | Specific-heat conversion `× 1e9` — correct factor is **`× 1e6`** (1 J/(kg·K) = 1e6 N·mm/(tonne·K)); error was 1000× | `specific_heat * 1e6` |
| 4 | `material.md` (bilinear template) | First `*Plastic` data point used total strain `σ_y/E` — first point must be **zero plastic strain** | First point `(σ_y, 0.0)`, subsequent points use plastic strain |
| 5 | `general/SKILL.md`, `static/SKILL.md`, `linear.md`, `high_cycle.md`, `layup_definition.md`, `transient.md`, 3 × `cross_module_examples/*.py` | `'MISES'` is not a valid **field output** (ODB) variable (valid only for `.dat` print / history); requesting it in `FieldOutputRequest` fails | Removed; Mises is computed in post-processing from `S` (see `postprocess_odb.md`) |
| 6 | `bc_load.md` | `Gravity` components are **actual accelerations**, not unit vectors: `comp2=-1.0` gave ~0 gravity; also `region` was missing | `comp2=-9800.0` (mm/s²) + `region`; `BodyForce` example corrected to ρ·g (N/mm³) |
| 7 | `job.md` | Restart attributes were placed on `mdb.Job` (not real API) — restart belongs to the **Model**: `restartJob/restartStep/restartIncrement` via `Model.setValues()`; submodel used hallucinated `submodel=True, submodelJob=` | Rewritten: `mdb.Model(objectToCopy=...)` + `setValues(restartJob=...)`; `mdb.Job(..., globalModel='Global-Job')` + model-level `SubmodelBC` |
| 8 | `step.md` | `matrixStorageFreq`, `maxLineSearchIterations` are not `StaticStep` parameters | Removed; line-search control noted as `*SOLUTION CONTROLS` |
| 9 | `thermal/reference/steady_state.md` | `filmCoeff=15e-6` (mW/mm²·K) — conversion W/(m²·K) → mW/(mm²·K) is `×1e-3`, not `×1e-6` | `15e-3` (both occurrences) |
| 10 | `transient.md` | `h_conv = 15e-6` same unit error | `15e-3` |
| 11 | `subroutine_skills/reference/material/vumat_elastic.md` | Spin sign opposite to official example; code assumed `ndir=3` (broken for plane stress); ignored that Explicit passes **deviatoric** stress; input file used SI units (7850.0 kg/m³, 210e9 Pa) | Rewritten verbatim from official example incl. `trace/3` recovery, official rotation formulas, ndir note; input file now `7.85e-9`, `210000.0` |
| 12 | `subroutine_skills/reference/load/dload_moving.md` | `TOTAL_PATH` never computed (clamped to 0); `PROPS` reference (DLOAD has no PROPS); SI unit comments; incomplete `*Amplitude, USER` input example | Compute `TOTAL_PATH = Σ SEG_LEN`, guard `NSEG < 2`, COMMON-block note, N-mm-MPa units, simplified `*Dload` example |
| 13 | `subroutine_skills/reference/thermal/film_convection.md` | `×1e-6` conversion for W/(m²·K) → mW/(mm²·K) | `×1e-3` |
| 14 | `subroutine_skills/reference/thermal/hetval_heat.md` | Cure example used SI (J/kg, kg/m³); `SIGMA_Y`, `K`, `N_HARD` implicitly INTEGER under `ABA_PARAM.INC` (I–N range) — `N_HARD = 0.3` would truncate to 0; input file used kg/m³ | Converted to N-mm-MPa (4.0e11 N·mm/tonne, 1.5e-9 tonne/mm³, MPa stresses); all locals explicitly declared |
| 15 | `subroutine_skills/reference/initial/sigini_stress.md` | SI units in geostatic (`N/m³`), tendon (`m²`), welding (`m`, `Pa`) examples | N-mm-MPa equivalents (`2e-5 N/mm³`, `500 mm²`, `200 MPa`, mm widths) |
| 16 | `subroutine_skills/reference/element/uel_spring.md` | `N/m`, `N/m³`, `m`, `N·s/m` unit comments | `N/mm`, `N/mm³`, `mm`, `N·s/mm` |
| 17 | `subroutine_skills/reference/boundary/disp_control.md`, `friction/fric_contact.md` | SI unit comments (m, m/s) | mm / mm/s values |
| 18 | `mesh.md` | `part.quality` is not a Part attribute | `part.verifyMesh()` |
| 19 | `modeling.md` | `CutSweep(pathEdge=...)` — parameter is `path` | `CutSweep(path=..., sketch=...)` |

---

## 2. Unverified — check against your Abaqus version (flagged during static review)

These could not be confirmed without a live Abaqus; treat as *verify before production use*:

| Location | Item | What to check |
|----------|------|---------------|
| `xfem/reference/crack_initiation.md` | `model.XFEMCrack(..., interaction=ON, contact=OFF)` | Whether `interaction`/`contact` are accepted keyword args for `XFEMCrack` in your version (may be version-dependent) |
| `xfem/reference/crack_initiation.md` | `material.maxpsDamageInitiation.DamageStabilizationCohesion(viscosity=...)` | Method name/args (`DamageStabilization` may differ) |
| `xfem/reference/crack_initiation.md` | `ContourIntegral(crackFront=Region(faces=...), crackTip=...)` | Crack front must be an edge/node set, not a face region — verify selection type |
| `bc_load.md` | `BoltLoad(preloadType=DEPENDENT, ...)` | `preloadType` validity for BoltLoad in your version |
| `bc_load.md` | `Temperature(distributionType=FROM_FILE, beginStep=0, ...)` | Step indexing (0- vs 1-based) and exact param names |
| `static/reference/nonlinear.md`, `linear.md` | Full scripts | Verify end-to-end on a local Abaqus install |
| `general/reference/modeling.md` | `BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF)` | Param names may differ slightly across versions |
| `thermal/reference/transient.md`, `steady_state.md` | `FilmCondition(definition=EMBEDDED_COEFF, ...)`, `Radiation(...)`, `BodyHeatFlux(...)` | Verify param sets on your version |

---

## 3. Known design limitations (accepted, documented)

- **No automated tests** — all templates must be validated in Abaqus before production use.
- **Python target**: Abaqus 2023+ / Python 3.9+ (f-strings used). Abaqus ≤ 2022 (Python 2.7)
  is **not** supported by the current templates.
- Fortran code is **fixed-format** (cols 1–5 labels, col 6 continuation, 7–72 code);
  continuation lines follow the official examples (`     1 ...` with the digit in column 6).
- Subroutine parameter passing between multiple subroutines uses COMMON blocks — the docs
  show the pattern but each project must manage its own blocks.
