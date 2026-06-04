# VDLOAD — Explicit Distributed Load Subroutine

## Skill Description

VDLOAD defines a distributed load for Abaqus/Explicit analysis. Unlike DLOAD (implicit), VDLOAD operates on a block of points simultaneously, enabling vectorized execution for better performance.

## Applicable Scenarios

- Moving loads in explicit dynamic analysis (vehicle-bridge interaction)
- Blast/explosion loading (pressure-time variation)
- Impact loading with spatial distribution
- Wave loading on offshore structures
- Non-uniform pressure varying rapidly with time

## Interface Definition

```fortran
      subroutine vdload(
C     Read only (unchanged during call) —
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
C     Write only —
     4 value)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| nBlock | Input | Number of points to process |
| ndim | Input | Number of dimensions |
| stepTime | Input | Current step time |
| totalTime | Input | Current total time |
| amplitude | Input | Amplitude curve value at this time |
| curCoords(nBlock,ndim) | Input | Current coordinates of points |
| velocity(nBlock,ndim) | Input | Current velocities |
| dirCos(nBlock,ndim,ndim) | Input | Direction cosines |
| jltyp | Input | Face/element type identifier |
| sname | Input | Surface name |
| value(nBlock) | Output | Load magnitude at each point |

## Fortran Code Template

### Template 1: Moving Pressure Wave (Blast Load)

```fortran
      subroutine vdload(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 value)
C
C     Moving pressure wave (simplified blast load)
C     Pressure = P_max * (1 - t/t_d) * exp(-a * t/t_d)
C       with spatial decay from blast center
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim), value(nBlock)
      character*80 sname
C
      real*8 P_MAX, T_D, A_DECAY, X_CENTER, Y_CENTER
      real*8 X, Y, DIST, TAU, PRESSURE_TIME, PRESSURE_SPACE
      integer I
C
      parameter (P_MAX=10.0D0)       ! Peak pressure (MPa)
      parameter (T_D=0.001D0)         ! Positive phase duration (s)
      parameter (A_DECAY=2.0D0)       ! Decay constant
      parameter (X_CENTER=50.0D0, Y_CENTER=50.0D0)  ! Blast center (mm)
C
C-----------------------------------------------------------------------
C     Loop over all points in block
C-----------------------------------------------------------------------
      do I = 1, nBlock
        X = curCoords(I, 1)
        Y = curCoords(I, 2)
C
C       Distance from blast center
        DIST = sqrt((X - X_CENTER)**2 + (Y - Y_CENTER)**2)
C
C       Temporal variation (Friedlander waveform)
        TAU = stepTime / T_D
        if (TAU .lt. 1.0D0) then
          PRESSURE_TIME = P_MAX * (1.0D0 - TAU) * exp(-A_DECAY * TAU)
        else
          PRESSURE_TIME = 0.0D0  ! Positive phase ended
        end if
C
C       Spatial decay (1/r for 2D cylindrical, 1/r² for 3D spherical)
        if (DIST .lt. 1.0D0) DIST = 1.0D0  ! Prevent singularity
        PRESSURE_SPACE = 1.0D0 / DIST
C
        value(I) = PRESSURE_TIME * PRESSURE_SPACE * amplitude
      end do
C
      return
      end
```

### Template 2: Moving Wheel Load (Vehicle-Bridge)

```fortran
      subroutine vdload(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 value)
C
C     Moving wheel load on bridge deck
C     Gaussian pressure distribution centered at vehicle position
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim), value(nBlock)
      character*80 sname
C
      real*8 VX, VY, P_AXLE, L_CONTACT, W_CONTACT
      real*8 X_WHEEL, Y_WHEEL, X_LOCAL, Y_LOCAL
      real*8 DIST2, SIGMA_X, SIGMA_Y, PRESSURE
      integer I
C
      parameter (VX=15000.0D0)       ! Vehicle speed (mm/s, = 54 km/h)
      parameter (VY=0.0D0)            ! No lateral movement
      parameter (P_AXLE=100000.0D0)   ! Axle load (N)
      parameter (L_CONTACT=300.0D0)   ! Contact patch length (mm)
      parameter (W_CONTACT=200.0D0)   ! Contact patch width (mm)
C
      SIGMA_X = L_CONTACT / 3.0D0     ! Std dev in X
      SIGMA_Y = W_CONTACT / 3.0D0     ! Std dev in Y
      X_WHEEL = VX * totalTime        ! Current wheel position
      Y_WHEEL = 50.0D0                ! Fixed lateral position
C
      do I = 1, nBlock
        X_LOCAL = curCoords(I, 1) - X_WHEEL
        Y_LOCAL = curCoords(I, 2) - Y_WHEEL
C
C       Gaussian pressure distribution
        DIST2 = (X_LOCAL/SIGMA_X)**2 + (Y_LOCAL/SIGMA_Y)**2
        if (DIST2 .lt. 20.0D0) then  ! Only near the wheel
          PRESSURE = (P_AXLE / (2.0D0*3.14159D0*SIGMA_X*SIGMA_Y))
     1             * exp(-0.5D0 * DIST2)
          value(I) = PRESSURE * amplitude
        else
          value(I) = 0.0D0
        end if
      end do
C
      return
      end
```

### Template 3: Wave Loading (Offshore)

```fortran
      subroutine vdload(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 value)
C
C     Regular wave loading (Airy wave theory)
C     Applied to vertical surface (e.g., offshore structure column)
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim), value(nBlock)
      character*80 sname
C
      real*8 RHO_W, G, H_WAVE, T_WAVE, L_WAVE, K_WAVE, OMEGA
      real*8 D_WATER, Z, P_HYDRO, P_WAVE, P_TOTAL
      integer I
C
      parameter (RHO_W=1.0D-9)        ! Water density (tonne/mm³)
      parameter (G=9800.0D0)           ! Gravity (mm/s²)
      parameter (H_WAVE=5000.0D0)      ! Wave height (mm)
      parameter (T_WAVE=5.0D0)         ! Wave period (s)
      parameter (L_WAVE=39000.0D0)     ! Wave length (mm)
      parameter (D_WATER=50000.0D0)    ! Water depth (mm)
C
      K_WAVE = 2.0D0 * 3.14159D0 / L_WAVE   ! Wave number
      OMEGA = 2.0D0 * 3.14159D0 / T_WAVE     ! Angular frequency
C
      do I = 1, nBlock
        Z = curCoords(I, 3)  ! Vertical coordinate
        if (Z .gt. 0.0D0) then
C         Above water surface
          value(I) = 0.0D0
        else
C         Hydrostatic + dynamic pressure
          P_HYDRO = -RHO_W * G * Z
C
C         Wave dynamic pressure (Airy theory)
          P_WAVE = RHO_W * G * H_WAVE / 2.0D0
     1           * cosh(K_WAVE * (Z + D_WATER)) / cosh(K_WAVE * D_WATER)
     2           * cos(K_WAVE * curCoords(I,1) - OMEGA * stepTime)
C
          P_TOTAL = P_HYDRO + P_WAVE
          value(I) = P_TOTAL * amplitude
        end if
      end do
C
      return
      end
```

## Block Processing — Performance

VDLOAD processes points in blocks. Always use the `I` loop over `nBlock`:

```fortran
! ✓ CORRECT — vectorized block loop
do I = 1, nBlock
  value(I) = curCoords(I,1) * factor
end do

! ✗ WRONG — scalar approach (performance penalty)
value(1) = curCoords(1,1) * factor
```

## Abaqus Input File Syntax

```
*Dsload
<surface_name>, P, <magnitude>
```

Or with amplitude:

```
*Dsload, amplitude=<amp_name>
<surface_name>, P, 1.0
```

## Python Script Integration

```python
from abaqus import *
from abaqusConstants import *

# Apply VDLOAD on a surface
pressure_face = instance.faces.findAt(((50.0, 50.0, 10.0),))
pressure_surface = assembly.Surface(name='Pressure-Surf', side1Faces=pressure_face)

# In explicit step
model.Pressure(
    name='Moving-Load',
    createStepName='Explicit-Step',
    region=pressure_surface,
    distributionType=USER_DEFINED,  # Triggers VDLOAD call
    magnitude=1.0
)

# Submit job with VDLOAD subroutine
job = mdb.Job(
    name='VDLOAD-Job',
    model='VDLOAD-Model',
    userSubroutine='vdload_moving.for'
)
```

## Vs. DLOAD Comparison

| Aspect | DLOAD (Standard) | VDLOAD (Explicit) |
|--------|-----------------|-------------------|
| Solver | Implicit (Abaqus/Standard) | Explicit (Abaqus/Explicit) |
| Loop style | One point per call | Block of points per call |
| Performance | N/A | Vectorized — faster for many points |
| Use with UMAT | Compatible | Compatible with VUMAT |
| Integration | Each integration point | Each surface facet |

## Verification Checklist

- [ ] Value(I) is computed for all I = 1 to nBlock
- [ ] Pressure units are consistent (MPa in N-mm-MPa system)
- [ ] Moving load position synchronized with totalTime (not stepTime)
- [ ] No division by zero in spatial calculations
- [ ] amplitude multiplier is used correctly

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Load not moving | Using stepTime instead of totalTime | Use totalTime for absolute position |
| Zero pressure everywhere | Distance check too restrictive | Relax DIST2 condition |
| Negative pressure (unphysical) | Sign error in pressure formula | Check sign convention |
| Performance degradation | Scalar operations inside loop | Vectorize all operations over nBlock |
