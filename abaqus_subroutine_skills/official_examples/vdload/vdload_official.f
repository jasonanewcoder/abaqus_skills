C=======================================================================
C Abaqus Official Example: VDLOAD for Explicit Distributed Load
C For Abaqus/Explicit
C=======================================================================
      SUBROUTINE VDLOAD(nblock, ndim, stepTime, totalTime,
     1 amplitude, curCoords, velocity, dirCos, label,
     2 value)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION curCoords(nblock,ndim), velocity(nblock,ndim),
     1 dirCos(nblock,ndim,ndim), value(nblock)
      CHARACTER*80 label
C
C     USER SUBROUTINE FOR DISTRIBUTED LOAD IN EXPLICIT
C
C     nblock    - NUMBER OF POINTS TO BE PROCESSED
C     ndim      - NUMBER OF COORDINATE DIRECTIONS
C     stepTime  - CURRENT STEP TIME
C     totalTime - TOTAL TIME
C     curCoords - CURRENT COORDINATES
C     value     - LOAD VALUE TO BE DEFINED
C
C     EXAMPLE: TIME AND POSITION VARYING PRESSURE
      DO 100 k = 1, nblock
        x = curCoords(k,1)
        y = curCoords(k,2)
        z = 0.D0
        IF (ndim .GT. 2) z = curCoords(k,3)
C
C       SINUSOIDAL SPATIAL DISTRIBUTION WITH TIME MODULATION
        value(k) = amplitude * SIN(3.1415926D0 * x) 
     1             * SIN(3.1415926D0 * y) 
     2             * SIN(6.2831853D0 * totalTime)
 100  CONTINUE
C
      RETURN
      END
