# Abaqus UMAT Elastoplastic Material Subroutine Skill

## Skill Description

This skill guides AI to generate isotropic hardening elastoplastic UMAT subroutines based on the von Mises yield criterion using the Radial Return Mapping algorithm with a consistent tangent modulus.

## Applicable Scenarios

- Plastic deformation analysis of metal materials
- Small-strain / small-deformation problems (large rotations are handled via the Jaumann rate by Abaqus itself — this UMAT uses the rate-form stress update through `STRESS`/`DSTRAN`)
- Isotropic hardening materials (linear or power-law hardening)

## Key Features

| Feature | Description |
|---------|-------------|
| Yield Criterion | von Mises |
| Hardening Model | Isotropic hardening (linear / power law) |
| Flow Rule | Associated flow rule |
| Algorithm | Radial Return Mapping with Newton iteration (exact consistent tangent) |
| State Variables | 1 (equivalent plastic strain) |
| Material Constants | 5 (E, ν, σ₀, K, n) |

## Theoretical Formulas

### 1. Yield Function

```
f = q − σ_y(ε̄ᵖ) ≤ 0,   q = √(3/2 · s:s) = √(3/2 · s_ij s_ij)
```

where `s` is the deviatoric stress, `q` the von Mises equivalent stress, `σ_y` the current yield stress and `ε̄ᵖ` the equivalent plastic strain.

### 2. Flow Rule

```
Δεᵖ = Δλ · ∂f/∂σ = Δλ · (3/2) · s/q
Δε̄ = Δλ     (equivalent plastic strain increment)
```

### 3. Hardening Law (Power Law)

```
σ_y(ε̄ᵖ) = σ₀ + K·(ε̄ᵖ)ⁿ        H = dσ_y/dε̄ᵖ = K·n·(ε̄ᵖ)ⁿ⁻¹
```

For `n = 1` this reduces to linear hardening with slope `H = K`.

### 4. Radial Return Algorithm

```
1. Elastic predictor:  σᵗʳⁱᵃˡ = σₙ + C:Δε,   sᵗʳⁱᵃˡ = dev(σᵗʳⁱᵃˡ)
2. qᵗʳⁱᵃˡ = √(3/2 · sᵗʳⁱᵃˡ:sᵗʳⁱᵃˡ)
3. Yield check: fᵗʳⁱᵃˡ = qᵗʳⁱᵃˡ − σ_y(ε̄ₙ)
4. If fᵗʳⁱᵃˡ > 0, solve for Δε̄ (Newton iteration):
     R(Δε̄) = qᵗʳⁱᵃˡ − 3G·Δε̄ − σ_y(ε̄ₙ + Δε̄) = 0
     Δε̄ ← Δε̄ + R / (3G + H(ε̄ₙ + Δε̄))
5. Return map:  sₙ₊₁ = (σ_y(ε̄ₙ₊₁)/qᵗʳⁱᵃˡ) · sᵗʳⁱᵃˡ,   σₙ₊₁ = sₙ₊₁ + pᵗʳⁱᵃˡ·I
```

> **Note on the tangent**: For a linear hardening model, one closed-form Newton step
> `Δε̄ = (qᵗʳⁱᵃˡ − σ_y(ε̄ₙ))/(3G + H)` is exact. For nonlinear hardening the Newton
> iteration above converges in 2-4 steps. Do NOT use `(qᵗʳⁱᵃˡ−σ_y)/(2G + 2H/3)` —
> that denominator is wrong and returns the stress below the yield surface.

## Material Parameters

| Parameter | Symbol | Unit | Description |
|-----------|--------|------|-------------|
| Young's Modulus | E | MPa | Elastic modulus |
| Poisson's Ratio | ν | - | Poisson's ratio |
| Initial Yield Stress | σ₀ | MPa | Yield onset |
| Hardening Coefficient | K | MPa | Hardening curve parameter |
| Hardening Exponent | n | - | Power law hardening exponent (n=1 → linear) |

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
C  von Mises elastoplastic UMAT - radial return with Newton iteration
C  Isotropic hardening, associated flow rule, consistent tangent
C
C  PROPS(1)=E, PROPS(2)=NU, PROPS(3)=SIGMA0, PROPS(4)=K, PROPS(5)=n
C  STATEV(1) = equivalent plastic strain (varepsilon-bar^p)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
      DIMENSION FLOW(6)
      PARAMETER(ONE=1.0D0,TWO=2.0D0,THREE=3.0D0,SIX=6.0D0,
     1          TOLER=1.0D-6, NEWTON=10)
C
C-----------------------------------------------------------------------
C  Material parameters
C-----------------------------------------------------------------------
      E      = PROPS(1)    ! Young's modulus
      NU     = PROPS(2)    ! Poisson's ratio
      SIGMA0 = PROPS(3)    ! Initial yield stress
      HARDK  = PROPS(4)    ! Hardening coefficient K
      HARDN  = PROPS(5)    ! Hardening exponent n (1.0 = linear)
C
C-----------------------------------------------------------------------
C  Elastic constants (N-mm-MPa consistent)
C-----------------------------------------------------------------------
      EBULK3 = E/(ONE-TWO*NU)          ! 3 x bulk modulus
      EG2    = E/(ONE+NU)              ! 2 x shear modulus
      EG     = EG2/TWO                 ! shear modulus G
      EG3    = THREE*EG                ! 3 x shear modulus
      ELAM   = (EBULK3-EG2)/THREE      ! Lame constant
C
C-----------------------------------------------------------------------
C  Elastic predictor: STRESS = STRESS + C : DSTRAN
C-----------------------------------------------------------------------
      DO I=1,NDI
        DO J=1,NDI
          DDSDDE(J,I) = ELAM
        END DO
        DDSDDE(I,I) = EG2 + ELAM
      END DO
      DO I=NDI+1,NTENS
        DDSDDE(I,I) = EG
      END DO
      DO I=1,NTENS
        DO J=1,NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J)*DSTRAN(J)
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  Read state variables
C-----------------------------------------------------------------------
      EQPLAS = STATEV(1)
C
C-----------------------------------------------------------------------
C  von Mises stress of trial state: q = sqrt(3/2 s:s)
C-----------------------------------------------------------------------
      SMISES = (STRESS(1)-STRESS(2))*(STRESS(1)-STRESS(2))
     1       + (STRESS(2)-STRESS(3))*(STRESS(2)-STRESS(3))
     1       + (STRESS(3)-STRESS(1))*(STRESS(3)-STRESS(1))
      DO I=NDI+1,NTENS
        SMISES = SMISES + SIX*STRESS(I)*STRESS(I)
      END DO
      SMISES = SQRT(SMISES/TWO)
C
C-----------------------------------------------------------------------
C  Current yield stress and hardening modulus
C  HARDN=1 -> linear hardening, H = HARDK (constant)
C-----------------------------------------------------------------------
      IF (HARDN .LE. ONE + TOLER) THEN
        SYIELD = SIGMA0 + HARDK*EQPLAS
        HARD   = HARDK
      ELSE
        IF (EQPLAS .GT. 1.0D-12) THEN
          SYIELD = SIGMA0 + HARDK*(EQPLAS**HARDN)
          HARD   = HARDK*HARDN*(EQPLAS**(HARDN-ONE))
        ELSE
          SYIELD = SIGMA0
          HARD   = HARDK*HARDN*(1.0D-12**(HARDN-ONE))
        END IF
      END IF
C
C-----------------------------------------------------------------------
C  Yield check
C-----------------------------------------------------------------------
      IF (SMISES .GT. (ONE+TOLER)*SYIELD) THEN
C
C       Flow direction n = 3/2 * s / q  (normal part used below)
        SHYDRO = (STRESS(1)+STRESS(2)+STRESS(3))/THREE
        DO I=1,NDI
          FLOW(I) = (STRESS(I)-SHYDRO)/SMISES
        END DO
        DO I=NDI+1,NTENS
          FLOW(I) = STRESS(I)/SMISES
        END DO
C
C       Newton iteration for the equivalent plastic strain increment:
C       R(DEQPL) = SMISES - 3G*DEQPL - SYIELD(EQPLAS+DEQPL) = 0
        DEQPL = (SMISES-SYIELD)/(EG3+HARD)
        DO KNEWT=1,NEWTON
          IF (HARDN .LE. ONE + TOLER) THEN
            SYSNEW = SIGMA0 + HARDK*(EQPLAS+DEQPL)
            HSNEW  = HARDK
          ELSE
            IF (EQPLAS+DEQPL .GT. 1.0D-12) THEN
              SYSNEW = SIGMA0 + HARDK*((EQPLAS+DEQPL)**HARDN)
              HSNEW  = HARDK*HARDN*((EQPLAS+DEQPL)**(HARDN-ONE))
            ELSE
              SYSNEW = SIGMA0
              HSNEW  = HARDK*HARDN*(1.0D-12**(HARDN-ONE))
            END IF
          END IF
          RHS = SMISES - EG3*DEQPL - SYSNEW
          DEQPL = DEQPL + RHS/(EG3+HSNEW)
          IF (ABS(RHS) .LT. TOLER*SYIELD) GOTO 130
        END DO
        WRITE(*,*) 'WARNING: PLASTICITY LOOP DID NOT CONVERGE'
 130    CONTINUE
C
C       Update stress:  s_new = (sigma_y_new / q_trial) * s_trial
        DO I=1,NDI
          STRESS(I) = FLOW(I)*SYSNEW + SHYDRO
        END DO
        DO I=NDI+1,NTENS
          STRESS(I) = FLOW(I)*SYSNEW
        END DO
C
C       Update equivalent plastic strain and plastic dissipation
        EQPLAS = EQPLAS + DEQPL
        STATEV(1) = EQPLAS
        SPD = SYIELD*DEQPL
C
C       Consistent tangent modulus (J2 plasticity, see Abaqus doc example)
        EFFG   = EG*SYSNEW/SMISES
        EFFG2  = TWO*EFFG
        EFFG3  = THREE*EFFG2/(TWO*EG3)
        EFFLAM = (EBULK3-EFFG2)/THREE
        DO I=1,NDI
          DO J=1,NDI
            DDSDDE(J,I) = EFFLAM
          END DO
          DDSDDE(I,I) = EFFG2 + EFFLAM
        END DO
        DO I=NDI+1,NTENS
          DDSDDE(I,I) = EFFG
        END DO
        DO I=1,NTENS
          DO J=1,NTENS
            DDSDDE(J,I) = DDSDDE(J,I) - EFFG3*FLOW(J)*FLOW(I)
          END DO
        END DO
C
      END IF
C
      RETURN
      END
```

## Abaqus Input File Example

```abaqus
*Material, name=Steel_Plastic
*User Material, constants=5
** E, NU, SIGMA0, K, n
210000.0, 0.3, 250.0, 500.0, 0.3
*Depvar
1
** State variables:
** 1 - Equivalent plastic strain
```

## Validation: Single-Element Uniaxial Test

Verify the UMAT with a single C3D8R element under uniaxial stress (fixed format: one element, one load step, small strain):

| Quantity | Analytical | Expect from UMAT |
|----------|-----------|------------------|
| Initial yield stress | σ₀ = 250 MPa | First plasticity when σ ≈ 250 MPa |
| Elastic slope | E = 210000 MPa | ε_el at yield ≈ 250/210000 = 1.19e-3 |
| Plastic slope (n=1, K=500) | dσ/dε_p = 500 MPa | Post-yield slope ≈ E·H/(E+H) = 500.5 MPa (total strain) |
| Return consistency | stress ON yield surface | σ = σ₀ + K·ε̄ᵖ at every converged increment |

Checklist:
1. Before yield: `STRESS` = linear elastic solution, `STATEV(1)` unchanged
2. After yield: `q − σ_y(ε̄)` ≈ 0 (within solver tolerance) — stress stays on the yield surface
3. `DDSDDE` positive definite (check no negative eigenvalues in `.msg`)
4. No warnings "PLASTICITY LOOP DID NOT CONVERGE"
5. A single-element test with imposed `DSTRAN` of 0.01 should give uniaxial stress ≈ 250 + 500·(0.01−0.00119) ≈ 254.4 MPa

## Algorithm Verification Points

1. **Yield Surface Consistency**: After the return map, `q = σ_y(ε̄ₙ₊₁)` must hold — this is the standard check for a correct radial return. The old (incorrect) form `DEQPL = (qᵗʳⁱᵃˡ−σ_y)/(2G + 2H/3)` maps stress BELOW the yield surface and must not be used.
2. **Energy Consistency**: Check plastic dissipation is non-negative (`SPD ≥ 0`).
3. **Tangent Consistency**: Compare `DDSDDE` with numerical differentiation of the stress update (perturb `DSTRAN` by ±1e-6, recompute, finite-difference).
4. **Objectivity**: Maintain stress update objectivity under large rotations (Abaqus rotates `STRESS` via `DROT` before calling UMAT).
5. **Uniaxial calibration**: Run the single-element test above and compare with the analytical stress-strain curve.

## Extension Directions

- Kinematic hardening (Armstrong-Frederick model)
- Mixed hardening (isotropic + kinematic)
- Anisotropic yield (Hill48, Barlat)
- Temperature dependence (pass `TEMP`/`DTEMP`, add thermo term to `DDSDDT`)
- Strain rate effects (Johnson-Cook) — requires the explicit rate form, better suited to VUMAT
- Large-deformation implementation via `DFGRD0`/`DFGRD1` (hypoelastic, unrotated configuration)

## References

- Abaqus User Subroutines Reference Guide — UMAT, incl. the official von Mises plasticity example (`official_examples/umat/umat_mises_plasticity_official.f` in this repository)
- Simo & Hughes, "Computational Inelasticity", Springer
- Dunne & Petrinic, "Introduction to Computational Plasticity"
- The consistent tangent for J₂ plasticity: `EFFG = EG·σ_y/q` formulation (see Abaqus doc example)
