# SDVINI — Initial State Variables Subroutine

## Skill Description

SDVINI defines initial values for solution-dependent state variables (SDVs) at each material point. This is essential when starting an analysis with non-zero history — for example, pre-existing plastic strain, hardening variables, or phase fractions.

## Applicable Scenarios

- Continuing an analysis with inherited state from a previous simulation
- Initializing heterogeneous material properties (e.g., functionally graded materials)
- Setting initial hardening/softening variables
- Prescribing initial porosity, damage, or phase fractions
- Combining with UMAT that reads history-dependent state

## Interface Definition

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| STATEV(NSTATV) | Output | State variable array to initialize |
| COORDS(NCRDS) | Input | Coordinates of the material point |
| NSTATV | Input | Number of state variables |
| NCRDS | Input | Number of coordinates |
| NOEL | Input | Element number |
| NPT | Input | Integration point number |
| LAYER | Input | Layer number (shells) |
| KSPT | Input | Section point number |

## Fortran Code Template

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
C     Initialize state variables based on spatial position
C     Example: Linear gradient of hardening variable along X-axis
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION STATEV(NSTATV), COORDS(NCRDS)
C
      REAL*8 X, Y, Z, X_MIN, X_MAX
      PARAMETER (X_MIN=0.0D0, X_MAX=100.0D0)
C
C-----------------------------------------------------------------------
C     Get coordinates
C-----------------------------------------------------------------------
      X = COORDS(1)
      IF (NCRDS .GE. 2) Y = COORDS(2)
      IF (NCRDS .GE. 3) Z = COORDS(3)
C
C-----------------------------------------------------------------------
C     Initialize state variables
C-----------------------------------------------------------------------
C     SDV1: Initial equivalent plastic strain (linear gradient)
      IF (X .LE. X_MIN) THEN
        STATEV(1) = 0.0D0
      ELSE IF (X .GE. X_MAX) THEN
        STATEV(1) = 0.1D0
      ELSE
        STATEV(1) = 0.1D0 * (X - X_MIN) / (X_MAX - X_MIN)
      END IF
C
C     SDV2: Initial hardening variable (proportional to SDV1)
      STATEV(2) = 210000.0D0 * STATEV(1)  ! H * peeq
C
C     SDV3-SDV6: Initialize backstress to zero
      STATEV(3) = 0.0D0
      STATEV(4) = 0.0D0
      STATEV(5) = 0.0D0
      STATEV(6) = 0.0D0
C
      RETURN
      END
```

## Usage with UMAT

The UMAT reads STATEV on first call at each integration point. SDVINI runs once before the first increment:

```python
# In Abaqus input file:
# *Initial Conditions, type=SOLUTION
# (SDVINI will be called automatically)
```

```fortran
C     In UMAT, check if this is the first call:
      IF (KINC .EQ. 0 .AND. STEPTIME .EQ. 0.0D0) THEN
C       STATEV has been initialized by SDVINI
C       Use STATEV values for initial hardening, etc.
      END IF
```

## Common Patterns

### Pattern 1: Read from External File

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV), COORDS(NCRDS)
C
      LOGICAL FIRST_CALL
      DATA FIRST_CALL /.TRUE./
      SAVE FIRST_CALL
C
      INTEGER UNIT_NUM
      PARAMETER (UNIT_NUM=100)
C
C     Read SDV file only once
      IF (FIRST_CALL) THEN
        FIRST_CALL = .FALSE.
        OPEN(UNIT=UNIT_NUM, FILE='sdv_initial.dat',
     1       STATUS='OLD', FORM='FORMATTED')
      END IF
C
C     Read element-specific values
C     (file format: ELEM_NUM, SDV1, SDV2, ...)
C
      RETURN
      END
```

### Pattern 2: Temperature-Dependent Initial State

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV), COORDS(NCRDS)
C
      REAL*8 TEMP
C
C     Get temperature at this point (from predefined field)
      CALL GETVRM('TEMP', ARRAY, JRCD, JRMATYP, CDUMMY, JDUMMY)
      TEMP = ARRAY(1)
C
C     Phase fraction depends on temperature
      IF (TEMP .LT. 800.0D0) THEN
        STATEV(1) = 0.0D0   ! No transformation
      ELSE IF (TEMP .GT. 900.0D0) THEN
        STATEV(1) = 1.0D0   ! Fully transformed
      ELSE
        STATEV(1) = (TEMP - 800.0D0) / 100.0D0
      END IF
C
      RETURN
      END
```

### Pattern 3: Random Field (Stochastic)

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION STATEV(NSTATV), COORDS(NCRDS)
C
      REAL*8 RANDOM_VAL
C
C     Simple pseudo-random based on element and integration point
C     (NOT cryptographically random — for spatially varying materials only)
      RANDOM_VAL = SIN(DBLE(NOEL)*3.14159D0 + DBLE(NPT)*1.5708D0)
      RANDOM_VAL = 0.5D0 * (RANDOM_VAL + 1.0D0)  ! Scale to [0,1]
C
C     Initialize porosity with random perturbation
      STATEV(1) = 0.001D0 + 0.002D0 * RANDOM_VAL
C
      RETURN
      END
```

## Abaqus Input File Syntax

```
*Initial Conditions, type=SOLUTION
<element_set>, <variable1>, <variable2>, ...
```

Or for automatic SDVINI call:

```
*Initial Conditions, type=SOLUTION, USER
```

## Verification Checklist

- [ ] NSTATV matches the number used by UMAT/VUMAT
- [ ] Initial values are physically reasonable (non-negative for plastic strain)
- [ ] SDVINI runs once before step 1, increment 1
- [ ] GETVRM can be used to access initial field variables

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| SDVINI not called | Missing *Initial Conditions, type=SOLUTION | Add initial conditions keyword |
| STATEV overwritten by UMAT | UMAT reinitializes on first call | Guard with KINC==0 check |
| Dimension mismatch | NSTATV differs between SDVINI and UMAT | Use same NSTATV (via *Depvar) |
