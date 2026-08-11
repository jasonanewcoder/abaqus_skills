C=======================================================================
C DFLUX user subroutine - Goldak double-ellipsoid moving heat source
C Companion to cross_module_examples/dflux_welding/model_setup.py
C Units: N-mm-MPa-s (power in mW, distances in mm, time in s)
C=======================================================================
      SUBROUTINE DFLUX(FLUX,SOL,JSTEP,JINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 EFF, VOLTAGE, CURRENT, V, T
      REAL*8 A_F, A_R, B, C_D, Q
      REAL*8 X, Y, Z, X0, Y0, Z0, XI
      REAL*8 F_F, F_R, F1, F2, Q1, Q2
      REAL*8 PI
      PARAMETER(PI=3.14159265358979D0)
C
C-----------------------------------------------------------------------
C Welding parameters (edit here; also mirrored in model_setup.py)
C-----------------------------------------------------------------------
      EFF     = 0.80D0     ! arc efficiency
      VOLTAGE = 24.0D0     ! V
      CURRENT = 180.0D0    ! A
      V       = 4.0D0      ! travel speed (mm/s)
      A_F     = 3.0D0      ! front semi-axis (mm)
      A_R     = 6.0D0      ! rear semi-axis (mm)
      B       = 3.0D0      ! half-width (mm)
      C_D     = 2.5D0      ! depth (mm)
C
      Q  = EFF*VOLTAGE*CURRENT*1000.0D0     ! net power (mW)
      F_F = 2.0D0*A_F/(A_F+A_R)             ! front fraction
      F_R = 2.0D0*A_R/(A_F+A_R)             ! rear fraction
C
C-----------------------------------------------------------------------
C Source center: starts at X=50, travels along X
C-----------------------------------------------------------------------
      T  = TIME(2)
      X0 = 50.0D0 + V*T
      Y0 = 25.0D0
      Z0 = 0.0D0
C
      X  = COORDS(1)
      Y  = COORDS(2)
      Z  = COORDS(3)
      XI = X - X0
C
C-----------------------------------------------------------------------
C Goldak double ellipsoid (volumetric, JLTYP=0)
C-----------------------------------------------------------------------
      IF (XI .GE. 0.0D0) THEN
C       Front half
        F1 = 6.0D0*SQRT(3.0D0)*F_F*Q/(A_F*B*C_D*PI*SQRT(PI))
        Q1 = EXP(-3.0D0*(XI/A_F)**2)
     1     * EXP(-3.0D0*((Y-Y0)/B)**2)
     2     * EXP(-3.0D0*((Z-Z0)/C_D)**2)
        FLUX(1) = F1*Q1
      ELSE
C       Rear half
        F2 = 6.0D0*SQRT(3.0D0)*F_R*Q/(A_R*B*C_D*PI*SQRT(PI))
        Q2 = EXP(-3.0D0*(XI/A_R)**2)
     1     * EXP(-3.0D0*((Y-Y0)/B)**2)
     2     * EXP(-3.0D0*((Z-Z0)/C_D)**2)
        FLUX(1) = F2*Q2
      END IF
C
      FLUX(2) = 0.0D0       ! dFLUX/dT = 0
C
      RETURN
      END
