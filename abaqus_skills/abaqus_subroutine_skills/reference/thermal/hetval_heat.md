# Abaqus HETVAL Heat Generation Subroutine Skill

## Skill Description

This skill guides AI to generate heat generation subroutines HETVAL for Abaqus, used to define heat generation within materials such as cure exothermic heat, Joule heat, chemical reaction heat, etc.

## Applicable Scenarios

- Composite material cure exothermic heat
- Battery charge/discharge heat generation
- Viscoplastic dissipation heat
- Chemical reaction heat

## Key Features

| Feature | Description |
|---------|-------------|
| Call Time | Each integration point in heat conduction analysis |
| Output | Volumetric heat generation rate |
| Dependencies | Temperature, state variables, field variables |

## HETVAL Interface Definition

```fortran
SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| FLUX(1) | Output | Heat generation rate (per unit volume) |
| FLUX(2) | Output | Derivative of heat generation rate with respect to temperature |
| TEMP | Input | Current temperature |
| STATEV(*) | Input/Output | State variables |
| TIME(1) | Input | Current step time |

## Heat Generation Types

### 1. Cure Exothermic Heat (Composite Materials)

```fortran
      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  Composite material cure exothermic heat
C  Based on cure degree and Arrhenius kinetics
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION FLUX(2), TIME(2), STATEV(*), PREDEF(*), DPRED(*),
     1 COORMS(3)
C
      REAL*8 T, ALPHA, DALPHA_DT, RATE
      REAL*8 A1, A2, DE1, DE2, M, N, R
      REAL*8 K1, K2, DH_DT
      REAL*8 TOTAL_HEAT
C
C-----------------------------------------------------------------------
C  Cure parameters
C-----------------------------------------------------------------------
      A1  = 2.08D7           ! Pre-exponential factor 1 (1/s)
      A2  = -1.85D7          ! Pre-exponential factor 2 (1/s)
      DE1 = 8.07D4           ! Activation energy 1 (J/mol)
      DE2 = 7.88D4           ! Activation energy 2 (J/mol)
      M   = 0.51D0           ! Reaction order m
      N   = 1.47D0           ! Reaction order n
      R   = 8.314D0          ! Gas constant
      TOTAL_HEAT = 4.0D5     ! Total cure heat (J/kg)
      RHO = 1500.0D0         ! Density (kg/m³)
C
C-----------------------------------------------------------------------
C  Get temperature and cure degree
C-----------------------------------------------------------------------
      T = TEMP + 273.15D0    ! Convert to absolute temperature
      ALPHA = STATEV(1)      ! Get cure degree from state variable
C
C-----------------------------------------------------------------------
C  Calculate reaction rate constant
C-----------------------------------------------------------------------
      K1 = A1 * EXP(-DE1/(R*T))
      K2 = A2 * EXP(-DE2/(R*T))
C
C-----------------------------------------------------------------------
C  Calculate cure rate
C-----------------------------------------------------------------------
      IF (ALPHA .LT. 0.3D0) THEN
        RATE = (K1 + K2*ALPHA**M) * (1.0D0-ALPHA)**N
      ELSE
        RATE = K1 * (1.0D0-ALPHA)**N
      END IF
C
C-----------------------------------------------------------------------
C  Calculate heat generation rate
C-----------------------------------------------------------------------
      FLUX(1) = RHO * TOTAL_HEAT * RATE
C
C-----------------------------------------------------------------------
C  Calculate temperature derivative (approximate)
C-----------------------------------------------------------------------
      DH_DT = FLUX(1) * DE1 / (R*T*T)
      FLUX(2) = DH_DT
C
C-----------------------------------------------------------------------
C  Update state variables (cure degree)
C-----------------------------------------------------------------------
      STATEV(1) = STATEV(1) + RATE * DTIME
      IF (STATEV(1) .GT. 0.999D0) STATEV(1) = 0.999D0
C
      RETURN
      END
```

### 2. Viscoplastic Dissipation Heat

```fortran
      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  Viscoplastic dissipation heat generation
C  Based on plastic work conversion
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION FLUX(2), TIME(2), STATEV(*), PREDEF(*), DPRED(*),
     1 COORMS(3)
C
      REAL*8 ETA, SIGMA_EQ, EPS_PLAS, RATE_PLAS
      REAL*8 HEAT_GENERATION
C
C-----------------------------------------------------------------------
C  Parameters
C-----------------------------------------------------------------------
      ETA = 0.9D0            ! Fraction of plastic work converted to heat (Taylor-Quinney coefficient)
C
C-----------------------------------------------------------------------
C  Get equivalent plastic strain and strain rate from state variables
C  Assume STATEV(1)=equivalent plastic strain, STATEV(2)=plastic strain rate
C-----------------------------------------------------------------------
      EPS_PLAS = STATEV(1)
      RATE_PLAS = STATEV(2)
C
C-----------------------------------------------------------------------
C  Calculate equivalent stress (from state variables or constitutive relationship)
C  Here assume simple power law hardening
C-----------------------------------------------------------------------
      SIGMA_Y = 200.0D6      ! Yield stress (Pa)
      K = 500.0D6            ! Hardening coefficient
      N_HARD = 0.3D0         ! Hardening exponent
C
      SIGMA_EQ = SIGMA_Y + K * (EPS_PLAS**N_HARD)
C
C-----------------------------------------------------------------------
C  Calculate heat generation rate (plastic power)
C  Q = η * σ_eq * ε̇_plas
C-----------------------------------------------------------------------
      HEAT_GENERATION = ETA * SIGMA_EQ * RATE_PLAS
C
      FLUX(1) = HEAT_GENERATION
      FLUX(2) = 0.0D0        ! Simplified to zero
C
      RETURN
      END
```

## Input File Example

```abaqus
*Material, name=Composite
*Conductivity
0.5, 
*Specific heat
1200.0, 
*Density
1500.0, 
*Heat generation
*Depvar
2
```

## FILM (Custom Convection Coefficient)

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
C  Custom convection coefficient - temperature dependent or position dependent
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION H(2), TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
      REAL*8 T, H_CONST, H_COEFF
      REAL*8 X, Y, Z, DIST
C
C-----------------------------------------------------------------------
C  Base convection coefficient
C-----------------------------------------------------------------------
      H_CONST = 10.0D0       ! W/(m²·K)
C
C-----------------------------------------------------------------------
C  Temperature dependent convection coefficient (natural convection)
C-----------------------------------------------------------------------
      T = TEMP
      H_COEFF = H_CONST * (1.0D0 + 0.01D0*(T-20.0D0))
C
C-----------------------------------------------------------------------
C  Position dependent (enhanced heat transfer near cooling channels)
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      DIST = SQRT(X*X + Y*Y)
C
      IF (DIST .LT. 0.1D0) THEN
        H_COEFF = H_COEFF * 2.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Output
C-----------------------------------------------------------------------
      H(1) = H_COEFF         ! Convection coefficient
      H(2) = 0.01D0*H_CONST  ! Derivative with respect to temperature (approximate)
      SINK = 20.0D0          ! Ambient temperature
C
      RETURN
      END
```

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 29.3
