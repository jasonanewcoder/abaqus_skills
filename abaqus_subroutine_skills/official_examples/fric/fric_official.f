C=======================================================================
C Abaqus Official Example: FRIC for User Defined Friction
C Define friction coefficient as function of slip rate and pressure
C=======================================================================
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
C     USER SUBROUTINE TO DEFINE FRICTION
C
C     FRICOUT(1) - TANGENTIAL FRICTION STRESS
C     FRICOUT(2) - FRICTION COEFFICIENT
C
C     CPRESS - CONTACT PRESSURE
C     DRDT   - SLIP RATE
C     TEMP   - TEMPERATURE
C
C     EXAMPLE: COULOMB FRICTION WITH SLIP RATE DEPENDENCE
C     MU = MU0 * (1 - A * |DRDT|)
C
      MU0 = 0.3D0    ! STATIC FRICTION COEFFICIENT
      A   = 0.01D0   ! RATE DEPENDENCE PARAMETER
C
      V = ABS(DRDT)
      MU = MU0 * (1.D0 - A * V)
      IF (MU .LT. 0.1D0) MU = 0.1D0
C
C     FRICTION STRESS = MU * PRESSURE
      FRICOUT(1) = MU * CPRESS
      FRICOUT(2) = MU
C
      RETURN
      END
