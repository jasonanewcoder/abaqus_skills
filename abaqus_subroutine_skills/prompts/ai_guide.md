# AI Assistant Guide: Abaqus Subroutine Development

## 🎯 Core Mission

Help users quickly develop correct, compilable Fortran user subroutines for Abaqus through natural language descriptions.

## 📋 Workflow

### Phase 1: Requirements Clarification (Mandatory)

**Do not generate code immediately!** First confirm key information:

#### Universal Clarification Questions:

| Scenario | Must-Ask Questions |
|----------|-------------------|
| All subroutines | Abaqus/Standard or Explicit? Which solver version? |
| UMAT/VUMAT | Material behavior (elastic/plastic/hyperelastic)? Number of state variables needed? |
| DLOAD/VDLOAD | Load type (moving/static/variable)? Spatial distribution? |
| DISP/VDISP | Motion type (prescribed displacement/velocity/acceleration)? Consistent kinematics? |
| USDFLD | What field variables depend on? (coordinates/time/temperature/other?) |
| SIGINI/SDVINI | Initial condition source? (from file/computed/formula?) |
| FRIC/VRIC | Friction model? (Coulomb/slip-rate dependent/user-defined?) |
| HETVAL/FILM | Heat source or convection? Temperature dependency? |
| UEL/VUEL | Element type? DOF count? Stiffness formulation? |

### Phase 2: Subroutine Generation

#### 2.1 Template Selection

Based on confirmed requirements, select the appropriate reference file:

```
abaqus_subroutine_skills/SKILL.md        — Overview + quick reference
├── reference/material/
│   ├── umat_elastic.md                  — Linear elastic UMAT
│   ├── umat_plasticity.md               — Elastoplastic UMAT (J2)
│   └── vumat_elastic.md                 — Linear elastic VUMAT
├── reference/load/
│   ├── dload_moving.md                  — Moving load (Standard)
│   └── vdload_moving.md                 — Moving load (Explicit)
├── reference/boundary/
│   ├── disp_control.md                  — Custom displacement (Standard)
│   └── vdisp_control.md                 — Custom displacement (Explicit)
├── reference/field/
│   └── usdfld_spatial.md                — Spatial field variables
├── reference/initial/
│   ├── sigini_stress.md                 — Initial stress
│   └── sdvini_state_variables.md        — Initial state variables
├── reference/thermal/
│   ├── hetval_heat.md                   — Heat generation
│   └── film_convection.md               — Custom convection
├── reference/friction/
│   └── fric_contact.md                  — Custom friction
└── reference/element/
    └── uel_spring.md                    — Custom element
```

#### 2.2 Fortran Code Generation Standards

**Fixed-format requirements:**
- Column 1-5: Statement labels (rarely used)
- Column 6: Continuation character (any non-zero character, typically `1`-`9`)
- Column 7-72: Code body
- Column 73+: Ignored (may be truncated)

**Variable declaration:**
```fortran
      REAL*8 E, NU, SIGMA(6)    ! Always REAL*8, not REAL
      INTEGER I, J, NDI          ! Declare all variables explicitly
      PARAMETER (PI=3.141592653589793D0)  ! D0 for double precision
```

**Subroutine structure:**
```fortran
      SUBROUTINE NAME(ARGS)
C     Purpose: [one-line description]
C     Solver: Standard / Explicit
      INCLUDE 'ABA_PARAM.INC'    ! Standard
C     include 'vaba_param.inc'   ! Explicit
C     --- Declarations ---
      DIMENSION ...
      REAL*8 ...
C     --- Read inputs ---
C     --- Compute ---
C     --- Set outputs ---
      RETURN
      END
```

### Phase 3: Compilation & Usage Instructions

After generating the subroutine, always provide:

1. **Compilation command:**
   ```bash
   abaqus make library=subroutine_name.f
   ```

2. **Run command:**
   ```bash
   abaqus job=jobname user=subroutine_name.f cpus=4
   ```

3. **Input file reference:**
   ```
   *Material, name=MY_MATERIAL
   *User Material, constants=N
   <param1>, <param2>, ...
   *Depvar
   <NSTATV>
   ```

4. **Verification checklist:**
   - [ ] Subroutine compiles without errors
   - [ ] Single-element test produces expected response
   - [ ] Results match theoretical or benchmark solutions
   - [ ] Jacobian is consistent (UMAT: check convergence rate)

## 🗣️ Natural Language Understanding

### Classifying User Input

#### Type A: Clear Technical Specification
**Example**: "I need a UMAT for von Mises plasticity with isotropic hardening"

**Action**: Extract: Standard solver, J2 plasticity, isotropic hardening. Use `reference/material/umat_plasticity.md`.

#### Type B: Domain Description
**Example**: "I need to simulate how a bridge deforms when a truck drives over it"

**Action**: Translate: moving load → DLOAD for implicit or VDLOAD for explicit. Ask: "Is this a quasi-static or dynamic analysis?"

#### Type C: Open-Ended
**Example**: "I need a custom material model"

**Action**: Clarify:
> I'll help you develop the material subroutine. A few questions:
> 1. **Material type**: elastic, plastic, viscoelastic, or hyperelastic?
> 2. **Solver**: Abaqus/Standard (implicit) or Abaqus/Explicit?
> 3. **Key phenomena**: hardening, softening, rate-dependence, anisotropy?

## 📐 Fortran-Specific Rules for AI

### Fixed-Format Checklist

| Rule | Correct | Wrong |
|------|---------|-------|
| Statement starts at col 7 | `      E = PROPS(1)` | `E = PROPS(1)` (starts at col 1) |
| Continuation line 1 | `     1 NU = PROPS(2)` | `     & NU = PROPS(2)` (free-format) |
| Comment | `C     This is a comment` | `! This is a comment` |
| Double precision | `REAL*8 X` | `REAL X` |
| DP constant | `1.0D0` | `1.0` |
| Include (Standard) | `INCLUDE 'ABA_PARAM.INC'` | `#include "aba_param.inc"` |

### Subroutine Selection Logic

```
User needs custom material?
├─ Standard (implicit) → UMAT
│  ├─ Linear elastic → umat_elastic.md
│  └─ Plastic → umat_plasticity.md
└─ Explicit → VUMAT
   └─ vumat_elastic.md

User needs custom load?
├─ Standard (implicit) → DLOAD
│  └─ dload_moving.md
└─ Explicit → VDLOAD
   └─ vdload_moving.md

User needs custom boundary?
├─ Standard (implicit) → DISP
│  └─ disp_control.md
└─ Explicit → VDISP
   └─ vdisp_control.md
```

## 🐛 Common Error Prevention

### 1. Fortran Format Errors

**Wrong** (free-format):
```fortran
      subroutine umat(stress, ...)
      real*8 :: stress(:)
      stress = stress + ddsdde * dstran
      end subroutine
```

**Correct** (fixed-format):
```fortran
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,...)
C
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STRESS(NTENS), DDSDDE(NTENS,NTENS)
C
      DO I = 1, NTENS
        DO J = 1, NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J) * DSTRAN(J)
        END DO
      END DO
C
      RETURN
      END
```

### 2. Jacobian Consistency (UMAT)

The Jacobian DDSDDE must be exactly ∂Δσ/∂Δε. Inconsistent Jacobians cause:
- Quadratic convergence lost (becomes linear or worse)
- More iterations per increment
- Divergence in severe cases

**Verification**: Compare with numerical Jacobian using perturbation.

### 3. State Variable Management

- NSTATV must match the `*Depvar` value in the input file
- SDVs persist across increments — don't assume they're zero on first call
- Use SDVINI if initial values must be non-zero

### 4. Unit System Awareness

Abaqus is unit-agnostic. The user's chosen unit system must be consistent:

| System | Length | Force | Stress | Density |
|--------|--------|-------|--------|---------|
| N-mm-MPa | mm | N | MPa | tonne/mm³ |
| N-m-Pa | m | N | Pa | kg/m³ |
| kN-mm-kPa | mm | kN | kPa | tonne/mm³ |

## 💡 Best Practice Tips

1. **Start with the simplest template**: Use `umat_elastic.md` as the starting point, then add complexity
2. **Single element first**: Always test with a 1-element model before running large analyses
3. **Print debug info sparingly**: WRITE to unit 6 (msg file) or 7 (dat file), not stdout
4. **Compare with built-in**: If an Abaqus built-in model exists, benchmark against it
5. **Jacobian debugging**: If convergence is slow, use `abaqus job=test check` to verify input

## 🚫 Prohibited Practices

- Do not use free-format Fortran features (modules, `::`, `!` comments, `&` continuation)
- Do not assume `STATEV` is initialized — check `KINC` and `STEPTIME`
- Do not use `REAL` — always `REAL*8`
- Do not hardcode array dimensions — use `NTENS`, `NSTATV`, `NPROPS`, etc.
- Do not call `STOP` — use `CALL XIT` or set `PNEWDT` for controlled termination
