C=======================================================================
C Abaqus Official Example: DLOAD for Distributed Load
C Time dependent and position dependent load
C=======================================================================
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS (3)
      CHARACTER*80 SNAME
C
      PARAMETER (HALF=0.5D0, TWO=2.D0)
C
C     TIME VARYING AND SPATIALLY VARYING PRESSURE LOAD
C     PROPORTIONAL TO X-COORDINATE AND TIME
C
C     F = COORDS(1) * TIME(1)
C
C     EXAMPLE: SINUSOIDAL VARIATION IN TIME AND SPACE
C
      PI = 4.D0*ATAN(1.D0)
      X = COORDS(1)
      Y = COORDS(2)
      Z = COORDS(3)
      T = TIME(2)
C
C     SPATIALLY DISTRIBUTED LOAD WITH TIME MODULATION
      SPATIAL_DIST = SIN(PI*X) * SIN(PI*Y)
      TIME_MOD = SIN(TWO*PI*T)
      F = SPATIAL_DIST * TIME_MOD
C
      RETURN
      END
