C=======================================================================
C Abaqus Official Example: FILM for User Defined Film Coefficient
C Define convection coefficient as function of temperature and position
C=======================================================================
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION H(2), TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
C     USER SUBROUTINE TO DEFINE FILM COEFFICIENT
C
C     H(1) - FILM COEFFICIENT
C     H(2) - DERIVATIVE OF H WITH RESPECT TO TEMPERATURE
C     SINK - SINK TEMPERATURE
C
C     EXAMPLE: TEMPERATURE DEPENDENT FILM COEFFICIENT
      T = TEMP
C
C     NATURAL CONVECTION: H INCREASES WITH TEMPERATURE
      H0 = 10.D0       ! BASE FILM COEFFICIENT
      BETA = 0.1D0     ! TEMPERATURE DEPENDENCE
      H(1) = H0 * (1.D0 + BETA * (T - 20.D0))
C
C     DERIVATIVE
      H(2) = H0 * BETA
C
C     SINK TEMPERATURE
      SINK = 20.D0     ! AMBIENT TEMPERATURE
C
      RETURN
      END
