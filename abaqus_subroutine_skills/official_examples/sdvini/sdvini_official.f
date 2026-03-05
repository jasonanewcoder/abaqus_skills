C=======================================================================
C Abaqus Official Example: SDVINI for Initial State Variables
C Define initial values for solution dependent state variables
C=======================================================================
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
C
C     USER SUBROUTINE TO DEFINE INITIAL STATE VARIABLES
C
C     STATEV(1) - FIRST STATE VARIABLE
C     STATEV(2) - SECOND STATE VARIABLE
C     ...
C
C     EXAMPLE: INITIALIZE STATE VARIABLES BASED ON COORDINATES
      X = COORDS(1)
      Y = COORDS(2)
      Z = COORDS(3)
C
C     INITIALIZE ALL STATE VARIABLES TO ZERO
      DO 10 I = 1,NSTATV
        STATEV(I) = 0.D0
 10   CONTINUE
C
C     OR INITIALIZE BASED ON POSITION
C     STATEV(1) = X
C     STATEV(2) = Y
C     STATEV(3) = Z
C
      RETURN
      END
