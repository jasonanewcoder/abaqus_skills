C=======================================================================
C Abaqus Official Example: VUEL for Explicit User Element
C Simple 2-node spring element for Abaqus/Explicit
C=======================================================================
      SUBROUTINE VUEL(nblock, rhs, amass, dtimeStable, svars,
     1 nsvars, energy, nenergy, nnode, ndof, nprops, njv,
     1 props, temp, u, v, a, dt, kstep, kinc, jelem,
     1 time, params, ndload, jdltype, adlmag, jpredef,
     1 jflags, ntable, table, label)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION rhs(nblock,ndof), amass(nblock,ndof,ndof),
     1 dtimeStable(nblock), svars(nblock,nsvars),
     2 energy(nblock,nenergy), props(nprops), temp(nblock),
     3 u(nblock,ndof), v(nblock,ndof), a(nblock,ndof),
     4 params(*), jdltype(ndload), adlmag(nblock,ndload),
     5 jpredef(*), jflags(*), table(ntable), jelem(nblock)
      CHARACTER*80 label
C
      PARAMETER (ZERO=0.D0, ONE=1.D0, TWO=2.D0)
C
C     USER SUBROUTINE FOR 2-NODE SPRING ELEMENT IN EXPLICIT
C     nnode = 2, ndof = 3 (3 DOF PER NODE)
C
C     props(1) = SPRING STIFFNESS
C     props(2) = DENSITY
C
      stiff = props(1)
      density = props(2)
C
      DO 100 k = 1, nblock
C       NODE 1 COORDINATES: u(k,1), u(k,2), u(k,3)
C       NODE 2 COORDINATES: u(k,4), u(k,5), u(k,6)
C
C       RELATIVE DISPLACEMENT
        dx = u(k,4) - u(k,1)
        dy = u(k,5) - u(k,2)
        dz = u(k,6) - u(k,3)
C
C       CURRENT LENGTH
        currLength = SQRT(dx*dx + dy*dy + dz*dz)
C
C       INITIAL LENGTH (STORED IN SVARS)
        IF (svars(k,1) .EQ. ZERO) THEN
          svars(k,1) = currLength  ! STORE INITIAL LENGTH
        END IF
        initLength = svars(k,1)
C
C       DIRECTION COSINES
        IF (currLength .GT. ZERO) THEN
          cx = dx / currLength
          cy = dy / currLength
          cz = dz / currLength
        ELSE
          cx = ZERO
          cy = ZERO
          cz = ZERO
        END IF
C
C       FORCE
        force = stiff * (currLength - initLength)
        svars(k,2) = force
C
C       RESIDUAL (INTERNAL FORCE)
        rhs(k,1) = -force * cx
        rhs(k,2) = -force * cy
        rhs(k,3) = -force * cz
        rhs(k,4) =  force * cx
        rhs(k,5) =  force * cy
        rhs(k,6) =  force * cz
C
C       MASS MATRIX (LUMPED)
        mass = density * initLength * 0.5D0
        DO i = 1, 6
          amass(k,i,i) = mass
        END DO
C
C       STABLE TIME INCREMENT
        dtimeStable(k) = 0.1D0 * SQRT(mass / stiff)
C
C       STRAIN ENERGY
        energy(k,1) = 0.5D0 * stiff * (currLength - initLength)**2
C
 100  CONTINUE
C
      RETURN
      END
