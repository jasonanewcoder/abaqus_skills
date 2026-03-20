C=======================================================================
C Abaqus Official Example: UMAT for Linear Elastic Material
C This is the standard example from Abaqus Documentation
C=======================================================================
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
C
      DIMENSION EELAS(6),EPLAS(6),FLOW(6)
      PARAMETER (ONE=1.0D0,TWO=2.0D0,THREE=3.0D0,SIX=6.0D0,
     1           ENUMAX=.4999D0,NEWTON=10,TOLER=1.0D-6)
C
C-----------------------------------------------------------------------
C     UMAT FOR ISOTROPIC ELASTICITY
C     CANNOT BE USED FOR PLANE STRESS
C-----------------------------------------------------------------------
C     PROPS(1) - E
C     PROPS(2) - NU
C-----------------------------------------------------------------------
C
C     ELASTIC PROPERTIES
      EMOD=PROPS(1)
      ENU=MIN(PROPS(2),ENUMAX)
      EBULK3=EMOD/(ONE-TWO*ENU)
      EG2=EMOD/(ONE+ENU)
      EG=EG2/TWO
      EG3=THREE*EG
      ELAM=(EBULK3-EG2)/THREE
C
C     ELASTIC STIFFNESS
C
      DO 20 K1=1,NDI
        DO 10 K2=1,NDI
          DDSDDE(K2,K1)=ELAM
 10     CONTINUE
        DDSDDE(K1,K1)=EG2+ELAM
 20   CONTINUE
      DO 40 K1=NDI+1,NTENS
        DDSDDE(K1,K1)=EG
 40   CONTINUE
C
C     CALCULATE STRESS FROM ELASTIC STRAINS
C
      DO 70 K1=1,NTENS
        DO 60 K2=1,NTENS
          STRESS(K2)=STRESS(K2)+DDSDDE(K2,K1)*DSTRAN(K1)
 60     CONTINUE
 70   CONTINUE
C
      RETURN
      END
