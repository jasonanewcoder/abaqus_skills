# Abaqus DLOAD Moving Load Subroutine Skill

## Skill Description

This skill guides AI to generate distributed load subroutines DLOAD for Abaqus Standard, implementing moving loads (such as wheel loads, cutting forces, laser scanning, etc.).

## Applicable Scenarios

- Moving wheel loads (bridge, pavement analysis)
- Machining simulation
- Laser/electron beam scanning heating
- Moving pressure loads

## Key Features

| Feature | Description |
|---------|-------------|
| Analysis Type | Implicit/Explicit Static or Dynamics |
| Load Type | Distributed pressure, concentrated force, etc. |
| Motion Type | Constant/variable speed/path-following |
| Load Distribution | Uniform/Gaussian/Custom |

## DLOAD Interface Definition

```fortran
SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| F | Output | Load magnitude (positive for pressure) |
| TIME(1) | Input | Current step time |
| TIME(2) | Input | Total time |
| COORDS(3) | Input | Integration point coordinates |
| NOEL | Input | Element number |
| NPT | Input | Integration point number |
| JLTYP | Input | Load type identifier |

## Moving Load Types

### 1. Constant Speed Linear Motion

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  Constant speed linear moving load - DLOAD
C  Load moves at constant speed along X direction
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, V, X0, X, T, LOAD_WIDTH, DIST
      REAL*8 GAUSS_CENTER, GAUSS_WIDTH, LOAD_SHAPE
C
C-----------------------------------------------------------------------
C  Load parameters (should be passed via PROPS or COMMON block)
C-----------------------------------------------------------------------
      F0 = 1000.0D0          ! Load peak (N/m² or N/m)
      V  = 10.0D0            ! Moving speed (m/s)
      X0 = 0.0D0             ! Initial position
      GAUSS_WIDTH = 0.1D0    ! Load distribution width
C
C-----------------------------------------------------------------------
C  Calculate current load center position
C-----------------------------------------------------------------------
      T = TIME(2)            ! Total time
      GAUSS_CENTER = X0 + V * T
C
C-----------------------------------------------------------------------
C  Calculate distance to load center
C-----------------------------------------------------------------------
      X = COORDS(1)          ! Current integration point X coordinate
      DIST = X - GAUSS_CENTER
C
C-----------------------------------------------------------------------
C  Gaussian distributed load
C-----------------------------------------------------------------------
      LOAD_SHAPE = EXP(-DIST*DIST / (2.0D0*GAUSS_WIDTH*GAUSS_WIDTH))
      F = F0 * LOAD_SHAPE
C
      RETURN
      END
```

### 2. Circular Moving Load (Rotating Table)

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  Circular moving load
C  Load moves at constant speed along a circular path of radius R
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, R, OMEGA, T, THETA, X_CENTER, Y_CENTER
      REAL*8 X, Y, X_LOAD, Y_LOAD, DIST, LOAD_RADIUS
C
C-----------------------------------------------------------------------
C  Load parameters
C-----------------------------------------------------------------------
      F0 = 1000.0D0          ! Load peak
      R = 1.0D0              ! Circle radius
      OMEGA = 1.0D0          ! Angular velocity (rad/s)
      X_CENTER = 0.0D0       ! Circle center X
      Y_CENTER = 0.0D0       ! Circle center Y
      LOAD_RADIUS = 0.05D0   ! Load application radius
C
C-----------------------------------------------------------------------
C  Calculate load center position
C-----------------------------------------------------------------------
      T = TIME(2)
      THETA = OMEGA * T
      X_LOAD = X_CENTER + R * COS(THETA)
      Y_LOAD = Y_CENTER + R * SIN(THETA)
C
C-----------------------------------------------------------------------
C  Calculate distance to load center
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      DIST = SQRT((X-X_LOAD)**2 + (Y-Y_LOAD)**2)
C
C-----------------------------------------------------------------------
C  Uniform circular load (within LOAD_RADIUS)
C-----------------------------------------------------------------------
      IF (DIST .LE. LOAD_RADIUS) THEN
        F = F0
      ELSE
        F = 0.0D0
      END IF
C
      RETURN
      END
```

### 3. Path-Following Moving Load

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  Curved path moving load
C  Path defined by node coordinates (read from external file)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, V, T, S, TOTAL_PATH
      REAL*8 X, Y, Z, X_LOAD, Y_LOAD, Z_LOAD
      REAL*8 DIST, LOAD_SIZE
      INTEGER NSEG, ISEG, MAXSEG
      PARAMETER(MAXSEG=100)
C
C  Path nodes (can be read from file)
      REAL*8 PATH_X(MAXSEG), PATH_Y(MAXSEG), PATH_Z(MAXSEG)
      REAL*8 SEG_LEN(MAXSEG)
      COMMON /PATHDATA/ PATH_X, PATH_Y, PATH_Z, SEG_LEN, NSEG
C
C-----------------------------------------------------------------------
C  Parameters
C-----------------------------------------------------------------------
      F0 = 1000.0D0
      V = 5.0D0
      LOAD_SIZE = 0.02D0
      T = TIME(2)
C
C-----------------------------------------------------------------------
C  Calculate current arc length position along path
C-----------------------------------------------------------------------
      S = V * T
      IF (S .GT. TOTAL_PATH) S = TOTAL_PATH
C
C-----------------------------------------------------------------------
C  Determine current segment
C-----------------------------------------------------------------------
      S_TEMP = 0.0D0
      ISEG = 1
      DO I = 1, NSEG-1
        IF (S .LE. S_TEMP + SEG_LEN(I)) THEN
          ISEG = I
          GOTO 100
        END IF
        S_TEMP = S_TEMP + SEG_LEN(I)
      END DO
      ISEG = NSEG - 1
 100   CONTINUE
C
C-----------------------------------------------------------------------
C  Linear interpolation on current segment for load position
C-----------------------------------------------------------------------
      RATIO = (S - S_TEMP) / SEG_LEN(ISEG)
      X_LOAD = PATH_X(ISEG) + RATIO * (PATH_X(ISEG+1) - PATH_X(ISEG))
      Y_LOAD = PATH_Y(ISEG) + RATIO * (PATH_Y(ISEG+1) - PATH_Y(ISEG))
      Z_LOAD = PATH_Z(ISEG) + RATIO * (PATH_Z(ISEG+1) - PATH_Z(ISEG))
C
C-----------------------------------------------------------------------
C  Calculate distance and apply load
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      Z = COORDS(3)
      DIST = SQRT((X-X_LOAD)**2 + (Y-Y_LOAD)**2 + (Z-Z_LOAD)**2)
C
      IF (DIST .LE. LOAD_SIZE) THEN
        F = F0 * (1.0D0 - DIST/LOAD_SIZE)  ! Linear decay
      ELSE
        F = 0.0D0
      END IF
C
      RETURN
      END
```

## Abaqus Input File Example

```abaqus
** Moving load definition
*Dload, amplitude=MoveLoad
Surface-1, P, 1.0
** 
** Need amplitude definition for load time history
*Amplitude, name=MoveLoad, definition=USER
```

## Notes

1. **Mesh Density**: Moving load region needs sufficiently dense mesh
2. **Time Step**: In explicit analysis, load moving speed affects stability
3. **Smooth Transition**: Use Gaussian or cosine distribution to avoid stress concentration
4. **Multiple Loads**: Can distinguish multiple moving loads via JLTYPE

## Differences from VDLOAD

| Feature | DLOAD (Standard) | VDLOAD (Explicit) |
|---------|------------------|-------------------|
| Call Method | Each integration point per increment | Each integration point per time step |
| Block Processing | No | Yes (vectorized) |
| Applicable Analysis | Implicit | Explicit |

## Extension Directions

- Multi-wheel load superposition
- Random irregularity pavement
- Heat source moving (coupled with thermal analysis)
- Variable load amplitude (braking/acceleration process)

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 34.4
