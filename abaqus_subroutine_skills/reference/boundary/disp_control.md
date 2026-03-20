# Abaqus DISP Custom Boundary Condition Subroutine Skill

## Skill Description

This skill guides AI to generate custom displacement boundary condition subroutines DISP for Abaqus Standard, implementing complex displacement control such as sinusoidal vibration, multi-point motion coordination, etc.

## Applicable Scenarios

- Sinusoidal/random vibration excitation
- Multi-DOF coordinated motion
- Displacement-controlled fatigue test simulation
- Geometric nonlinear large displacement problems

## Key Features

| Feature | Description |
|---------|-------------|
| Analysis Type | Implicit/Explicit Dynamics |
| Control Type | Displacement, Velocity, Acceleration |
| Time Function | Arbitrary time-dependent function |
| Spatial Distribution | Coordinate-based, node set-based distribution |

## DISP Interface Definition

```fortran
SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| U(1) | Output | Displacement 1 (X direction or DOF 1) |
| U(2) | Output | Displacement 2 (Y direction or DOF 2) |
| U(3) | Output | Displacement 3 (Z direction or DOF 3) |
| TIME(1) | Input | Current increment time |
| TIME(2) | Input | Total time |
| COORDS(3) | Input | Node coordinates |
| NOEL | Input | Element number (node number) |
| KSTEP | Input | Step number |

## Displacement Control Types

### 1. Sinusoidal Vibration Displacement

```fortran
      SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
C
C  Sinusoidal vibration displacement boundary condition
C  Amplitude and frequency adjustable
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION U(3), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 AMP, FREQ, PHASE, T, PI
      PARAMETER(PI=3.141592653589793D0)
C
C-----------------------------------------------------------------------
C  Vibration parameters
C-----------------------------------------------------------------------
      AMP   = 1.0D-3       ! Amplitude (m)
      FREQ  = 10.0D0       ! Frequency (Hz)
      PHASE = 0.0D0        ! Initial phase (rad)
C
C-----------------------------------------------------------------------
C  Calculate displacement
C-----------------------------------------------------------------------
      T = TIME(2)
C
C  Apply sinusoidal displacement only in X direction
      U(1) = AMP * SIN(2.0D0*PI*FREQ*T + PHASE)
      U(2) = 0.0D0
      U(3) = 0.0D0
C
      RETURN
      END
```

### 2. Sweep Vibration (Frequency Linearly Increasing)

```fortran
      SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
C
C  Sweep vibration displacement - frequency varies linearly with time
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION U(3), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 AMP, F0, F1, T_TOTAL, T, PI
      REAL*8 F_INST, PHASE
      PARAMETER(PI=3.141592653589793D0)
C
C-----------------------------------------------------------------------
C  Sweep parameters
C-----------------------------------------------------------------------
      AMP     = 1.0D-3     ! Amplitude (m)
      F0      = 5.0D0      ! Start frequency (Hz)
      F1      = 100.0D0    ! End frequency (Hz)
      T_TOTAL = 10.0D0     ! Total sweep time (s)
C
C-----------------------------------------------------------------------
C  Calculate instantaneous frequency (linear sweep)
C-----------------------------------------------------------------------
      T = TIME(2)
      IF (T .GT. T_TOTAL) THEN
        F_INST = F1
      ELSE
        F_INST = F0 + (F1 - F0) * T / T_TOTAL
      END IF
C
C-----------------------------------------------------------------------
C  Calculate phase (integral of frequency)
C  Linear sweep: φ(t) = 2π(f₀t + (f₁-f₀)t²/(2T))
C-----------------------------------------------------------------------
      PHASE = 2.0D0*PI*(F0*T + (F1-F0)*T*T/(2.0D0*T_TOTAL))
C
C-----------------------------------------------------------------------
C  Calculate displacement
C-----------------------------------------------------------------------
      U(1) = AMP * SIN(PHASE)
      U(2) = 0.0D0
      U(3) = 0.0D0
C
      RETURN
      END
```

### 3. Spatial Distribution Displacement (Bending Deformation)

```fortran
      SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
C
C  Spatial distribution displacement - simulate beam bending
C  Displacement follows cubic polynomial along length
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION U(3), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 MAX_DISP, L, X, RAMP, T
      REAL*8 SHAPE_FUNC
C
C-----------------------------------------------------------------------
C  Parameters
C-----------------------------------------------------------------------
      MAX_DISP = 0.01D0    ! Maximum displacement (m)
      L        = 1.0D0     ! Beam length (m)
      T = TIME(2)
C
C-----------------------------------------------------------------------
C  Time ramp function
C-----------------------------------------------------------------------
      IF (T .LT. 1.0D0) THEN
        RAMP = T
      ELSE
        RAMP = 1.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Get node X coordinate (assuming beam along X direction)
C-----------------------------------------------------------------------
      X = COORDS(1)
C
C-----------------------------------------------------------------------
C  Calculate shape function (simply supported first bending mode)
C  w(x) = sin(πx/L)
C-----------------------------------------------------------------------
      IF (X .GE. 0.0D0 .AND. X .LE. L) THEN
        SHAPE_FUNC = SIN(3.141592653589793D0 * X / L)
      ELSE
        SHAPE_FUNC = 0.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Z direction displacement (transverse bending)
C-----------------------------------------------------------------------
      U(1) = 0.0D0
      U(2) = 0.0D0
      U(3) = MAX_DISP * RAMP * SHAPE_FUNC
C
      RETURN
      END
```

### 4. Rotational Motion (Rigid Body Rotation)

```fortran
      SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
C
C  Rigid body rotation displacement - rotate about Z axis
C  Suitable for displacement control of rotating components
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION U(3), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 X0, Y0, OMEGA, T, THETA
      REAL*8 X, Y, DX, DY
      REAL*8 X_NEW, Y_NEW
C
C-----------------------------------------------------------------------
C  Rotation parameters
C-----------------------------------------------------------------------
      X0    = 0.0D0        ! Rotation center X coordinate
      Y0    = 0.0D0        ! Rotation center Y coordinate
      OMEGA = 1.0D0        ! Angular velocity (rad/s)
C
C-----------------------------------------------------------------------
C  Calculate current rotation angle
C-----------------------------------------------------------------------
      T = TIME(2)
      THETA = OMEGA * T
C
C-----------------------------------------------------------------------
C  Get node coordinates relative to rotation center
C-----------------------------------------------------------------------
      X = COORDS(1) - X0
      Y = COORDS(2) - Y0
C
C-----------------------------------------------------------------------
C  Calculate rotated position
C-----------------------------------------------------------------------
      X_NEW = X * COS(THETA) - Y * SIN(THETA)
      Y_NEW = X * SIN(THETA) + Y * COS(THETA)
C
C-----------------------------------------------------------------------
C  Calculate displacement increment
C-----------------------------------------------------------------------
      DX = X_NEW - X
      DY = Y_NEW - Y
C
      U(1) = DX
      U(2) = DY
      U(3) = 0.0D0
C
      RETURN
      END
```

## Input File Example

```abaqus
** Displacement boundary condition
*Boundary, user
Node_Set, 1, 1
Node_Set, 2, 2
Node_Set, 3, 3
**
** Or use keyword
*Boundary, type=DISPLACEMENT, user
Node_Set, 1, 3
```

## Differences from VDISP

| Feature | DISP (Standard) | VDISP (Explicit) |
|---------|-----------------|------------------|
| Output | Total displacement | Total displacement |
| Processing Method | Per node | Block processing |
| Typical Application | Low frequency vibration | Impact, transient |

## Notes

1. **Displacement Compatibility**: Multi-node displacements should be coordinated to avoid tearing
2. **Time Continuity**: Displacement function should be continuously differentiable with respect to time
3. **Velocity/Acceleration**: Abaqus automatically calculates velocity and acceleration
4. **Large Displacement**: In geometric nonlinear analysis, displacement may accumulate

## Extension Directions

- Random vibration (PSD control)
- Multi-axis coordinated motion
- Feedback-based active control
- Data exchange with external controllers

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 34.3
