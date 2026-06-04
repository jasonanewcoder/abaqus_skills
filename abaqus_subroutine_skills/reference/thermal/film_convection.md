# FILM — Convection Boundary Condition Subroutine

## Skill Description

FILM defines a non-uniform film (convection) boundary condition where the convection coefficient h and/or sink temperature can vary with position, time, temperature, or other field variables.

## Applicable Scenarios

- Natural convection with temperature-dependent h
- Forced convection varying with flow velocity
- Spray cooling with spatial distribution
- Selective cooling/heating patterns
- Pool boiling heat transfer

## Interface Definition

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| H | Output | Film coefficient at this point |
| SINK | Output | Sink (ambient) temperature |
| TEMP | Input | Current surface temperature |
| KSTEP | Input | Step number |
| KINC | Input | Increment number |
| TIME(2) | Input | TIME(1)=step time, TIME(2)=total time |
| NOEL | Input | Element number |
| NPT | Input | Integration point number |
| COORDS(3) | Input | Coordinates |
| JLTYP | Input | Face identifier |
| FIELD | Input | Field variable array |
| NFIELD | Input | Number of field variables |
| SNAME | Input | Surface name |
| NODE | Input | Node number |
| AREA | Input | Area associated with this point |

## Fortran Code Template

### Template 1: Temperature-Dependent Natural Convection

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
C     Natural convection: h varies with (T_surface - T_ambient)^(1/3)
C     h = C * |T - T_inf|^(1/3)  (laminar natural convection)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
      REAL*8 T_INF, C_NATURAL, DT, SIGN_DT
C
C-----------------------------------------------------------------------
C     Parameters
C-----------------------------------------------------------------------
      T_INF = 20.0D0         ! Ambient temperature (°C)
      C_NATURAL = 1.42D0     ! Natural convection constant (vertical plate)
C                            ! Units: W/(m²·K^1.333) → mW/(mm²·K^1.333) × 1e-6
C
C-----------------------------------------------------------------------
C     Calculate film coefficient
C-----------------------------------------------------------------------
      DT = TEMP - T_INF
      SIGN_DT = SIGN(1.0D0, DT)
C
      H = C_NATURAL * (ABS(DT) ** 0.333D0)
C
C     Convert to Abaqus units if needed:
C     W/(m²·K) → mW/(mm²·K): multiply by 1e-6
      H = H * 1.0D-6
C
      SINK = T_INF
C
      RETURN
      END
```

### Template 2: Forced Convection with Position Dependence

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
C     Forced convection: h varies with position and time
C     Simulates cooling jet moving along surface
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
      REAL*8 H_MAX, JET_WIDTH, JET_CENTER, DIST
      REAL*8 VELOCITY, T_COOLANT
      PARAMETER (H_MAX=500.0D-6, JET_WIDTH=10.0D0, VELOCITY=20.0D0)
      PARAMETER (T_COOLANT=15.0D0)
C
C-----------------------------------------------------------------------
C     Moving cooling jet along X-axis
C-----------------------------------------------------------------------
      JET_CENTER = VELOCITY * TIME(2)   ! Time(2) = total time
C
C     Gaussian distribution around jet center
      DIST = COORDS(1) - JET_CENTER
      H = H_MAX * EXP(-0.5D0 * (DIST / JET_WIDTH) ** 2)
C
      SINK = T_COOLANT
C
      RETURN
      END
```

### Template 3: Boiling Heat Transfer (Pool Boiling)

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
C     Pool boiling curve: nucleate boiling + transition + film boiling
C     h = f(wall superheat)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
      REAL*8 TSAT, DT_SUPER, H_NC, H_NB, H_FB
      PARAMETER (TSAT=100.0D0)       ! Saturation temperature (°C)
      PARAMETER (H_NC=1.0D-3)        ! Natural convection h
      PARAMETER (H_FB=0.2D-3)        ! Film boiling h
C
C-----------------------------------------------------------------------
C     Boiling curve
C-----------------------------------------------------------------------
      DT_SUPER = TEMP - TSAT
C
      IF (DT_SUPER .LE. 0.0D0) THEN
C       Single-phase liquid (natural convection)
        H = H_NC
      ELSE IF (DT_SUPER .LT. 5.0D0) THEN
C       Nucleate boiling onset
        H = H_NC + (4.0D-3 - H_NC) * DT_SUPER / 5.0D0
      ELSE IF (DT_SUPER .LT. 30.0D0) THEN
C       Fully developed nucleate boiling
        H = 4.0D-3 * (DT_SUPER / 5.0D0) ** 2.0D0
      ELSE IF (DT_SUPER .LT. 50.0D0) THEN
C       Transition boiling (degrading h)
        H = 4.0D-3 * (30.0D0/5.0D0)**2 * EXP(-0.1D0*(DT_SUPER-30.0D0))
      ELSE
C       Film boiling
        H = H_FB
      END IF
C
      SINK = TSAT  ! Sink = saturation temperature for boiling
C
      RETURN
      END
```

## Abaqus Input File Syntax

```
*Film, USER
<surface_name>, <surface_temperature_dep>
```

Or with fixed sink temperature:

```
*Film, USER, FIXED SINK
<surface_name>
```

## Using with Python Script

```python
# Apply FILM user subroutine to a surface
top_face = instance.faces.findAt(((50.0, 50.0, 10.0),))
film_surface = assembly.Surface(name='Film-Surf', side1Faces=top_face)

model.FilmCondition(
    name='User-Convection',
    createStepName='Thermal-Step',
    surface=film_surface,
    definition=USER,
    sinkTemperature=20.0,  # Default (may be overridden by FILM)
    filmCoeff=1.0           # Default (may be overridden by FILM)
)

# Submit with user subroutine
job = mdb.Job(
    name='Film-Job',
    model='Thermal-Model',
    userSubroutine='film_user.for'
)
```

## Verification Checklist

- [ ] H output is in correct Abaqus units (mW/(mm²·K))
- [ ] SINK temperature is physically reasonable
- [ ] FILM is called at each surface integration point each increment
- [ ] Multiple FILM surfaces work independently

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| h=0 at all points | H not assigned | Check that code path sets H |
| Unrealistic cooling rate | h too large (unit error) | Divide by 1e6 for W/(m²·K)→mW/(mm²·K) |
| Temperature diverges | SINK not set | Ensure SINK is always assigned |
| FILM not called | Wrong *Film keyword | Use *Film, USER not *Film |
