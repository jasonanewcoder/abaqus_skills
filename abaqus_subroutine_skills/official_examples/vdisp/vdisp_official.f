C=======================================================================
C Abaqus Official Example: VDISP for Explicit Displacement
C For Abaqus/Explicit
C=======================================================================
      SUBROUTINE VDISP(nblock, nDof, nCoord, kstep, kinc,
     1 stepTime, totalTime, dtNext, dt, cbname, coordNp,
     2 u, v, a, rf)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION u(nblock, nDof), v(nblock, nDof), a(nblock, nDof),
     1 coordNp(nblock, nCoord), rf(nblock, nDof)
      CHARACTER*80 cbname
C
C     USER SUBROUTINE FOR DISPLACEMENT BOUNDARY IN EXPLICIT
C
C     nblock    - NUMBER OF POINTS
C     nDof      - NUMBER OF DOF
C     stepTime  - CURRENT STEP TIME
C     totalTime - TOTAL TIME
C     coordNp   - CURRENT COORDINATES
C     u         - DISPLACEMENT TO BE DEFINED
C     v         - VELOCITY TO BE DEFINED
C     a         - ACCELERATION TO BE DEFINED
C
C     EXAMPLE: SINUSOIDAL DISPLACEMENT
      DO 100 k = 1, nblock
        x = coordNp(k,1)
        y = coordNp(k,2)
C
C       SINUSOIDAL DISPLACEMENT IN X DIRECTION
        u(k,1) = 0.1D0 * SIN(6.2831853D0 * totalTime) * x
        v(k,1) = 0.1D0 * 6.2831853D0 * COS(6.2831853D0 * totalTime) * x
        a(k,1) = -0.1D0 * (6.2831853D0**2) * SIN(6.2831853D0 * totalTime) * x
C
C       ZERO DISPLACEMENT IN OTHER DIRECTIONS
        u(k,2) = 0.D0
        u(k,3) = 0.D0
        v(k,2) = 0.D0
        v(k,3) = 0.D0
        a(k,2) = 0.D0
        a(k,3) = 0.D0
 100  CONTINUE
C
      RETURN
      END
