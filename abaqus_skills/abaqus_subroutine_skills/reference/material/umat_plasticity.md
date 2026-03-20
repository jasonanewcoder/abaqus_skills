# Abaqus UMAT Elastoplastic Material Subroutine Skill

## Skill Description

This skill guides AI to generate isotropic hardening elastoplastic UMAT subroutines based on von Mises yield criterion using Radial Return Mapping algorithm.

## Applicable Scenarios

- Plastic deformation analysis of metal materials
- Large deformation small strain problems
- Isotropic hardening materials

## Key Features

| Feature | Description |
|---------|-------------|
| Yield Criterion | von Mises |
| Hardening Model | Isotropic hardening (linear/power law) |
| Flow Rule | Associated flow rule |
| Algorithm | Radial Return Mapping (exact consistent tangent) |
| Large Deformation | Supported (based on Jaumann rate) |

## Theoretical Formulas

### 1. Yield Function

```
f = ||s|| - √(2/3) * σ_y(ε̄^p) ≤ 0
```

Where s is deviatoric stress, σ_y is yield stress, ε̄^p is equivalent plastic strain.

### 2. Flow Rule

```
Δε^p = Δγ * ∂f/∂σ = Δγ * (3/2) * s/||s||
```

### 3. Hardening Law (Power Law)

```
σ_y = σ_0 + K*(ε̄^p)^n
```

### 4. Radial Return Algorithm

```
1. Elastic predictor: σ^trial = σ_n + C:Δε
2. Deviatoric stress: s^trial = dev(σ^trial)
3. Yield check: f^trial = ||s^trial|| - √(2/3)*σ_y
4. If f^trial > 0:
   Δγ = f^trial / (2*G + (2/3)*H)
   s_{n+1} = s^trial * (1 - 2*G*Δγ/||s^trial||)
   ε̄^p_{n+1} = ε̄^p_n + √(2/3)*Δγ
```

## Material Parameters

| Parameter | Symbol | Unit | Description |
|-----------|--------|------|-------------|
| Young's Modulus | E | MPa | Elastic modulus |
| Poisson's Ratio | ν | - | Poisson's ratio |
| Initial Yield Stress | σ_0 | MPa | Yield onset |
| Hardening Coefficient | K | MPa | Hardening curve parameter |
| Hardening Exponent | n | - | Power law hardening exponent |

## Fortran Code

```fortran
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C
C  von Mises Elastoplastic UMAT - Radial Return Algorithm
C  Isotropic hardening, associated flow rule
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
C
C  Material parameters
      REAL*8 E, NU, SIGMA_Y, HARD_K, HARD_N
      REAL*8 G, KMOD, LAM, FAC
C  Stress/strain related
      REAL*8 STRESS_TRIAL(6), STRESS_DEV(6)
      REAL*8 STRAIN_ELAS(6)
      REAL*8 EQPLAS, DEQPL, SMIS_EFF, SMIS_TRIAL
      REAL*8 YIELD_STRESS, HARD_MOD
      REAL*8 DGAMMA, FACTOR, ONEMFAC
      REAL*8 TERM1, TERM2, TERM3
      INTEGER I, J
      PARAMETER(TOLER=1.0D-10, SQRT_2_3=0.8164965809D0)
C
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      E        = PROPS(1)    ! Young's modulus
      NU       = PROPS(2)    ! Poisson's ratio
      SIGMA_Y  = PROPS(3)    ! Initial yield stress
      HARD_K   = PROPS(4)    ! Hardening coefficient K
      HARD_N   = PROPS(5)    ! Hardening exponent n
C
C-----------------------------------------------------------------------
C  Calculate elastic constants
C-----------------------------------------------------------------------
      G    = E / (2.0D0*(1.0D0+NU))         ! Shear modulus
      KMOD = E / (3.0D0*(1.0D0-2.0D0*NU))   ! Bulk modulus
      LAM  = KMOD - 2.0D0*G/3.0D0            ! Lame constant
C
C-----------------------------------------------------------------------
C  Read state variables
C  STATEV(1) = Equivalent plastic strain
C-----------------------------------------------------------------------
      EQPLAS = STATEV(1)
C
C-----------------------------------------------------------------------
C  Elastic predictor: calculate trial stress
C-----------------------------------------------------------------------
C  Volumetric strain increment
      TRACE = DSTRAN(1) + DSTRAN(2) + DSTRAN(3)
      P_TRIAL = (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0 + KMOD*TRACE
C
C  Deviatoric strain increment and trial deviatoric stress
      DO I = 1, NDI
        STRESS_DEV(I) = STRESS(I) - (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0
     1                + 2.0D0*G*(DSTRAN(I) - TRACE/3.0D0)
      END DO
      DO I = NDI+1, NTENS
        STRESS_DEV(I) = STRESS(I) + 2.0D0*G*DSTRAN(I)
      END DO
C
C-----------------------------------------------------------------------
C  Calculate equivalent deviatoric stress of trial stress
C-----------------------------------------------------------------------
      SMIS_TRIAL = SQRT(STRESS_DEV(1)**2 + STRESS_DEV(2)**2 
     1           + STRESS_DEV(3)**2 + 2.0D0*(STRESS_DEV(4)**2
     2           + STRESS_DEV(5)**2 + STRESS_DEV(6)**2))
C
C-----------------------------------------------------------------------
C  Calculate current yield stress
C-----------------------------------------------------------------------
      IF (EQPLAS .LE. TOLER) THEN
        YIELD_STRESS = SIGMA_Y
        HARD_MOD = 0.0D0
      ELSE
        YIELD_STRESS = SIGMA_Y + HARD_K*(EQPLAS**HARD_N)
        HARD_MOD = HARD_K*HARD_N*(EQPLAS**(HARD_N-1.0D0))
      END IF
C
C-----------------------------------------------------------------------
C  Yield check
C-----------------------------------------------------------------------
      PHI = SMIS_TRIAL - SQRT_2_3*YIELD_STRESS
C
      IF (PHI .LE. TOLER) THEN
C       Elastic step
        DEQPL = 0.0D0
        DO I = 1, NTENS
          STRESS(I) = STRESS_DEV(I)
        END DO
        DO I = 1, NDI
          STRESS(I) = STRESS(I) + P_TRIAL
        END DO
      ELSE
C       Plastic step - Radial return
C-----------------------------------------------------------------------
C  Calculate plastic multiplier increment
C-----------------------------------------------------------------------
        DEQPL = PHI / (2.0D0*G + 2.0D0*HARD_MOD/3.0D0)
        DGAMMA = 1.5D0*DEQPL
C
C-----------------------------------------------------------------------
C  Update equivalent plastic strain
C-----------------------------------------------------------------------
        EQPLAS = EQPLAS + DEQPL
        STATEV(1) = EQPLAS
C
C-----------------------------------------------------------------------
C  Update stress
C-----------------------------------------------------------------------
        FACTOR = 1.0D0 - 2.0D0*G*DGAMMA/SMIS_TRIAL
        ONEMFAC = 1.0D0 - FACTOR
C
        DO I = 1, NTENS
          STRESS(I) = FACTOR*STRESS_DEV(I)
        END DO
        DO I = 1, NDI
          STRESS(I) = STRESS(I) + P_TRIAL
        END DO
C
      END IF
C
C-----------------------------------------------------------------------
C  Calculate consistent tangent modulus (Jacobian matrix)
C-----------------------------------------------------------------------
C  Initialize
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C
      IF (PHI .LE. TOLER) THEN
C       Elastic Jacobian
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = LAM
          END DO
          DDSDDE(I,I) = LAM + 2.0D0*G
        END DO
        DO I = NDI+1, NTENS
          DDSDDE(I,I) = G
        END DO
      ELSE
C       Elastoplastic consistent tangent
        TERM1 = 2.0D0*G*FACTOR
        TERM2 = 2.0D0*G*(ONEMFAC - DGAMMA/SMIS_TRIAL)
     1        / (1.0D0 + HARD_MOD/(3.0D0*G))
C
C       Jacobian for deviatoric stress part
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = -TERM1/3.0D0 - TERM2*STRESS_DEV(I)
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)
          END DO
          DDSDDE(I,I) = DDSDDE(I,I) + TERM1
        END DO
C
C       Volumetric part
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = DDSDDE(I,J) + KMOD
          END DO
        END DO
C
C       Shear part
        DO I = NDI+1, NTENS
          DDSDDE(I,I) = TERM1/2.0D0
          DO J = NDI+1, NTENS
            DDSDDE(I,J) = DDSDDE(I,J) - TERM2*STRESS_DEV(I)
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)
          END DO
        END DO
      END IF
C
C-----------------------------------------------------------------------
C  Plastic dissipation work
C-----------------------------------------------------------------------
      SPD = YIELD_STRESS*DEQPL/DTIME
C
      RETURN
      END
```

## Abaqus Input File Example

```abaqus
*Material, name=Steel_Plastic
*User Material, constants=5
** E, NU, SIGMA_Y, K, n
210000.0, 0.3, 250.0, 500.0, 0.3
*Depvar
1
** State variables:
** 1 - Equivalent plastic strain
```

## Algorithm Verification Points

1. **Yield Surface Consistency**: Ensure stress points always lie on yield surface
2. **Energy Consistency**: Check plastic dissipation is non-negative
3. **Tangent Consistency**: Jacobian matrix should be consistent with numerical differentiation
4. **Objectivity**: Maintain stress update objectivity under large rotations

## Extension Directions

- Kinematic hardening (Armstrong-Frederick model)
- Mixed hardening (isotropic + kinematic)
- Anisotropic yield (Hill48, Barlat)
- Temperature dependence
- Strain rate effects (Johnson-Cook)

## References

- Simo & Hughes, "Computational Inelasticity", Springer
- Dunne & Petrinic, "Introduction to Computational Plasticity"
- Abaqus User Subroutines Reference Guide
