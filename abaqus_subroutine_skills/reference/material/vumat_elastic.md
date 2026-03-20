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
| Stability | Unconditional (convergence前提) | Conditional (CFL condition) |

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
σ^∇ = C : D
σ_{n+1} = σ_n + Δt * σ^∇ + Ω·σ_n - σ_n·Ω
```

Where:
- D is deformation rate tensor (strain increment/Δt)
- Ω is spin tensor
- σ^∇ is Jaumann rate

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
C  Local variables
      integer i, j, k, nDirDim, nShem, nblock
      real*8 E, nu, lambda, twoMu, mu, bulkMod
      real*8 traceEps, stressRate(6), spin(3,3)
      real*8 stressRot(3,3), stressTemp(3,3)
      real*8 F(3,3), detF, J, FInv(3,3)
      real*8 C(6,6)
C
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      E        = props(1)    ! Young's modulus
      nu       = props(2)    ! Poisson's ratio
C
C-----------------------------------------------------------------------
C  Calculate elastic constants
C-----------------------------------------------------------------------
      mu       = E / (2.0D0*(1.0D0+nu))      ! Shear modulus
      twoMu    = 2.0D0*mu
      lambda   = E*nu / ((1.0D0+nu)*(1.0D0-2.0D0*nu))
      bulkMod  = lambda + twoMu/3.0D0
C
C-----------------------------------------------------------------------
C  Assemble elasticity matrix C (6x6)
C-----------------------------------------------------------------------
      do i = 1, 6
        do j = 1, 6
          C(i,j) = 0.0D0
        end do
      end do
C
      do i = 1, ndir
        do j = 1, ndir
          C(i,j) = lambda
        end do
        C(i,i) = lambda + twoMu
      end do
      do i = ndir+1, ndir+nshr
        C(i,i) = mu
      end do
C
C-----------------------------------------------------------------------
C  Loop over each integration point
C-----------------------------------------------------------------------
      do k = 1, nblock
C
C       Calculate stress rate
        do i = 1, ndir+nshr
          stressRate(i) = 0.0D0
          do j = 1, ndir+nshr
            stressRate(i) = stressRate(i) + C(i,j)*strainInc(k,j)
          end do
        end do
C
C       Stress rotation (Jaumann rate)
C       Build spin tensor
        if (nshr .eq. 1) then
          spin(1,2) = relSpinInc(k,1)
          spin(2,1) = -relSpinInc(k,1)
        else if (nshr .eq. 3) then
          spin(1,2) = relSpinInc(k,1)
          spin(1,3) = relSpinInc(k,2)
          spin(2,3) = relSpinInc(k,3)
          spin(2,1) = -relSpinInc(k,1)
          spin(3,1) = -relSpinInc(k,2)
          spin(3,2) = -relSpinInc(k,3)
        end if
        spin(1,1) = 0.0D0
        spin(2,2) = 0.0D0
        spin(3,3) = 0.0D0
C
C       Convert old stress to 3x3 matrix
        stressTemp(1,1) = stressOld(k,1)
        stressTemp(2,2) = stressOld(k,2)
        stressTemp(3,3) = stressOld(k,3)
        if (nshr .eq. 1) then
          stressTemp(1,2) = stressOld(k,4)
          stressTemp(2,1) = stressOld(k,4)
          stressTemp(1,3) = 0.0D0
          stressTemp(3,1) = 0.0D0
          stressTemp(2,3) = 0.0D0
          stressTemp(3,2) = 0.0D0
        else
          stressTemp(1,2) = stressOld(k,4)
          stressTemp(2,1) = stressOld(k,4)
          stressTemp(1,3) = stressOld(k,5)
          stressTemp(3,1) = stressOld(k,5)
          stressTemp(2,3) = stressOld(k,6)
          stressTemp(3,2) = stressOld(k,6)
        end if
C
C       Calculate rotated stress
        do i = 1, 3
          do j = 1, 3
            stressRot(i,j) = stressTemp(i,j)
            do i1 = 1, 3
              stressRot(i,j) = stressRot(i,j) 
     1                       + spin(i,i1)*stressTemp(i1,j)
     2                       - stressTemp(i,i1)*spin(i1,j)
            end do
          end do
        end do
C
C       Update stress
        stressNew(k,1) = stressRot(1,1) + stressRate(1)
        stressNew(k,2) = stressRot(2,2) + stressRate(2)
        stressNew(k,3) = stressRot(3,3) + stressRate(3)
        if (nshr .ge. 1) then
          stressNew(k,4) = stressRot(1,2) + stressRate(4)
        end if
        if (nshr .ge. 2) then
          stressNew(k,5) = stressRot(1,3) + stressRate(5)
          stressNew(k,6) = stressRot(2,3) + stressRate(6)
        end if
C
C       Update internal energy
        enerInternNew(k) = enerInternOld(k)
        do i = 1, ndir+nshr
          enerInternNew(k) = enerInternNew(k) 
     1                     + 0.5D0*(stressOld(k,i)+stressNew(k,i))
     2                     *strainInc(k,i)/density(k)
        end do
C
C       State variable update (if any)
        do i = 1, nstatev
          stateNew(k,i) = stateOld(k,i)
        end do
C
      end do  ! end k loop
C
      return
      end
```

## Abaqus Input File Example

```abaqus
*Material, name=Elastic_VUMAT
*Density
7850.0
*User Material, constants=2
** E, NU
210.e9, 0.3
```

## Explicit Analysis Considerations

1. **Time Step Limit**: Must satisfy CFL condition
2. **Hourglass Control**: First-order reduced integration elements require hourglass control
3. **Energy Balance**: Monitor total energy (internal + kinetic + dissipated)
4. **Contact Settings**: Explicit analysis contact algorithm differs from implicit

## Stability Check

```fortran
C  Calculate wave speed (for stability check)
waveSpeed = sqrt((bulkMod + 4.0D0*mu/3.0D0)/density(k))
stableDt = charLength(k)/waveSpeed
```

## Extension Directions

- Johnson-Cook constitutive (strain rate, temperature effects)
- Damage evolution (failure model)
- Equation of state (high-pressure physics)

## References

- Abaqus User Subroutines Reference Guide
- Belytschko et al., "Nonlinear Finite Elements for Continua and Structures"
