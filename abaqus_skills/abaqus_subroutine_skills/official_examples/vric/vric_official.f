C=======================================================================
C Abaqus Official Example: VRIC for Explicit Friction
C For Abaqus/Explicit
C=======================================================================
      SUBROUTINE VRIC(nBlock, nProps, nTemp, nField, jFlags,
     1 jData, props, temp, field, cpres, cshear, cq, cslip,
     2 cslipRate, cDot, cCoord, cAloc, dAux, dSlip, dSlipRate,
     2 dStress, alpha)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION jFlags(*), jData(*), props(nProps),
     1 temp(nBlock), field(nBlock,nField), cpres(nBlock),
     2 cshear(nBlock,2), cq(nBlock), cslip(nBlock,2),
     3 cslipRate(nBlock,2), cDot(nBlock), cCoord(nBlock,3),
     4 cAloc(nBlock,2), dAux(nBlock,10), dSlip(nBlock,2),
     5 dSlipRate(nBlock,2), dStress(nBlock,2), alpha(nBlock)
C
C     USER SUBROUTINE FOR FRICTION IN EXPLICIT
C
C     nBlock       - NUMBER OF CONTACT POINTS
C     props        - MATERIAL PROPERTIES
C     cpres        - CONTACT PRESSURE
C     cshear       - SHEAR STRESS
C     cslipRate    - SLIP RATE
C     alpha        - FRICTION COEFFICIENT TO BE DEFINED
C
C     EXAMPLE: VELOCITY DEPENDENT FRICTION
      DO 100 k = 1, nBlock
C       SLIP VELOCITY MAGNITUDE
        vMag = SQRT(cslipRate(k,1)**2 + cslipRate(k,2)**2)
C
C       FRICTION COEFFICIENT DECREASES WITH VELOCITY
        mu0 = 0.4D0     ! STATIC FRICTION
        muInf = 0.2D0   ! DYNAMIC FRICTION
        vCrit = 1.0D0   ! CRITICAL VELOCITY
C
        alpha(k) = muInf + (mu0 - muInf) * EXP(-vMag/vCrit)
 100  CONTINUE
C
      RETURN
      END
