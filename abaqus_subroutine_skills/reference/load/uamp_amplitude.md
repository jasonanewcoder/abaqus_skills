# UAMP — Custom Amplitude — Detailed Reference

## Skill Description

UAMP defines a user amplitude function for Standard (implicit) and Explicit analyses:
loads, BCs, temperatures, etc. can all reference a `*Amplitude, definition=USER`.
Use it for control laws (PID), feedback from the analysis state (displacement-dependent
loading), or complex time functions that tabular amplitudes cannot express.

> 中文提示：UAMP 让载荷/边界条件变成「程序控制」——例如根据当前位移/温度
> 反馈调整载荷（自动加载、PID 控制、落锤速度控制）。比 TabularAmplitude 灵活得多。

## Interface

```fortran
      SUBROUTINE UAMP(
     1     AMPNAME, LOW, LCURDIR, NDOF, NMODES, NSECPTS,
     2     JSTEP, KINC, KSTEP, TINE, DURATION, DTIME, NOEL, NPT,
     3     LAYER, KSPT, KITER, KEVL, NOFFSET, FLAG, LFLAG,
     4     FREQ, TIME, DT, FIELD, NFIELD, U, DU, NDOFA, V, D,
     5     A, JTYPE, JDIED, NSCD, CDS, X, FX, COORDS, CP, PREDEF,
     6     STATEV, NSTATEV, PNEWDT, AMP, AMPHI, AMPA, AMPD, ROT,
     7     NROT, C1, C2, C3, L1, L2, L3, F1, F2, F3, IPERIOD,
     8     NCYCLE, NSAVE, AXIS, IDIR, NSECT, VAR, NVAR, DVAR, NDVAR,
     9     JSRT, JPSRT)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 AMPNAME
      INTEGER LOW(2), LCURDIR(2)
      DIMENSION TIME(2), FIELD(NFIELD), U(NDOF), DU(NDOFA), V(NDOFA),
     1 D(NDOFA), A(NDOFA), X(NDOFA), FX(NDOFA), COORDS(3),
     2 PREDEF(2,*), STATEV(NSTATEV), AMP(2), AMPHI(*), AMPA(*),
     3 AMPD(*), ROT(*), C1(3), C2(3), C3(3), F1(3), F2(3), F3(3),
     4 AXIS(*), VAR(NVAR), DVAR(NDVAR)
      REAL*8 CP(*), CDS(*)
```

Key arguments (simplified):

| Argument | Meaning |
|----------|---------|
| AMPNAME | Input: name of the amplitude definition |
| JSTEP, KINC, KSTEP, TINE | Input: step/increment info; TINE = current step time |
| DTIME | Input: current increment |
| TIME | Input: TIME(1)=step time, TIME(2)=total time |
| U, V, A | Input: displacements/velocities/accelerations at the control point |
| COORDS | Input: coordinates of the control point |
| FLAG, LFLAG | Input: 1 → first call of the step; 0 otherwise |
| FREQ | Input: suggested output frequency |
| STATEV | Input/Output: user state variables (like UMAT) |
| PNEWDT | Output: suggested new increment size (can request cutback) |
| AMP(1) | **Output: the amplitude value** |
| AMP(2) | Output: dAMP/dTIME |

## Template: Displacement-Controlled Feedback Load (simple PID-like)

```fortran
      SUBROUTINE UAMP(
     1     AMPNAME, LOW, LCURDIR, NDOF, NMODES, NSECPTS,
     2     JSTEP, KINC, KSTEP, TINE, DURATION, DTIME, NOEL, NPT,
     3     LAYER, KSPT, KITER, KEVL, NOFFSET, FLAG, LFLAG,
     4     FREQ, TIME, DT, FIELD, NFIELD, U, DU, NDOFA, V, D,
     5     A, JTYPE, JDIED, NSCD, CDS, X, FX, COORDS, CP, PREDEF,
     6     STATEV, NSTATEV, PNEWDT, AMP, AMPHI, AMPA, AMPD, ROT,
     7     NROT, C1, C2, C3, L1, L2, L3, F1, F2, F3, IPERIOD,
     8     NCYCLE, NSAVE, AXIS, IDIR, NSECT, VAR, NVAR, DVAR, NDVAR,
     9     JSRT, JPSRT)
C
C  Load grows to keep the displacement of DOF 1 at TARGET (mm):
C  AMP = KP * (TARGET - U(1))  with a cap.
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 AMPNAME
      INTEGER LOW(2), LCURDIR(2)
      DIMENSION TIME(2), FIELD(NFIELD), U(NDOF), DU(NDOFA), V(NDOFA),
     1 D(NDOFA), A(NDOFA), X(NDOFA), FX(NDOFA), COORDS(3),
     2 PREDEF(2,*), STATEV(NSTATEV), AMP(2), AMPHI(*), AMPA(*),
     3 AMPD(*), ROT(*), C1(3), C2(3), C3(3), F1(3), F2(3), F3(3),
     4 AXIS(*), VAR(NVAR), DVAR(NDVAR)
      REAL*8 CP(*), CDS(*)
C
      REAL*8 KP, TARGET, AMP_MAX
      PARAMETER (KP=1000.0D0)     ! proportional gain (N/mm)
      PARAMETER (TARGET=5.0D0)    ! target displacement (mm)
      PARAMETER (AMP_MAX=5.0D4)   ! load cap (N)
C
      IF (FLAG .EQ. 1) THEN
C       First call of the step: initialize
        STATEV(1) = 0.0D0
      END IF
C
C  Proportional feedback on DOF 1 of the control point
      AMP(1) = KP * (TARGET - U(1))
      IF (AMP(1) .GT.  AMP_MAX) AMP(1) =  AMP_MAX
      IF (AMP(1) .LT. -AMP_MAX) AMP(1) = -AMP_MAX
      AMP(2) = 0.0D0        ! derivative wrt time (for Newton) — usually 0
C
      RETURN
      END
```

## Input File Example

```abaqus
*Amplitude, name=Control-Amp, definition=USER, time=TOTAL TIME
** (state variables must be declared)
*User Amplitude, name=Control-Amp
** (list of UAMP state variable initial values, if any)
```

Loads/BCs referencing it:

```abaqus
*Cload
Load-Point, 1, 1.0
*Amplitude, name=Control-Amp, definition=USER
```

> In CAE: create the load, then in the amplitude field choose "User-defined" and
> give the amplitude name; the UAMP state variables come from the
> `*User Amplitude` keyword (edit the .inp).

## Guidance

1. `AMP(1)` is the amplitude multiplier — the actual load = input magnitude × AMP(1)
2. `FLAG=1` marks the first call of each step — initialize STATEV there
3. Set `PNEWDT` when you need smaller increments (feedback control often needs it)
4. `TIME(1)` is step time; use `DURATION` for the step length
5. Test the control law on a simple model first — feedback loops can oscillate

## Related

- `bc_load.md` — amplitudes on loads/BCs (tabular)
- `disp_control.md` / `vdisp_control.md` — prescribed displacement control
- `uexternaldb_mgmt.md` — loading control parameters from files at job start
