# DFLUX — Moving Heat Source (Welding / Laser) — Detailed Reference

## Skill Description

DFLUX defines a distributed heat flux (mW/mm³ volumetric, or mW/mm² surface) as a
function of position and time — the standard way to model **moving heat sources**
(welding, laser cladding, friction stir heat input) in Abaqus Standard.

> 中文提示：焊接热源模拟 = DFLUX（热输入）+ 热传导分析 + 后续应力分析。
> 最常用的是 Goldak 双椭球热源，见下方模板 2。

## Interface

```fortran
      SUBROUTINE DFLUX(FLUX,SOL,JSTEP,JINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
C  FLUX(1): heat flux (mW/mm³ for volumetric JLTYP=0, or mW/mm² for surface)
C  FLUX(2): rate of change of flux with respect to temperature dF/dT
C  SOL:    solution dependent variable (temperature at the point)
C  JLTYP:  load type: 0 = volumetric body flux, 1 = surface flux
```

| Argument | Meaning |
|----------|---------|
| FLUX(1) | Output: heat flux magnitude (volumetric or surface) |
| FLUX(2) | Output: dFLUX/dT (used in Newton iterations; 0.0 if independent of T) |
| SOL | Input: temperature at integration point |
| JLTYP | Input: 0 → volumetric body flux (mW/mm³); 1 → surface flux (mW/mm²) |
| COORDS | Input: coordinates of the integration point (mm) |
| TIME(2) | Input: step time / total time (s) |
| TEMP, PRESS | Input: temperature / pressure at the point |

## Template 1: Volumetric Heat Source (simple Gaussian ball)

```fortran
      SUBROUTINE DFLUX(FLUX,SOL,JSTEP,JINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 Q, V, T, X0, Y0, Z0
      REAL*8 X, Y, Z, R, R0, DIST_SQ
      REAL*8 EFF, VOLTAGE, CURRENT, H
C
C  Welding parameters (arc efficiency x V x I = net power, W -> mW)
      EFF     = 0.75D0      ! arc efficiency
      VOLTAGE = 25.0D0      ! V
      CURRENT = 200.0D0     ! A
      V       = 5.0D0       ! travel speed (mm/s)
      R0      = 3.0D0       ! heat source radius (mm)
      H       = 2.0D0       ! penetration depth (mm)
C
      Q = EFF*VOLTAGE*CURRENT*1000.0D0    ! net power in mW
C
C  Source center moves along X at speed V
      T  = TIME(2)
      X0 = V*T
      Y0 = 0.0D0
      Z0 = 0.0D0
C
      X = COORDS(1)
      Y = COORDS(2)
      Z = COORDS(3)
C
      DIST_SQ = (X-X0)**2 + (Y-Y0)**2 + (Z-Z0)**2
C
C  Gaussian volumetric distribution (normalized so integral = Q)
      FLUX(1) = (6.0D0*Q/(3.14159265358979D0**1.5D0*R0**3))
     1        * EXP(-3.0D0*DIST_SQ/(R0*R0))
      FLUX(2) = 0.0D0
C
      RETURN
      END
```

## Template 2: Goldak Double-Ellipsoid (most accurate for arc welding)

```fortran
      SUBROUTINE DFLUX(FLUX,SOL,JSTEP,JINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 EFF, VOLTAGE, CURRENT, V, T
      REAL*8 A_F, A_R, B, C_D, Q
      REAL*8 X, Y, Z, X0, Y0, Z0, XI
      REAL*8 F_F, F_R, F1, F2, Q1, Q2
C
      EFF     = 0.8D0
      VOLTAGE = 24.0D0
      CURRENT = 180.0D0
      V       = 4.0D0        ! travel speed (mm/s)
      A_F     = 3.0D0        ! front semi-axis (mm)
      A_R     = 6.0D0        ! rear semi-axis (mm)
      B       = 3.0D0        ! half-width (mm)
      C_D     = 2.5D0        ! depth (mm)
C
      Q  = EFF*VOLTAGE*CURRENT*1000.0D0    ! net power (mW)
      F_F = 2.0D0*A_F/(A_F+A_R)            ! front fraction
      F_R = 2.0D0*A_R/(A_F+A_R)            ! rear fraction
      PI = 3.14159265358979D0
C
      T  = TIME(2)
      X0 = V*T
      Y0 = 0.0D0
      Z0 = 0.0D0
C
      X  = COORDS(1)
      Y  = COORDS(2)
      Z  = COORDS(3)
      XI = X - X0           ! coordinate relative to source center
C
C  Front ellipsoid (x ahead of the source)
      IF (XI .GE. 0.0D0) THEN
        F1 = 6.0D0*SQRT(3.0D0)*F_F*Q/(A_F*B*C_D*PI*SQRT(PI))
        Q1 = EXP(-3.0D0*(XI/A_F)**2) * EXP(-3.0D0*(Y/B)**2)
     1     * EXP(-3.0D0*(Z/C_D)**2)
        FLUX(1) = F1*Q1
      ELSE
C  Rear ellipsoid (x behind the source)
        F2 = 6.0D0*SQRT(3.0D0)*F_R*Q/(A_R*B*C_D*PI*SQRT(PI))
        Q2 = EXP(-3.0D0*(XI/A_R)**2) * EXP(-3.0D0*(Y/B)**2)
     1     * EXP(-3.0D0*(Z/C_D)**2)
        FLUX(1) = F2*Q2
      END IF
      FLUX(2) = 0.0D0
C
      RETURN
      END
```

## Companion: HETVAL or BodyHeatFlux alternative

For heat input that depends on material state (curing, resistive heating) prefer
`HETVAL` (see `hetval_heat.md`). For constant internal generation, `BodyHeatFlux`
in CAE is simpler than DFLUX.

## Abaqus Input File Example

```abaqus
*Step, name=Heat-In, inc=500
*Heat Transfer, steady state=NO, end=SS
3600.0, 0.5, 0.005, 20.0
**
*DFLUX, op=NEW
Weld-Surf, BFNU, 1.0
**    (surface set, BFNU=body flux via user subroutine, magnitude is a multiplier)
*Output, field
*Node Output
NT,
*Element Output
HFL,
*End Step
```

> JLTYP for `BFNU` is 0 (volumetric). For surface flux use `FUNU` → JLTYP=1.
> The magnitude in `*DFLUX` multiplies the subroutine's FLUX(1).

## Practical Guidance

1. **Mesh the weld path finely**: heat source radius needs ≥ 2–3 elements across
2. **Time increments**: keep the source travel per increment ≤ element size
   (`dt ≤ element_size / V`) to avoid flux skipping
3. **Boundary conditions**: convection (FILM) on exposed faces + radiation for high T
4. **Units**: verify power — W → mW (`×1000`), distances mm, time s
5. **Verify**: peak temperature at the weld centerline; compare to published weld
   thermal cycles if available; check total heat input ≈ ∫∫FLUX dV dt
6. For a pure **thermal-only** run first, then map temperatures to stress analysis
   (sequential coupling, see `thermal/reference/transient.md`)

## Related

- `film_convection.md` — boundary convection
- `hetval_heat.md` — state-dependent volumetric heat generation
- `thermal/reference/transient.md` — sequential thermal-mechanical workflow
