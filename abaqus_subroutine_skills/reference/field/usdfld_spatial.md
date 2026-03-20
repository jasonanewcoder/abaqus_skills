# Abaqus USDFLD Custom Field Variable Subroutine Skill

## Skill Description

This skill guides AI to generate user-defined field variable subroutines USDFLD for Abaqus, used to define material property fields that vary with time or space, such as temperature fields, damage fields, initial defect distributions, etc.

## Applicable Scenarios

- Temperature-dependent material properties
- Spatially inhomogeneous materials (e.g., FGM functionally graded materials)
- Initial defect/porosity distribution
- Cure degree distribution (composite curing)
- Humidity distribution

## Key Features

| Feature | Description |
|---------|-------------|
| Call Time | Each material point at each increment start |
| Output | Field variable array for subsequent material calculation |
| Dependencies | Can depend on time, coordinates, other field variables |
| Transfer | Field variables can be passed to UMAT and other subroutines |

## USDFLD Interface Definition

```fortran
SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| FIELD(NFIELD) | Output | Field variable values |
| STATEV(NSTATV) | Input/Output | State variables |
| TIME(1) | Input | Current step time |
| TIME(2) | Input | Total time |
| COORD(3) | Input | Material point coordinates |
| NFIELD | Input | Number of field variables |
| NSTATV | Input | Number of state variables |

## Field Variable Types

### 1. Spatial Linear Distribution (Gradient Field)

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  Spatial linear gradient field variable
C  For functionally graded materials (FGM)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      CHARACTER*3  FLGRAY(15)
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 X, Y, Z, F0, F1, X_MIN, X_MAX, GRADIENT
C
C-----------------------------------------------------------------------
C  Define linear gradient parameters
C-----------------------------------------------------------------------
      F0    = 0.0D0        ! Field variable value at X_MIN
      F1    = 1.0D0        ! Field variable value at X_MAX
      X_MIN = 0.0D0        ! Gradient start X coordinate
      X_MAX = 10.0D0       ! Gradient end X coordinate
C
C-----------------------------------------------------------------------
C  Get current point coordinates
C-----------------------------------------------------------------------
      X = COORD(1)
      Y = COORD(2)
      Z = COORD(3)
C
C-----------------------------------------------------------------------
C  Calculate linear interpolation
C-----------------------------------------------------------------------
      IF (X .LE. X_MIN) THEN
        FIELD(1) = F0
      ELSE IF (X .GE. X_MAX) THEN
        FIELD(1) = F1
      ELSE
        GRADIENT = (X - X_MIN) / (X_MAX - X_MIN)
        FIELD(1) = F0 + (F1 - F0) * GRADIENT
      END IF
C
C-----------------------------------------------------------------------
C  Store state variables (optional)
C-----------------------------------------------------------------------
      STATEV(1) = FIELD(1)
C
      RETURN
      END
```

### 2. Gaussian Distribution Field (Local Hot Spots)

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  Gaussian distributed field variable - simulate local temperature hot spots or damage concentration zones
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 X, Y, Z, X_CENTER, Y_CENTER, Z_CENTER
      REAL*8 AMP, SIGMA_X, SIGMA_Y, SIGMA_Z
      REAL*8 DIST_SQ, FIELD_VAL
      INTEGER N_HOTSPOTS, I
      PARAMETER(N_HOTSPOTS=3)
      REAL*8 XC(N_HOTSPOTS), YC(N_HOTSPOTS), ZC(N_HOTSPOTS)
C
C-----------------------------------------------------------------------
C  Define hot spot positions (can be read from file)
C-----------------------------------------------------------------------
      DATA XC /1.0D0, 3.0D0, 5.0D0/
      DATA YC /1.0D0, 2.0D0, 1.5D0/
      DATA ZC /0.0D0, 0.0D0, 0.0D0/
      
      AMP = 100.0D0         ! Peak field variable value
      SIGMA_X = 0.5D0       ! Distribution width in X direction
      SIGMA_Y = 0.5D0       ! Distribution width in Y direction
      SIGMA_Z = 0.5D0       ! Distribution width in Z direction
C
C-----------------------------------------------------------------------
C  Get current point coordinates
C-----------------------------------------------------------------------
      X = COORD(1)
      Y = COORD(2)
      Z = COORD(3)
C
C-----------------------------------------------------------------------
C  Calculate superimposed Gaussian field from multiple hot spots
C-----------------------------------------------------------------------
      FIELD_VAL = 0.0D0
      DO I = 1, N_HOTSPOTS
        DIST_SQ = ((X-XC(I))/SIGMA_X)**2 
     1          + ((Y-YC(I))/SIGMA_Y)**2 
     2          + ((Z-ZC(I))/SIGMA_Z)**2
        FIELD_VAL = FIELD_VAL + AMP * EXP(-0.5D0*DIST_SQ)
      END DO
C
      FIELD(1) = FIELD_VAL
C
C-----------------------------------------------------------------------
C  Store state variables
C-----------------------------------------------------------------------
      STATEV(1) = FIELD(1)
C
      RETURN
      END
```

### 3. Time-Dependent Cure Degree Field

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  Composite material cure degree field
C  Based on Arrhenius equation cure kinetics
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 T_TEMP, T_CURR, T_PREV
      REAL*8 A1, A2, DE1, DE2, M, N, R
      REAL*8 ALPHA, DALPHA, RATE
      REAL*8 K1, K2
C
C-----------------------------------------------------------------------
C  Cure kinetics parameters
C-----------------------------------------------------------------------
      A1  = 2.08D7           ! Pre-exponential factor 1 (1/s)
      A2  = -1.85D7          ! Pre-exponential factor 2 (1/s)
      DE1 = 8.07D4           ! Activation energy 1 (J/mol)
      DE2 = 7.88D4           ! Activation energy 2 (J/mol)
      M   = 0.51D0           ! Reaction order m
      N   = 1.47D0           ! Reaction order n
      R   = 8.314D0          ! Gas constant (J/(mol*K))
C
C-----------------------------------------------------------------------
C  Read cure degree from previous increment in state variables
C-----------------------------------------------------------------------
      IF (TIME(1) .EQ. 0.0D0) THEN
        ALPHA = 0.0D0        ! Initial cure degree
      ELSE
        ALPHA = STATEV(1)
      END IF
C
C-----------------------------------------------------------------------
C  Get current temperature (should obtain from thermal analysis in practical application)
C-----------------------------------------------------------------------
      T_CURR = 180.0D0 + 273.15D0   ! Current temperature (K), sample value
C
C-----------------------------------------------------------------------
C  Calculate reaction rate constant (Arrhenius equation)
C-----------------------------------------------------------------------
      K1 = A1 * EXP(-DE1/(R*T_CURR))
      K2 = A2 * EXP(-DE2/(R*T_CURR))
C
C-----------------------------------------------------------------------
C  Calculate cure rate (autocatalytic model)
C-----------------------------------------------------------------------
      IF (ALPHA .LT. 0.3D0) THEN
        RATE = (K1 + K2*ALPHA**M) * (1.0D0-ALPHA)**N
      ELSE
        RATE = K1 * (1.0D0-ALPHA)**N
      END IF
C
C-----------------------------------------------------------------------
C  Update cure degree
C-----------------------------------------------------------------------
      DALPHA = RATE * DTIME
      ALPHA = ALPHA + DALPHA
C
C  Limit range
      IF (ALPHA .GT. 0.999D0) ALPHA = 0.999D0
C
C-----------------------------------------------------------------------
C  Output field variables
C-----------------------------------------------------------------------
      FIELD(1) = ALPHA       ! Cure degree
      FIELD(2) = T_CURR      ! Temperature
C
C-----------------------------------------------------------------------
C  Update state variables
C-----------------------------------------------------------------------
      STATEV(1) = ALPHA
      STATEV(2) = RATE
C
      RETURN
      END
```

## Association with Material Properties

Associate field variables in input file:

```abaqus
*Material, name=FGM_Material
*Elastic
** E varies with field variable
100000.0, 0.3, , , FIELD(1)
200000.0, 0.3, , , 1.0
**
*User Defined Field
*Depvar
2
```

## Notes

1. **Call Order**: USDFLD is called at the start of each increment, before UMAT
2. **Field Variable Count**: NFIELD must be defined in input file
3. **Transfer Mechanism**: Field variables passed to UMAT via STATEV or directly
4. **Update Frequency**: Time step can be controlled via PNEWDT

## Extension Directions

- Coupling with external data files (measured temperature fields)
- Random field generation (Monte Carlo analysis)
- Multi-physics coupling (thermo-chemo-mechanical)
- Damage field evolution

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26.7.2
