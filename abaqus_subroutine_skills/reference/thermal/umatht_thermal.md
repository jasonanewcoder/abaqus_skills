# UMATHT — Custom Thermal Material — Detailed Reference

## Skill Description

UMATHT defines the thermal constitutive behavior for a material: heat flux vs
temperature gradient (Fourier law, possibly nonlinear/anisotropic), internal energy
`U`, and the derivatives `dU/dT` and `dF_i/dG_j` needed by the Newton iteration of
the heat transfer solver. Use it when built-in `*Conductivity`/`*SpecificHeat`
cannot represent the behavior (e.g. temperature-dependent, phase-change latent heat,
orthotropic nonlinear conduction).

> 中文提示：UMATHT 用于自定义导热/内能关系；焊接、淬火、相变材料、
> 非线性导热都适合。比 HETVAL 更底层——HETVAL 只加热生成，UMATHT 控制整个热本构。

## Interface

```fortran
      SUBROUTINE UMATHT(U,DUDT,DUDG,FLUX,DFDT,DFDG,STATEV,TEMP,
     1 DTEMP,DTEMDX,TIME,DTIME,PREDEF,DPRED,CMNAME,NTGrd,NSTATV,
     2 PROPS,NPROPS,COORDS,PNEWDT,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION DUDG(NTGrd),FLUX(NTGrd),DFDT(NTGrd),
     1 DFDG(NTGrd,NTGrd),STATEV(NSTATV),DTEMDX(NTGrd),
     2 TIME(2),PREDEF(1),DPRED(1),PROPS(NPROPS),COORDS(3)
```

| Argument | Meaning |
|----------|---------|
| U | Output: internal energy per unit mass (N·mm/tonne = mJ/tonne) |
| DUDT | Output: dU/dT at constant gradient |
| DUDG(1..NTGrd) | Output: dU/dG — usually 0 |
| FLUX(1..NTGrd) | Output: heat flux components (mW/mm²) |
| DFDT(1..NTGrd) | Output: dFLUX/dT |
| DFDG(1..NTGrd,1..NTGrd) | Output: dFLUX_i/dG_j (conductivity matrix) |
| TEMP, DTEMP | Input: temperature, temperature increment |
| DTEMDX | Input: temperature gradient (K/mm) |
| NTGrd | Input: number of gradient components (3 for 3D) |
| PROPS | Input: material constants |

## Template: Nonlinear Temperature-Dependent Conductivity with Phase-Change Latent Heat

```fortran
      SUBROUTINE UMATHT(U,DUDT,DUDG,FLUX,DFDT,DFDG,STATEV,TEMP,
     1 DTEMP,DTEMDX,TIME,DTIME,PREDEF,DPRED,CMNAME,NTGrd,NSTATV,
     2 PROPS,NPROPS,COORDS,PNEWDT,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  Thermal material with:
C    - conductivity k(T) (mW/(mm·K))
C    - specific heat cp(T) (N·mm/(tonne·K))
C    - latent heat L at phase-change interval [T_S, T_L]
C  PROPS: 1=k0, 2=cp0, 3=rho (tonne/mm³), 4=T_S, 5=T_L, 6=L (N·mm/tonne)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION DUDG(NTGrd),FLUX(NTGrd),DFDT(NTGrd),
     1 DFDG(NTGrd,NTGrd),STATEV(NSTATV),DTEMDX(NTGrd),
     2 TIME(2),PREDEF(1),DPRED(1),PROPS(NPROPS),COORDS(3)
C
      REAL*8 K0, CP0, RHO, T_S, T_L, LATENT
      REAL*8 K, CP, CP_EFF, T
      INTEGER I, J
C
      K0   = PROPS(1)
      CP0  = PROPS(2)
      RHO  = PROPS(3)
      T_S  = PROPS(4)
      T_L  = PROPS(5)
      LATENT = PROPS(6)
      T    = TEMP
C
C  Temperature-dependent conductivity (linear increase with T)
      K = K0 * (1.0D0 + 0.001D0*(T - 20.0D0))
C
C  Specific heat with smeared latent heat over [T_S, T_L]
      CP = CP0
      IF (T .GE. T_S .AND. T .LE. T_L) THEN
        CP_EFF = CP + LATENT/(T_L - T_S)
      ELSE
        CP_EFF = CP
      END IF
C
C  Internal energy (per unit mass): integral of cp_eff dT
      U = CP0*(T - 20.0D0)
      IF (T .GE. T_S .AND. T .LE. T_L) THEN
        U = U + LATENT*(T - T_S)/(T_L - T_S)
      ELSE IF (T .GT. T_L) THEN
        U = U + LATENT
      END IF
      DUDT = CP_EFF
C
C  Heat flux: Fourier law with the conductivity matrix
      DO I = 1, NTGrd
        FLUX(I) = 0.0D0
        DFDT(I) = 0.0D0
        DO J = 1, NTGrd
          DFDG(I,J) = 0.0D0
        END DO
        DFDG(I,I) = K        ! diagonal conductivity (isotropic)
        FLUX(I) = -K*DTEMDX(I)
      END DO
C
      DO I = 1, NTGrd
        DUDG(I) = 0.0D0
      END DO
C
      RETURN
      END
```

> Units: `U` is energy per mass (N·mm/tonne); `FLUX` is mW/mm² = N·mm/(s·mm²).
> `CP0` must be in N·mm/(tonne·K) (= J/(kg·K) × 1e6).

## Input File Example

```abaqus
*Material, name=Steel-PhaseChange
*User Material, constants=6
** k0, cp0, rho, T_S, T_L, L
45.0, 4.6e8, 7.85e-9, 1480.0, 1520.0, 2.7e8
*Depvar
1
```

## Guidance

1. Always initialize ALL outputs (`U, DUDT, DUDG, FLUX, DFDT, DFDG`) on every call
2. `DUDT` must be positive (thermodynamic stability); negative → solver issues
3. `DFDG` is the conductivity matrix; keep it symmetric and positive definite
4. Check units of latent heat: N·mm/tonne = J/kg × 1e6 (e.g. steel ~2.7e8)

## Related

- `dflux_welding.md` — heat input via DFLUX (used together with UMATHT in welding)
- `hetval_heat.md` — heat generation without a custom thermal constitutive model
- `thermal/reference/steady_state.md`, `transient.md` — heat transfer steps
