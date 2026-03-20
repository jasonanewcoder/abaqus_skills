# Abaqus FRIC Custom Friction Subroutine Skill

## Skill Description

This skill guides AI to generate custom friction subroutines FRIC for Abaqus, used to define complex contact friction behavior such as velocity-dependent friction, temperature-dependent friction, wear models, etc.

## Applicable Scenarios

- Velocity-dependent friction (Stribeck effect)
- Temperature-dependent friction (thermal tribology)
- Friction coefficient change due to wear
- Anisotropic friction

## Key Features

| Feature | Description |
|---------|-------------|
| Analysis Type | Implicit/Explicit Contact Analysis |
| Friction Model | Coulomb friction, velocity-dependent, temperature-dependent |
| Output | Friction stress, friction coefficient |

## FRIC Interface Definition

```fortran
SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| FRICOUT(2) | Output | Tangential friction stress, friction coefficient |
| FRICIN(*) | Input | Friction-related input data |
| SLIP | Input | Slip amount |
| DRDT | Input | Slip velocity |
| TEMP | Input | Contact point temperature |
| CPRESS | Input | Contact pressure |

## Friction Model Types

### 1. Velocity-Dependent Friction (Stribeck Curve)

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  Velocity dependent friction - Stribeck model
C  Includes static friction, mixed lubrication, hydrodynamic lubrication regions
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 V, MU_S, MU_K, MU_F, V_CRIT, V_TRANSITION
      REAL*8 MU, EXP_TERM
      REAL*8 TAU_MAX
C
C-----------------------------------------------------------------------
C  Friction parameters
C-----------------------------------------------------------------------
      MU_S = 0.5D0           ! Static friction coefficient
      MU_K = 0.3D0           ! Kinetic friction coefficient (medium speed)
      MU_F = 0.05D0          ! Hydrodynamic friction coefficient (high speed)
      V_CRIT = 0.001D0       ! Static-kinetic friction transition velocity (m/s)
      V_TRANSITION = 1.0D0   ! Mixed to hydrodynamic transition velocity (m/s)
C
C-----------------------------------------------------------------------
C  Get slip velocity
C-----------------------------------------------------------------------
      V = ABS(DRDT)
C
C-----------------------------------------------------------------------
C  Stribeck curve model
C-----------------------------------------------------------------------
      IF (V .LT. V_CRIT) THEN
C       Static friction region
        MU = MU_S - (MU_S - MU_K) * (V / V_CRIT)
      ELSE IF (V .LT. V_TRANSITION) THEN
C       Mixed lubrication region (exponential decay)
        EXP_TERM = EXP(-LOG(MU_K/MU_F) * (V - V_CRIT) 
     1           / (V_TRANSITION - V_CRIT))
        MU = MU_K * EXP_TERM
      ELSE
C       Hydrodynamic region
        MU = MU_F
      END IF
C
C-----------------------------------------------------------------------
C  Calculate maximum shear stress
C  τ_max = μ * σ_n
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
C
C-----------------------------------------------------------------------
C  Output
C-----------------------------------------------------------------------
      FRICOUT(1) = TAU_MAX   ! Friction stress
      FRICOUT(2) = MU        ! Friction coefficient
C
      RETURN
      END
```

### 2. Temperature-Dependent Friction (Thermal Tribology)

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  Temperature dependent friction
C  Friction coefficient varies with contact surface temperature
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 T_CONTACT, MU_0, T_REF, T_CRITICAL
      REAL*8 MU, TAU_MAX
C
C-----------------------------------------------------------------------
C  Friction parameters
C-----------------------------------------------------------------------
      MU_0 = 0.4D0           ! Friction coefficient at room temperature
      T_REF = 20.0D0         ! Reference temperature (°C)
      T_CRITICAL = 400.0D0   ! Critical temperature (°C)
C
C-----------------------------------------------------------------------
C  Get contact surface temperature
C-----------------------------------------------------------------------
      T_CONTACT = TEMP
C
C-----------------------------------------------------------------------
C  Temperature dependent friction model
C  Temperature increase leads to friction coefficient decrease (oxide film, material softening)
C-----------------------------------------------------------------------
      IF (T_CONTACT .LE. T_REF) THEN
        MU = MU_0
      ELSE IF (T_CONTACT .LT. T_CRITICAL) THEN
        MU = MU_0 * (1.0D0 - 0.5D0*(T_CONTACT - T_REF)
     1       / (T_CRITICAL - T_REF))
      ELSE
        MU = 0.5D0 * MU_0
      END IF
C
C-----------------------------------------------------------------------
C  Output
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
      FRICOUT(1) = TAU_MAX
      FRICOUT(2) = MU
C
      RETURN
      END
```

### 3. Wear-Induced Friction Degradation

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  Friction model considering wear
C  Cumulative slip distance leads to friction coefficient decrease
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 MU_0, MU_MIN, S_TOTAL, S_CRIT
      REAL*8 DS, MU, TAU_MAX
      INTEGER SV_INDEX
      PARAMETER(SV_INDEX=1)
C
C-----------------------------------------------------------------------
C  Parameters
C-----------------------------------------------------------------------
      MU_0 = 0.5D0           ! Initial friction coefficient
      MU_MIN = 0.2D0         ! Minimum friction coefficient (after complete wear)
      S_CRIT = 1.0D0         ! Critical cumulative slip distance (m)
C
C-----------------------------------------------------------------------
C  Read cumulative slip distance from state variables
C-----------------------------------------------------------------------
      S_TOTAL = FRICIN(NINPT + SV_INDEX)
C
C-----------------------------------------------------------------------
C  Update cumulative slip distance
C-----------------------------------------------------------------------
      DS = ABS(SLIP)
      S_TOTAL = S_TOTAL + DS
C
C-----------------------------------------------------------------------
C  Wear-induced friction coefficient decrease
C-----------------------------------------------------------------------
      IF (S_TOTAL .LE. S_CRIT) THEN
        MU = MU_0 - (MU_0 - MU_MIN) * (S_TOTAL / S_CRIT)
      ELSE
        MU = MU_MIN
      END IF
C
C-----------------------------------------------------------------------
C  Output
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
      FRICOUT(1) = TAU_MAX
      FRICOUT(2) = MU
C
C  Store updated cumulative slip distance (via state variables)
      FRICOUT(3) = S_TOTAL
C
      RETURN
      END
```

## Input File Example

```abaqus
*Surface interaction, name=Frictional_Contact
*Friction, user
** Pass friction parameters (optional)
0.3, 0.1, 1.0
*Surface behavior, pressure-overclosure=hard
```

## Explicit Friction (VRIC)

Explicit analysis uses VRIC subroutine with slightly different interface:

```fortran
      SUBROUTINE VRIC(FRICOUT,FRICIN,TIME,DTIME,TEMP,DTEMP,
     1 FIELD,NFIELD,CPRESS,CNORM,CMTN,NPRED,NPREDF,DBS,DRDT,
     1 SLIP,ILINEAR,NSTRV,CMNAME,IPARAM,IPARAM2)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), FIELD(NFIELD),
     1 CMTN(3), PREDEF(*), DPRED(*), DBS(3)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
C  Similar to FRIC, but processes block data
      REAL*8 MU
      MU = 0.3D0
      FRICOUT(1) = MU * CPRESS
      FRICOUT(2) = MU
C
      RETURN
      END
```

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 38.1
