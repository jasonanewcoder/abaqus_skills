# CREEP — Creep / Viscoplastic Material — Detailed Reference

## Skill Description

CREEP defines creep and viscoplastic material behavior for Abaqus Standard
(time-dependent inelastic strain under sustained load). Use it for high-temperature
creep, relaxation, weld residual-stress aging, polymers, and soil creep.

> 中文提示：蠕变分析需要三个量：蠕变应变增量 DCE、等效蠕变应变率 EC、应力对
> 蠕变应变率的导数。金属高温蠕变最常用 Norton 幂律与温度相关形式。

## Interface

```fortran
      SUBROUTINE CREEP(DECRA,DESWA,STATEV,SERD,EC,ESW,P,QTILD,
     1 TEMP,DTEMP,PREDEF,DPRED,TIME,DTIME,CMNAME,LEXIMP,LEND,
     2 COORDS,NSTATV,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION DECRA(5),DESWA(5),STATEV(NSTATV),PREDEF(1),
     1 DPRED(1),TIME(2),COORDS(3)
```

| Argument | Meaning |
|----------|---------|
| DECRA(1) | Output: increment of equivalent creep strain Δε̄ᶜ |
| DECRA(2) | Output: increment of volume change (usually 0) |
| DECRA(3) | Output: dΔε̄ᶜ/dσ̄ (derivative wrt equivalent stress) |
| DECRA(4) | Output: dΔε̄ᶜ/dε̄ᶜ (derivative wrt equivalent creep strain) |
| DECRA(5) | Output: dΔε̄ᶜ/dT (temperature derivative) |
| EC | Output: equivalent creep strain rate ε̄̇ᶜ |
| P | Input: equivalent pressure stress |
| QTILD | Input: equivalent (Mises) stress σ̄ |
| TEMP, DTEMP | Input: temperature / increment |
| TIME, DTIME | Input: time |
| LEXIMP | Input: 1 → implicit (return DECRA(1..5) needed); 0 → explicit |
| STATEV | Input/Output: state variables |

## Template 1: Norton Power Law (steady-state creep)

```fortran
      SUBROUTINE CREEP(DECRA,DESWA,STATEV,SERD,EC,ESW,P,QTILD,
     1 TEMP,DTEMP,PREDEF,DPRED,TIME,DTIME,CMNAME,LEXIMP,LEND,
     2 COORDS,NSTATV,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  Norton:  eps_c_dot = A * sigma^n * exp(-Q/(R*T))
C  PROPS(1)=A (1/(MPa^n·s)), PROPS(2)=n, PROPS(3)=Q (J/mol),
C  PROPS(4)=R (gas constant)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION DECRA(5),DESWA(5),STATEV(NSTATV),PREDEF(1),
     1 DPRED(1),TIME(2),COORDS(3)
C
      REAL*8 A, N, Q, R, T
      REAL*8 RATE, RATE_DSIG
C
      A = PROPS(1)
      N = PROPS(2)
      Q = PROPS(3)
      R = PROPS(4)
      T = TEMP + 273.15D0
C
      IF (QTILD .GT. 1.0D-12) THEN
        RATE = A * (QTILD**N) * EXP(-Q/(R*T))
      ELSE
        RATE = 0.0D0
      END IF
C
      EC = RATE                      ! equivalent creep strain rate (1/s)
      DECRA(1) = RATE * DTIME        ! creep strain increment
      DECRA(2) = 0.0D0
C  d(deps)/d(sigma): A*n*sigma^(n-1)*exp(...)*dt
      IF (QTILD .GT. 1.0D-12) THEN
        DECRA(3) = RATE * N/QTILD * DTIME
      ELSE
        DECRA(3) = 0.0D0
      END IF
C  d(deps)/d(eps_c): 0 for Norton (no primary creep)
      DECRA(4) = 0.0D0
C  d(deps)/dT: RATE * (Q/(R*T^2)) * DTIME
      DECRA(5) = RATE * (Q/(R*T*T)) * DTIME
C
      DESWA(1) = 0.0D0               ! volumetric creep strain increment
      DESWA(2) = 0.0D0
      DESWA(3) = 0.0D0
C
      SERD = QTILD * RATE * DTIME    ! creep dissipation
C
      RETURN
      END
```

## Template 2: Time-Hardening Law (primary + steady creep)

```fortran
      SUBROUTINE CREEP(DECRA,DESWA,STATEV,SERD,EC,ESW,P,QTILD,
     1 TEMP,DTEMP,PREDEF,DPRED,TIME,DTIME,CMNAME,LEXIMP,LEND,
     2 COORDS,NSTATV,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  Time hardening:  eps_c_dot = A * sigma^n * t^m
C  PROPS(1)=A, PROPS(2)=n, PROPS(3)=m
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION DECRA(5),DESWA(5),STATEV(NSTATV),PREDEF(1),
     1 DPRED(1),TIME(2),COORDS(3)
C
      REAL*8 A, N, M, T
      REAL*8 RATE, RATE_DSIG
C
      A = PROPS(1)
      N = PROPS(2)
      M = PROPS(3)
      T = TIME(1)
C
      IF (QTILD .GT. 1.0D-12 .AND. T .GT. 1.0D-12) THEN
        RATE = A * (QTILD**N) * (T**M)
      ELSE
        RATE = 0.0D0
      END IF
C
      EC = RATE
      DECRA(1) = RATE * DTIME
      DECRA(2) = 0.0D0
      IF (QTILD .GT. 1.0D-12) THEN
        DECRA(3) = RATE * N/QTILD * DTIME
      ELSE
        DECRA(3) = 0.0D0
      END IF
      DECRA(4) = 0.0D0
      IF (T .GT. 1.0D-12) THEN
        DECRA(5) = RATE * M/T * DTIME    ! d(deps)/dt for time hardening
      ELSE
        DECRA(5) = 0.0D0
      END IF
C
      DESWA(1) = 0.0D0
      DESWA(2) = 0.0D0
      DESWA(3) = 0.0D0
      SERD = QTILD * RATE * DTIME
C
      RETURN
      END
```

## Input File Example

```abaqus
*Material, name=Steel-HighTemp
*User Material, constants=4
** A (1/(MPa^n·s)), n, Q (J/mol), R (J/mol·K)
1.0e-20, 4.5, 250000.0, 8.314
*Depvar
1
```

## Guidance

1. `DECRA(3..5)` are derivatives for the Newton iteration — wrong derivatives cause
   convergence trouble; for tricky laws return 0.0 (degrades to explicit-like behavior)
2. `QTILD` is the von Mises equivalent stress; avoid dividing by it when zero
3. In coupled temperature-displacement steps, `TEMP` is the current temperature
4. Verify with a uniaxial creep test: εᶜ(t) must match the law's integral
5. Creep + plasticity: define both `*Plastic` (or UMAT) and the creep law — Abaqus
   adds the strain rates (note: UMAT + CREEP combination needs care; the built-in
   `*Creep` under the same material works with `*Plastic`)

## Related

- `umat_plasticity.md` — plasticity (usually combined with creep at high temperature)
- `thermal/reference/transient.md` — thermal-mechanical coupling where creep matters
