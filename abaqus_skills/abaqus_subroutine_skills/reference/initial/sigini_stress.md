# Abaqus SIGINI Initial Stress Subroutine Skill

## Skill Description

This skill guides AI to generate initial stress subroutines SIGINI for Abaqus, used to define initial stress states such as geostress equilibrium, residual stress, etc.

## Applicable Scenarios

- Geostress equilibrium (geotechnical engineering)
- Residual stress initialization (welding, casting)
- Prestressed structures
- Gravity equilibrium initial step

## Key Features

| Feature | Description |
|---------|-------------|
| Call Time | Each integration point at analysis start |
| Output | Initial stress tensor (6 components) |
| Dependencies | Coordinates, element number, etc. |

## SIGINI Interface Definition

```fortran
SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| SIGMA(NTENS) | Output | Initial stress components |
| COORDS(NCRDS) | Input | Integration point coordinates |
| NTENS | Input | Number of stress components |
| NOEL | Input | Element number |
| LREBAR | Input | Rebar flag |

## Initial Stress Types

### 1. Hydrostatic Pressure Distribution (Geostress)

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  Geostress initialization - hydrostatic pressure increasing linearly with depth
C  Suitable for geotechnical analysis
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, DEPTH
      REAL*8 GAMMA, K0, SV, SH
C
C-----------------------------------------------------------------------
C  Geostress parameters
C-----------------------------------------------------------------------
      GAMMA = 20.0D3       ! Soil unit weight (N/m³)
      K0    = 0.5D0        ! Coefficient of lateral earth pressure
      GROUND_LEVEL = 0.0D0 ! Ground surface elevation
C
C-----------------------------------------------------------------------
C  Calculate depth
C-----------------------------------------------------------------------
      Z = COORDS(3)
      DEPTH = GROUND_LEVEL - Z
      IF (DEPTH .LT. 0.0D0) DEPTH = 0.0D0
C
C-----------------------------------------------------------------------
C  Calculate vertical and horizontal stresses
C-----------------------------------------------------------------------
      SV = GAMMA * DEPTH          ! Vertical stress (negative for compression)
      SH = K0 * SV                ! Horizontal stress
C
C-----------------------------------------------------------------------
C  Set initial stress (negative for compressive stress)
C-----------------------------------------------------------------------
      SIGMA(1) = SH               ! S11
      SIGMA(2) = SH               ! S22
      SIGMA(3) = SV               ! S33
      SIGMA(4) = 0.0D0            ! S12
      IF (NTENS .GT. 4) THEN
        SIGMA(5) = 0.0D0          ! S13
        SIGMA(6) = 0.0D0          ! S23
      END IF
C
      RETURN
      END
```

### 2. Prestressed Tendon Initial Stress

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  Prestressed tendon initial stress
C  For simulating prestressed concrete structures
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, TENDON_FORCE, AREA
      REAL*8 SIGMA_PRESTRESS
      INTEGER TENDON_ID
C
C-----------------------------------------------------------------------
C  Check if it is rebar/prestressed tendon
C-----------------------------------------------------------------------
      IF (LREBAR .EQ. 1) THEN
C       Prestress parameters
        TENDON_FORCE = 1000.0D3    ! Prestress force (N)
        AREA = 500.0D-6            ! Tendon cross-section area (m²)
        SIGMA_PRESTRESS = TENDON_FORCE / AREA
C
C       Determine by tendon name
        IF (REBARN .EQ. 'TENDON_1') THEN
          SIGMA(1) = SIGMA_PRESTRESS
        ELSE IF (REBARN .EQ. 'TENDON_2') THEN
          SIGMA(1) = SIGMA_PRESTRESS * 0.9D0
        ELSE
          SIGMA(1) = 0.0D0
        END IF
      ELSE
C       Concrete part has no initial stress
        DO I = 1, NTENS
          SIGMA(I) = 0.0D0
        END DO
      END IF
C
      RETURN
      END
```

### 3. Welding Residual Stress

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  Welding residual stress distribution
C  Based on double elliptical distribution model
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, WELD_CENTER, WELD_WIDTH
      REAL*8 DIST, SIGMA_MAX, SIGMA_RESIDUAL
      REAL*8 WIDTH_1, WIDTH_2
C
C-----------------------------------------------------------------------
C  Welding parameters
C-----------------------------------------------------------------------
      WELD_CENTER = 0.0D0          ! Weld center X coordinate
      WELD_WIDTH  = 0.02D0         ! Weld width (m)
      SIGMA_MAX   = 200.0D6        ! Maximum residual stress (Pa)
      WIDTH_1     = 0.01D0         ! Heat affected zone width 1
      WIDTH_2     = 0.05D0         ! Heat affected zone width 2
C
C-----------------------------------------------------------------------
C  Calculate distance to weld center
C-----------------------------------------------------------------------
      X = COORDS(1)
      DIST = ABS(X - WELD_CENTER)
C
C-----------------------------------------------------------------------
C  Double elliptical residual stress distribution
C-----------------------------------------------------------------------
      IF (DIST .LE. WIDTH_1) THEN
C       Weld zone (tensile stress)
        SIGMA_RESIDUAL = SIGMA_MAX * SQRT(1.0D0 - (DIST/WIDTH_1)**2)
      ELSE IF (DIST .LE. WIDTH_2) THEN
C       Heat affected zone (compressive stress)
        SIGMA_RESIDUAL = -SIGMA_MAX * 0.3D0 
     1                 * SQRT(1.0D0 - ((DIST-WIDTH_1)/(WIDTH_2-WIDTH_1))**2)
      ELSE
C       Base material zone (stress relieved)
        SIGMA_RESIDUAL = 0.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Set stress (longitudinal residual stress is primary)
C-----------------------------------------------------------------------
      SIGMA(1) = SIGMA_RESIDUAL    ! S11 - longitudinal
      SIGMA(2) = 0.0D0             ! S22
      SIGMA(3) = 0.0D0             ! S33
      SIGMA(4) = 0.0D0             ! S12
      IF (NTENS .GT. 4) THEN
        SIGMA(5) = 0.0D0
        SIGMA(6) = 0.0D0
      END IF
C
      RETURN
      END
```

## Input File Example

```abaqus
** Initial stress
*Initial Conditions, type=STRESS, user
Whole_Model,
```

## Notes

1. **Equilibrium Check**: Initial stress should be as close to equilibrium state as possible
2. **Stress Coordination**: Initial stress in different regions should be continuous
3. **First Step Analysis**: Usually set as static general step for equilibrium
4. **Output Verification**: Check if initial stress is correctly applied

## SDVINI (Initial State Variables)

Used to initialize UMAT state variables:

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
C
C     Initialize equivalent plastic strain
      STATEV(1) = 0.0D0
C
C     Initialize other state variables
      DO I = 2, NSTATV
        STATEV(I) = 0.0D0
      END DO
C
      RETURN
      END
```

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 19.2
