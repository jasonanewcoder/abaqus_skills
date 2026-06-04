# VDISP — Explicit Displacement Boundary Condition Subroutine

## Skill Description

VDISP prescribes displacement boundary conditions for Abaqus/Explicit analysis. Unlike DISP (implicit, one point per call), VDISP processes a block of nodes simultaneously.

## Applicable Scenarios

- Moving boundary conditions (prescribed motion of tool/indenter)
- Seismic base excitation (ground motion)
- Vibration testing with input motion
- Impact with prescribed velocity
- Flexible multi-body constraints

## Interface Definition

```fortran
      subroutine vdisp(
C     Read only —
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
C     Write only —
     4 u, v, a)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| nBlock | Input | Number of nodes in block |
| ndim | Input | Number of dimensions |
| stepTime | Input | Current step time |
| totalTime | Input | Current total time |
| amplitude | Input | Amplitude curve value at this time |
| curCoords(nBlock,ndim) | Input | Current nodal coordinates |
| velocity(nBlock,ndim) | Input | Current nodal velocities |
| dirCos(nBlock,ndim,ndim) | Input | Direction cosines |
| jltyp | Input | Boundary condition type |
| sname | Input | Boundary condition name |
| u(nBlock,ndim) | Output | Prescribed displacements |
| v(nBlock,ndim) | Output | Prescribed velocities |
| a(nBlock,ndim) | Output | Prescribed accelerations |

**Important**: For displacement BCs (type=0), set `u`, `v`, `a`. For velocity BCs (type=1), set `v`, `a`. For acceleration BCs (type=2), set `a`.

## Fortran Code Template

### Template 1: Seismic Base Excitation

```fortran
      subroutine vdisp(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 u, v, a)
C
C     Seismic base excitation: prescribe ground motion
C     Input: acceleration time history (recorded or synthetic)
C     Output: displacement, velocity, acceleration
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim)
      dimension u(nBlock,ndim), v(nBlock,ndim), a(nBlock,ndim)
      character*80 sname
C
      real*8 OMEGA, A0, T, D_GROUND, V_GROUND, A_GROUND
      integer I, IDIM
C
      parameter (OMEGA=12.57D0)       ! Angular frequency (rad/s, ~2 Hz)
      parameter (A0=9800.0D0)          ! Peak acceleration (mm/s², ~1g)
C
      T = totalTime
C
C-----------------------------------------------------------------------
C     Harmonic ground motion (sine sweep for demonstration)
C-----------------------------------------------------------------------
      A_GROUND = A0 * sin(OMEGA * T) * (1.0D0 + 0.5D0 * T)
      V_GROUND = -(A0 / OMEGA) * cos(OMEGA * T)  ! Simplified integration
      D_GROUND = -(A0 / (OMEGA**2)) * sin(OMEGA * T)
C
C-----------------------------------------------------------------------
C     Apply same motion to all nodes (rigid base)
C-----------------------------------------------------------------------
      do I = 1, nBlock
C       Apply in X-direction only
        u(I, 1) = D_GROUND * amplitude
        v(I, 1) = V_GROUND * amplitude
        a(I, 1) = A_GROUND * amplitude
C
C       Other directions: fixed
        do IDIM = 2, ndim
          u(I, IDIM) = 0.0D0
          v(I, IDIM) = 0.0D0
          a(I, IDIM) = 0.0D0
        end do
      end do
C
      return
      end
```

### Template 2: Moving Tool (Indentation/Punch)

```fortran
      subroutine vdisp(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 u, v, a)
C
C     Moving rigid tool: controlled indentation with velocity profile
C     Approach → hold → retract
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim)
      dimension u(nBlock,ndim), v(nBlock,ndim), a(nBlock,ndim)
      character*80 sname
C
      real*8 V_APPROACH, V_RETRACT, DWELL_TIME, HOLD_TIME
      real*8 T_APPROACH, T_RETRACT, D_CURRENT, V_CURRENT, A_CURRENT
      real*8 T
      integer I, IDIM
C
      parameter (V_APPROACH=-100.0D0)  ! mm/s (negative = downward)
      parameter (V_RETRACT=50.0D0)     ! mm/s
      parameter (DWELL_TIME=0.5D0)     ! s, dwell at max depth
      parameter (HOLD_TIME=0.2D0)      ! s, hold after approach
C
      T = totalTime
      T_APPROACH = DWELL_TIME          ! Approach phase duration
      T_RETRACT = T_APPROACH + HOLD_TIME + DWELL_TIME
C
C-----------------------------------------------------------------------
C     Determine motion phase
C-----------------------------------------------------------------------
      if (T .le. T_APPROACH) then
C       Approach phase
        V_CURRENT = V_APPROACH
        A_CURRENT = 0.0D0
        D_CURRENT = V_APPROACH * T
C
      else if (T .le. T_APPROACH + HOLD_TIME) then
C       Hold phase
        V_CURRENT = 0.0D0
        A_CURRENT = 0.0D0
        D_CURRENT = V_APPROACH * T_APPROACH  ! Stay at max depth
C
      else if (T .le. T_RETRACT) then
C       Retract phase
        V_CURRENT = V_RETRACT
        A_CURRENT = 0.0D0
        D_CURRENT = V_APPROACH * T_APPROACH
     1            + V_RETRACT * (T - T_APPROACH - HOLD_TIME)
C
      else
C       Done — hold at final position
        V_CURRENT = 0.0D0
        A_CURRENT = 0.0D0
        D_CURRENT = V_APPROACH * T_APPROACH
     1            + V_RETRACT * (T_RETRACT - T_APPROACH - HOLD_TIME)
      end if
C
C-----------------------------------------------------------------------
C     Apply to all nodes (Z-displacement)
C-----------------------------------------------------------------------
      do I = 1, nBlock
C       Apply in Z-direction
        if (ndim .ge. 3) then
          u(I, 3) = D_CURRENT * amplitude
          v(I, 3) = V_CURRENT * amplitude
          a(I, 3) = A_CURRENT * amplitude
        end if
C
C       Other directions: constrained
        if (ndim .ge. 1) then
          u(I, 1) = 0.0D0
          v(I, 1) = 0.0D0
          a(I, 1) = 0.0D0
        end if
        if (ndim .ge. 2) then
          u(I, 2) = 0.0D0
          v(I, 2) = 0.0D0
          a(I, 2) = 0.0D0
        end if
      end do
C
      return
      end
```

### Template 3: Multi-Axis Motion (Orbital/Planar)

```fortran
      subroutine vdisp(
     1 nBlock, ndim, stepTime, totalTime,
     2 amplitude, curCoords, velocity, dirCos,
     3 jltyp, sname,
     4 u, v, a)
C
C     Orbital motion: circular path in X-Y plane
C     Useful for wear/fretting simulations
C
      include 'vaba_param.inc'
C
      dimension curCoords(nBlock,ndim), velocity(nBlock,ndim),
     1          dirCos(nBlock,ndim,ndim)
      dimension u(nBlock,ndim), v(nBlock,ndim), a(nBlock,ndim)
      character*80 sname
C
      real*8 RADIUS, OMEGA, T
      real*8 D_X, D_Y, V_X, V_Y, A_X, A_Y
      integer I
C
      parameter (RADIUS=5.0D0)        ! Orbital radius (mm)
      parameter (OMEGA=6.283D0)        ! Angular speed (rad/s, 1 Hz)
C
      T = totalTime * amplitude
C
C     Kinematics of circular motion
      D_X = RADIUS * cos(OMEGA * T) - RADIUS  ! Offset to start at (0,0)
      D_Y = RADIUS * sin(OMEGA * T)
C
      V_X = -RADIUS * OMEGA * sin(OMEGA * T)
      V_Y =  RADIUS * OMEGA * cos(OMEGA * T)
C
      A_X = -RADIUS * OMEGA**2 * cos(OMEGA * T)
      A_Y = -RADIUS * OMEGA**2 * sin(OMEGA * T)
C
      do I = 1, nBlock
        u(I, 1) = D_X
        u(I, 2) = D_Y
        v(I, 1) = V_X
        v(I, 2) = V_Y
        a(I, 1) = A_X
        a(I, 2) = A_Y
        if (ndim .ge. 3) then
          u(I, 3) = 0.0D0
          v(I, 3) = 0.0D0
          a(I, 3) = 0.0D0
        end if
      end do
C
      return
      end
```

## Abaqus Input File Syntax

```
*Boundary, type=DISPLACEMENT, USER
<node_set>, <first_dof>, <last_dof>
```

For velocity BC:

```
*Boundary, type=VELOCITY, USER
<node_set>, <first_dof>, <last_dof>
```

## Python Script Integration

```python
# Define node set for VDISP
fixed_nodes = instance.nodes.getByBoundingBox(
    0, 0, 0, plate_width, 0, plate_thickness
)
node_region = assembly.Set(name='Base-Nodes', nodes=fixed_nodes)

# Apply user-defined displacement BC
model.DisplacementBC(
    name='User-Motion',
    createStepName='Explicit-Step',
    region=node_region,
    u1=UNSET, u2=UNSET, u3=UNSET,  # Will be determined by VDISP
    distributionType=USER_DEFINED
)

# Requires explicit step
model.ExplicitDynamicsStep(
    name='Explicit-Step',
    previous='Initial',
    timePeriod=1.0
)

# Submit with user subroutine
job = mdb.Job(
    name='VDISP-Job',
    model='VDISP-Model',
    userSubroutine='vdisp_motion.for'
)
```

## VDISP vs. DISP

| Aspect | DISP (Standard) | VDISP (Explicit) |
|--------|----------------|-------------------|
| Solver | Implicit | Explicit |
| Loop style | One node per call | Block of nodes |
| Output required | u only (v,a computed) | u, v, a (all must be set) |
| Consistency | V and A computed from u | Must provide all three consistently |
| Use case | Slow/quasi-static | Dynamic, fast-varying |

## Consistency Requirement

For explicit dynamics, `u`, `v`, and `a` must be kinematically consistent:

```
v = du/dt  (approximately)
a = dv/dt  (approximately)
```

In practice, Abaqus uses your `v` and `a` outputs directly. For smooth motion, use analytical derivatives. For tabular data, use central differences.

## Verification Checklist

- [ ] u, v, a are set for all nodes (I = 1 to nBlock)
- [ ] u, v, a are kinematically consistent
- [ ] Motion boundaries updated every explicit increment
- [ ] totalTime (not stepTime) used for absolute position tracking

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Jerky motion | Inconsistent u, v, a | Use analytical derivatives |
| Nodes not moving | jltyp mismatch | Check BC type in input file |
| Excessive energy | Velocity/acceleration spike | Smooth transition at phase changes |
| All DOFs locked | Uninitialized output for some DOFs | Set ALL u(I,1:ndim) explicitly |
