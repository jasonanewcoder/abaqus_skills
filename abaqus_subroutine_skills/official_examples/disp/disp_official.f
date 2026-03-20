C=======================================================================
C Abaqus Official Example: DISP for Imposed Displacement
C Time dependent displacement boundary condition
C=======================================================================
      SUBROUTINE DISP(U,KSTEP,KINC,TIME,NOEL,NPT,COORDS,JLTYP,
     1 SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION U(3), TIME(2), COORDS (3)
      CHARACTER*80 SNAME
C
      PARAMETER (HALF=0.5D0, ONE=1.D0, TWO=2.D0, PI=3.141592653589793D0)
C
C     USER SUBROUTINE TO DEFINE TIME DEPENDENT DISPLACEMENT
C
C     U(1) - DISPLACEMENT IN X DIRECTION
C     U(2) - DISPLACEMENT IN Y DIRECTION
C     U(3) - DISPLACEMENT IN Z DIRECTION
C
C     RAMP DISPLACEMENT
      IF (TIME(2) .LE. ONE) THEN
        U(1) = TIME(2)
      ELSE
        U(1) = ONE
      END IF
C
C     SINUSOIDAL DISPLACEMENT IN Y DIRECTION
      U(2) = SIN(TWO*PI*TIME(2))
C
C     ZERO DISPLACEMENT IN Z DIRECTION
      U(3) = 0.D0
C
      RETURN
      END
