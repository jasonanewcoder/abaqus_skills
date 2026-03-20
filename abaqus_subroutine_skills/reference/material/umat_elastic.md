# Abaqus UMAT Linear Elastic Material Subroutine Skill

## Skill Description

This skill guides AI to generate linear elastic material UMAT subroutines for Abaqus Standard implicit analysis. This is the simplest UMAT implementation, suitable as an introductory example.

## Applicable Scenarios

- Isotropic linear elastic materials
- Verifying UMAT interface and compilation
- As a base template for more complex material models

## Key Features

| Feature | Description |
|---------|-------------|
| Analysis Type | Implicit Static/Dynamic (Standard) |
| Material Model | Linear Elastic, Isotropic |
| Input Parameters | Young's Modulus E, Poisson's Ratio ν |
| State Variables | None |
| Stress Update | Direct calculation, unconditionally stable |

## Theoretical Formulas

### Constitutive Relationship (3D)

```
σ = D : ε
```

Where elastic matrix D (isotropic material):

```
D = E/((1+ν)(1-2ν)) ×
    [1-ν   ν     ν     0        0        0    ]
    [ν     1-ν   ν     0        0        0    ]
    [ν     ν     1-ν   0        0        0    ]
    [0     0     0     (1-2ν)/2 0        0    ]
    [0     0     0     0        (1-2ν)/2 0    ]
    [0     0     0     0        0        (1-2ν)/2]
```

## UMAT Interface Definition

```fortran
SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| STRESS(NTENS) | Input/Output | Stress tensor (Voigt notation) |
| STATEV(NSTATV) | Input/Output | State variable array |
| DDSDDE(NTENS,NTENS) | Output | Material Jacobian matrix ∂Δσ/∂Δε |
| STRAN(NTENS) | Input | Total strain (at start of increment) |
| DSTRAN(NTENS) | Input | Strain increment |
| PROPS(NPROPS) | Input | Material parameter array |
| NTENS | Input | Number of stress/strain components (=NDI+NSHR) |

## Fortran Code Template

```fortran
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C
C  Linear Elastic Material UMAT Subroutine
C  Isotropic linear elastic, for Abaqus/Standard
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
C  PROPS(1) = Young's modulus E
C  PROPS(2) = Poisson's ratio NU
      REAL*8 E, NU, EG, EG2, ELAM, FAC
      INTEGER I, J
C
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      E    = PROPS(1)    ! Young's modulus
      NU   = PROPS(2)    ! Poisson's ratio
C
C-----------------------------------------------------------------------
C  Calculate elastic constants
C-----------------------------------------------------------------------
      EG2  = E / (1.0D0 + NU)        ! 2*G
      EG   = EG2 / 2.0D0              ! G
      ELAM = E * NU / ((1.0D0 + NU) * (1.0D0 - 2.0D0*NU))  ! Lame constant
C
C-----------------------------------------------------------------------
C  Initialize Jacobian matrix
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  Assemble Jacobian matrix (3D/Plane Strain/Axisymmetric)
C-----------------------------------------------------------------------
      IF (NDI .EQ. 3) THEN
C       3D or plane strain case
        FAC = ELAM + EG2
        DDSDDE(1,1) = FAC
        DDSDDE(2,2) = FAC
        DDSDDE(3,3) = FAC
        DDSDDE(1,2) = ELAM
        DDSDDE(1,3) = ELAM
        DDSDDE(2,1) = ELAM
        DDSDDE(2,3) = ELAM
        DDSDDE(3,1) = ELAM
        DDSDDE(3,2) = ELAM
        DDSDDE(4,4) = EG
        IF (NSHR .GE. 2) THEN
          DDSDDE(5,5) = EG
          DDSDDE(6,6) = EG
        END IF
      ELSE IF (NDI .EQ. 2) THEN
C       Plane stress case
        FAC = E / (1.0D0 - NU*NU)
        DDSDDE(1,1) = FAC
        DDSDDE(2,2) = FAC
        DDSDDE(1,2) = FAC * NU
        DDSDDE(2,1) = FAC * NU
        DDSDDE(3,3) = FAC * (1.0D0 - NU) / 2.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Stress update: σ_new = σ_old + D : Δε
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J) * DSTRAN(J)
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  Calculate strain energy (optional)
C-----------------------------------------------------------------------
      SSE = 0.0D0
      DO I = 1, NTENS
        SSE = SSE + STRESS(I) * (STRAN(I) + 0.5D0*DSTRAN(I))
      END DO
      SSE = SSE / 2.0D0
C
      RETURN
      END
```

## Abaqus Input File Example

```abaqus
** Material definition
*Material, name=Elastic_UMAT
*User Material, constants=2
** E, NU
210000.0, 0.3
```

## Verification Methods

1. **Simple Tension Test**: Compare stress-strain curve with Abaqus built-in elastic material
2. **Single Element Test**: Check stress update correctness
3. **Symmetry Test**: Verify Jacobian matrix symmetry

## Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Compilation error | Fortran syntax error | Check fixed format (column 6 continuation) |
| Abnormal results | Incorrect Jacobian matrix | Verify DDSDDE symmetry and values |
| Convergence difficulty | Inconsistent Jacobian | Ensure DDSDDE = ∂Δσ/∂Δε |

## Extension Suggestions

This template can be extended to:
- Anisotropic elasticity (orthotropic, transversely isotropic)
- Temperature-dependent elastic modulus
- Nonlinear elasticity (hyperelasticity)

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26.7
