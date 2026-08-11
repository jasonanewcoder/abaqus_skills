# Abaqus VUMAT Linear Elastic Material Subroutine Skill

## Skill Description

This skill guides AI to generate linear elastic material VUMAT subroutines for Abaqus Explicit analysis. Explicit analysis has special stability requirements.

## Applicable Scenarios

- Impact dynamics analysis
- High-speed collision simulation
- Transient dynamics problems
- Large deformation analysis

## Key Features

| Feature | Description |
|---------|-------------|
| Analysis Type | Explicit Dynamics |
| Material Model | Linear Elastic, Isotropic |
| Stress Update | Based on deformation gradient |
| Large Deformation | Supported (based on Jaumann rate or Green-Naghdi rate) |

## Key Differences Between VUMAT and UMAT

| Feature | UMAT (Standard) | VUMAT (Explicit) |
|---------|-----------------|------------------|
| Time Integration | Implicit | Explicit |
| Jacobian Matrix | Required | Not required |
| Deformation Gradient | Provided | Provided |
| Stress Update | Incremental form | Based on deformation gradient |
| Stability | Unconditional (implicit convergence) | Conditional (CFL condition) |

## VUMAT Interface Definition

```fortran
subroutine vumat(
     1 nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2 stepTime, totalTime, dt, cmname, coordMp, charLength,
     3 props, density, strainInc, relSpinInc,
     4 tempOld, stretchOld, defgradOld, fieldOld,
     5 stressOld, stateOld, enerInternOld, enerInelasOld,
     6 tempNew, stretchNew, defgradNew, fieldNew,
     7 stressNew, stateNew, enerInternNew, enerInelasNew)
```

## Key Parameter Descriptions

| Parameter | Description |
|-----------|-------------|
| nblock | Number of element points in block |
| ndir | Number of direct stress/strain components |
| nshr | Number of shear stress/strain components |
| defgradOld/New | Deformation gradient at increment start/end |
| strainInc | Strain increment |
| stressOld/New | Stress at increment start/end |
| relSpinInc | Relative spin increment |

## Theoretical Formulas

### Stress Update Based on Jaumann Rate

```
σᵗʳᵒᵗ = σₙ + W·σₙ − σₙ·W        (rotation part; W built from relSpinInc)
σₙ₊₁ = σᵗʳᵒᵗ + C : Δε             (elastic increment)
```

Where:
- Δε is the strain increment tensor
- W is the spin (incremental rotation) — the sign convention in the code
  below matches the official Abaqus example, do NOT invert it
- Abaqus/Explicit stores the deviatoric stress in `stressOld`/`stressNew`;
  the hydrostatic pressure is handled by the element, so VUMAT must add
  `trace/3` before rotating the stress (see code below)

## Fortran Code

```fortran
      subroutine vumat(
     1 nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2 stepTime, totalTime, dt, cmname, coordMp, charLength,
     3 props, density, strainInc, relSpinInc,
     4 tempOld, stretchOld, defgradOld, fieldOld,
     5 stressOld, stateOld, enerInternOld, enerInelasOld,
     6 tempNew, stretchNew, defgradNew, fieldNew,
     7 stressNew, stateNew, enerInternNew, enerInelasNew)
C
C  Explicit dynamics linear elastic VUMAT
C  Jaumann rate based stress update
C
      include 'vaba_param.inc'
C
      dimension props(nprops), density(nblock), coordMp(nblock,*),
     1 charLength(nblock), strainInc(nblock,ndir+nshr),
     2 relSpinInc(nblock,nshr), tempOld(nblock),
     3 stretchOld(nblock,ndir+nshr),
     4 defgradOld(nblock,ndir+nshr+nshr),
     5 fieldOld(nblock,nfieldv), stressOld(nblock,ndir+nshr),
     6 stateOld(nblock,nstatev), enerInternOld(nblock),
     7 enerInelasOld(nblock), tempNew(nblock),
     8 stretchNew(nblock,ndir+nshr),
     9 defgradNew(nblock,ndir+nshr+nshr),
     1 fieldNew(nblock,nfieldv),
     2 stressNew(nblock,ndir+nshr), stateNew(nblock,nstatev),
     3 enerInternNew(nblock), enerInelasNew(nblock)
C
      character*80 cmname
C
      parameter(one = 1.0d0, two = 2.0d0, half = 0.5d0,
     1          three = 3.0d0)
C
C  Local variables
      real*8 e, xnu, alamda, amu, trace, traceStrainInc
      real*8 sigOld1, sigOld2, sigOld3, sigOld4, sigOld5, sigOld6
      real*8 sigNew1, sigNew2, sigNew3, sigNew4, sigNew5, sigNew6
      integer i
C
C-----------------------------------------------------------------------
C  Material parameters
C-----------------------------------------------------------------------
      e    = props(1)    ! Young's modulus
      xnu  = props(2)    ! Poisson's ratio
C
C  Lame constants
      alamda = xnu*e / ((one+xnu)*(one-two*xnu))
      amu    = half*e / (one+xnu)
C
C-----------------------------------------------------------------------
C  Update stresses using Jaumann rate
C  NOTE: Abaqus/Explicit passes the DEVIATORIC stress to VUMAT; the
C  hydrostatic pressure is handled by the element formulation. The
C  trace/3 correction below recovers the total stress, exactly as in
C  the official Abaqus example (official_examples/vumat/).
C-----------------------------------------------------------------------
      do 100 i = 1, nblock
C
C       Recover total stress from stored deviatoric stress
        trace = stressOld(i,1) + stressOld(i,2) + stressOld(i,3)
        sigOld1 = stressOld(i,1) + trace/three
        sigOld2 = stressOld(i,2) + trace/three
        sigOld3 = stressOld(i,3) + trace/three
        sigOld4 = stressOld(i,4)
        sigOld5 = stressOld(i,5)
        sigOld6 = stressOld(i,6)
C
C       Apply rotation (Jaumann rate) - sign convention follows the
C       official Abaqus example exactly.
C       NOTE: component indices assume ndir=3 (3D, plane strain,
C       axisymmetric). For plane stress (ndir=2, nshr=1) the shear
C       component is stored at index 3 instead of 4.
        if (nshr .eq. 1) then
          sigNew1 = sigOld1 - sigOld4*relSpinInc(i,1)*two
          sigNew2 = sigOld2 + sigOld4*relSpinInc(i,1)*two
          sigNew3 = sigOld3
          sigNew4 = sigOld4 + (sigOld1-sigOld2)*relSpinInc(i,1)
        else
          sigNew1 = sigOld1 - sigOld4*relSpinInc(i,1)*two
     1                  + sigOld5*relSpinInc(i,2)*two
          sigNew2 = sigOld2 + sigOld4*relSpinInc(i,1)*two
     1                  - sigOld6*relSpinInc(i,3)*two
          sigNew3 = sigOld3 - sigOld5*relSpinInc(i,2)*two
     1                  + sigOld6*relSpinInc(i,3)*two
          sigNew4 = sigOld4 + (sigOld1-sigOld2)*relSpinInc(i,1)
     1                  - sigOld6*relSpinInc(i,2)
     2                  - sigOld5*relSpinInc(i,3)
          sigNew5 = sigOld5 + sigOld4*relSpinInc(i,2)
     1                  + (sigOld1-sigOld3)*relSpinInc(i,2)
     2                  - sigOld6*relSpinInc(i,1)
          sigNew6 = sigOld6 + sigOld4*relSpinInc(i,3)
     1                  + (sigOld2-sigOld3)*relSpinInc(i,3)
     2                  + sigOld5*relSpinInc(i,1)
        end if
C
C       Elastic stress increment from strain increment
        traceStrainInc = strainInc(i,1) + strainInc(i,2)
     1                 + strainInc(i,3)
        sigNew1 = sigNew1 + alamda*traceStrainInc
     1                    + two*amu*strainInc(i,1)
        sigNew2 = sigNew2 + alamda*traceStrainInc
     1                    + two*amu*strainInc(i,2)
        sigNew3 = sigNew3 + alamda*traceStrainInc
     1                    + two*amu*strainInc(i,3)
        sigNew4 = sigNew4 + amu*strainInc(i,4)
        if (nshr .gt. 1) then
          sigNew5 = sigNew5 + amu*strainInc(i,5)
          sigNew6 = sigNew6 + amu*strainInc(i,6)
        end if
C
C       Store new stress
        stressNew(i,1) = sigNew1
        stressNew(i,2) = sigNew2
        stressNew(i,3) = sigNew3
        stressNew(i,4) = sigNew4
        if (nshr .gt. 1) then
          stressNew(i,5) = sigNew5
          stressNew(i,6) = sigNew6
        end if
C
C       Update internal energy
        enerInternNew(i) = enerInternOld(i)
     1    + half * (
     2      (stressOld(i,1)+stressNew(i,1))*strainInc(i,1) +
     3      (stressOld(i,2)+stressNew(i,2))*strainInc(i,2) +
     4      (stressOld(i,3)+stressNew(i,3))*strainInc(i,3) +
     5      (stressOld(i,4)+stressNew(i,4))*strainInc(i,4) +
     6      (stressOld(i,5)+stressNew(i,5))*strainInc(i,5) +
     7      (stressOld(i,6)+stressNew(i,6))*strainInc(i,6) ) / density(i)
C
 100  continue
C
      return
      end
```

## Abaqus Input File Example

```abaqus
*Material, name=Elastic_VUMAT
*Density
7.85e-9
*User Material, constants=2
** E (MPa), NU
210000.0, 0.3
```

> Units follow the project standard (N-mm-MPa): density in tonne/mm³,
> modulus in MPa. Do NOT use kg/m³ (7850.0) or Pa (210e9) here.

## Explicit Analysis Considerations

1. **Time Step Limit**: Must satisfy CFL condition
2. **Hourglass Control**: First-order reduced integration elements require hourglass control
3. **Energy Balance**: Monitor total energy (internal + kinetic + dissipated)
4. **Contact Settings**: Explicit analysis contact algorithm differs from implicit

## Stability Check

```fortran
C  Calculate P-wave speed (for explicit stability check)
      waveSpeed = sqrt((alamda + two*amu)/density(i))
      stableDt  = charLength(i)/waveSpeed
```

## Extension Directions

- Johnson-Cook constitutive (strain rate, temperature effects)
- Damage evolution (failure model)
- Equation of state (high-pressure physics)

## References

- Abaqus User Subroutines Reference Guide
- Belytschko et al., "Nonlinear Finite Elements for Continua and Structures"
