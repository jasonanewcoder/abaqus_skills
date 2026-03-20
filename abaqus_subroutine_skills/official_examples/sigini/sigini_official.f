C=======================================================================
C Abaqus Official Example: SIGINI for Initial Stress
C Define initial stress state
C=======================================================================
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
C     USER SUBROUTINE TO DEFINE INITIAL STRESS
C
C     SIGMA(1) - S11
C     SIGMA(2) - S22
C     SIGMA(3) - S33
C     SIGMA(4) - S12
C     SIGMA(5) - S13 (IF NTENS > 4)
C     SIGMA(6) - S23 (IF NTENS > 4)
C
C     EXAMPLE: INITIAL STRESS VARYING WITH DEPTH (Z COORDINATE)
      Z = COORDS(3)
      DEPTH = -Z    ! ASSUME Z IS UPWARD POSITIVE
      IF (DEPTH .LT. 0.D0) DEPTH = 0.D0
C
C     LINEAR STRESS DISTRIBUTION WITH DEPTH
      SY = -100.D0 * DEPTH    ! VERTICAL STRESS (COMPRESSIVE)
      SX = -50.D0 * DEPTH     ! HORIZONTAL STRESS
C
      SIGMA(1) = SX
      SIGMA(2) = SX
      SIGMA(3) = SY
      SIGMA(4) = 0.D0
      IF (NTENS .GT. 4) THEN
        SIGMA(5) = 0.D0
        SIGMA(6) = 0.D0
      END IF
C
      RETURN
      END
