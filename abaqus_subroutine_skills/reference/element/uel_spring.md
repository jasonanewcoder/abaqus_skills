# Abaqus UEL Custom Element Subroutine Skill

## Skill Description

This skill guides AI to generate custom element subroutines UEL for Abaqus, implementing special element types such as nonlinear springs, dampers, zero-thickness contact elements, etc.

## Applicable Scenarios

- Nonlinear spring elements
- Custom dampers
- Zero-thickness bond elements
- Special connection elements
- Multi-point displacement constraint elements

## Key Features

| Feature | Description |
|---------|-------------|
| DOFs | Can define arbitrary DOF combinations |
| Geometry | Arbitrary number of nodes, arbitrary dimensions |
| Constitutive | Fully custom force-displacement relationship |
| Output | Custom element output variables |

## UEL Interface Definition

```fortran
SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
```

## Key Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| RHS(NDOFEL,NRHS) | Output | Residual force vector |
| AMATRX(NDOFEL,NDOFEL) | Output | Element stiffness matrix |
| SVARS(NSVARS) | Input/Output | Element state variables |
| U(NDOFEL) | Input | Node total displacements |
| DU(NDOFEL) | Input | Node displacement increments |
| COORDS | Input | Node coordinates |

## Element Types

### 1. Nonlinear Spring Element (2-Node)

```fortran
      SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
C
C  Nonlinear spring element UEL
C  2 nodes, each with 3 translational DOFs
C  Force-displacement relationship: F = k1*u + k2*u^3 (hardening type nonlinearity)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION RHS(NDOFEL,NRHS), AMATRX(NDOFEL,NDOFEL),
     1 SVARS(NSVARS), ENERGY(8), PROPS(NPROPS),
     2 COORDS(MCRD,NNODE), U(NDOFEL), DU(NDOFEL),
     3 V(NDOFEL), A(NDOFEL), TIME(2), PARAMS(3),
     4 JDLTYP(MDLOAD,*), ADLMAG(MDLOAD,*), DDLMAG(MDLOAD,*),
     5 PREDEF(2,NPREDF,NNODE), LFLAGS(*), JPROPS(*)
C
      REAL*8 K1, K2, F_MAX, U_SEP
      REAL*8 X1, Y1, Z1, X2, Y2, Z2
      REAL*8 DX, DY, DZ, L0, L, STRAIN
      REAL*8 FORCE, STIFFNESS
      REAL*8 DIR_COS(3), DISP_REL(3)
      INTEGER I, J, DOF_MAP(6)
C
C-----------------------------------------------------------------------
C  Define DOF mapping
C  Node 1: DOF 1-3 (Ux, Uy, Uz)
C  Node 2: DOF 4-6 (Ux, Uy, Uz)
C-----------------------------------------------------------------------
      DATA DOF_MAP /1, 2, 3, 4, 5, 6/
C
C-----------------------------------------------------------------------
C  Read material parameters
C-----------------------------------------------------------------------
      K1    = PROPS(1)     ! Linear stiffness (N/m)
      K2    = PROPS(2)     ! Nonlinear stiffness coefficient (N/m³)
      F_MAX = PROPS(3)     ! Maximum bearing force (N)
      U_SEP = PROPS(4)     ! Separation displacement (m)
C
C-----------------------------------------------------------------------
C  Calculate initial spring length
C-----------------------------------------------------------------------
      X1 = COORDS(1,1)
      Y1 = COORDS(2,1)
      Z1 = COORDS(3,1)
      X2 = COORDS(1,2)
      Y2 = COORDS(2,2)
      Z2 = COORDS(3,2)
      
      L0 = SQRT((X2-X1)**2 + (Y2-Y1)**2 + (Z2-Z1)**2)
C
C-----------------------------------------------------------------------
C  Calculate current length and direction cosines
C-----------------------------------------------------------------------
C  Node displacements
      DX = (X2 + U(4)) - (X1 + U(1))
      DY = (Y2 + U(5)) - (Y1 + U(2))
      DZ = (Z2 + U(6)) - (Z1 + U(3))
      
      L = SQRT(DX*DX + DY*DY + DZ*DZ)
C
C  Direction cosines
      IF (L .GT. 1.0D-12) THEN
        DIR_COS(1) = DX / L
        DIR_COS(2) = DY / L
        DIR_COS(3) = DZ / L
      ELSE
        DIR_COS(1) = 0.0D0
        DIR_COS(2) = 0.0D0
        DIR_COS(3) = 0.0D0
      END IF
C
C-----------------------------------------------------------------------
C  Calculate relative displacement (along spring direction)
C-----------------------------------------------------------------------
      DISP_REL(1) = U(4) - U(1)
      DISP_REL(2) = U(5) - U(2)
      DISP_REL(3) = U(6) - U(3)
      
      STRAIN = L - L0    ! Spring deformation (positive for elongation)
C
C-----------------------------------------------------------------------
C  Nonlinear constitutive relationship
C  F = k1*u + k2*u^3  (when |F| < F_MAX)
C  F = 0               (when |u| > u_sep, separation)
C-----------------------------------------------------------------------
      IF (ABS(STRAIN) .GT. U_SEP) THEN
C       Separation
        FORCE = 0.0D0
        STIFFNESS = 0.0D0
      ELSE
C       Nonlinear elastic
        FORCE = K1*STRAIN + K2*STRAIN**3
        
C       Limit maximum force
        IF (ABS(FORCE) .GT. F_MAX) THEN
          FORCE = SIGN(F_MAX, FORCE)
          STIFFNESS = 0.0D0    ! Perfectly plastic
        ELSE
          STIFFNESS = K1 + 3.0D0*K2*STRAIN**2
        END IF
      END IF
C
C-----------------------------------------------------------------------
C  Assemble residual vector (internal forces)
C-----------------------------------------------------------------------
      DO I = 1, 3
C       Force on node 1 (negative direction)
        RHS(I,1) = -FORCE * DIR_COS(I)
C       Force on node 2 (positive direction)
        RHS(I+3,1) = FORCE * DIR_COS(I)
      END DO
C
C-----------------------------------------------------------------------
C  Assemble stiffness matrix
C-----------------------------------------------------------------------
C  Initialize
      DO I = 1, NDOFEL
        DO J = 1, NDOFEL
          AMATRX(I,J) = 0.0D0
        END DO
      END DO
C
C  Geometric stiffness + material stiffness
      DO I = 1, 3
        DO J = 1, 3
C         Diagonal terms
          AMATRX(I,I) = AMATRX(I,I) + STIFFNESS * DIR_COS(I)**2
          AMATRX(I+3,I+3) = AMATRX(I+3,I+3) + STIFFNESS * DIR_COS(I)**2
C         Coupling terms
          AMATRX(I,I+3) = -STIFFNESS * DIR_COS(I)**2
          AMATRX(I+3,I) = -STIFFNESS * DIR_COS(I)**2
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  Store state variables
C-----------------------------------------------------------------------
      SVARS(1) = STRAIN      ! Spring strain
      SVARS(2) = FORCE       ! Spring force
      SVARS(3) = L           ! Current length
C
C-----------------------------------------------------------------------
C  Energy calculation (optional)
C-----------------------------------------------------------------------
      ENERGY(1) = 0.5D0*K1*STRAIN**2 + 0.25D0*K2*STRAIN**4  ! Elastic strain energy
C
      RETURN
      END
```

### 2. Damper Element

```fortran
      SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
C
C  Viscous damper element
C  Force proportional to relative velocity
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION RHS(NDOFEL,NRHS), AMATRX(NDOFEL,NDOFEL),
     1 SVARS(NSVARS), ENERGY(8), PROPS(NPROPS),
     2 COORDS(MCRD,NNODE), U(NDOFEL), DU(NDOFEL),
     3 V(NDOFEL), A(NDOFEL), TIME(2), PARAMS(3),
     4 JDLTYP(MDLOAD,*), ADLMAG(MDLOAD,*), DDLMAG(MDLOAD,*),
     5 PREDEF(2,NPREDF,NNODE), LFLAGS(*), JPROPS(*)
C
      REAL*8 C_DAMP
      REAL*8 DIR_COS(3), V_REL(3), V_NORM, FORCE
      INTEGER I
C
C-----------------------------------------------------------------------
C  Read damping coefficient
C-----------------------------------------------------------------------
      C_DAMP = PROPS(1)      ! Damping coefficient (N·s/m)
C
C-----------------------------------------------------------------------
C  Calculate direction cosines (assume initial direction)
C-----------------------------------------------------------------------
      X1 = COORDS(1,1)
      Y1 = COORDS(2,1)
      Z1 = COORDS(3,1)
      X2 = COORDS(1,2)
      Y2 = COORDS(2,2)
      Z2 = COORDS(3,2)
      
      L0 = SQRT((X2-X1)**2 + (Y2-Y1)**2 + (Z2-Z1)**2)
      DIR_COS(1) = (X2-X1) / L0
      DIR_COS(2) = (Y2-Y1) / L0
      DIR_COS(3) = (Z2-Z1) / L0
C
C-----------------------------------------------------------------------
C  Calculate relative velocity
C-----------------------------------------------------------------------
      V_REL(1) = V(4) - V(1)
      V_REL(2) = V(5) - V(2)
      V_REL(3) = V(6) - V(3)
C
C  Relative velocity component in spring direction
      V_NORM = V_REL(1)*DIR_COS(1) + V_REL(2)*DIR_COS(2) 
     1       + V_REL(3)*DIR_COS(3)
C
C-----------------------------------------------------------------------
C  Damping force
C-----------------------------------------------------------------------
      FORCE = C_DAMP * V_NORM
C
C-----------------------------------------------------------------------
C  Assemble residual
C-----------------------------------------------------------------------
      DO I = 1, 3
        RHS(I,1) = -FORCE * DIR_COS(I)
        RHS(I+3,1) = FORCE * DIR_COS(I)
      END DO
C
C-----------------------------------------------------------------------
C  Damping stiffness matrix (for implicit analysis)
C-----------------------------------------------------------------------
      DO I = 1, NDOFEL
        DO J = 1, NDOFEL
          AMATRX(I,J) = 0.0D0
        END DO
      END DO
C
C  Damping contribution (multiply by appropriate integration factor)
      DO I = 1, 3
        AMATRX(I,I) = C_DAMP * DIR_COS(I)**2
        AMATRX(I+3,I+3) = C_DAMP * DIR_COS(I)**2
        AMATRX(I,I+3) = -C_DAMP * DIR_COS(I)**2
        AMATRX(I+3,I) = -C_DAMP * DIR_COS(I)**2
      END DO
C
C-----------------------------------------------------------------------
C  Dissipated energy
C-----------------------------------------------------------------------
      ENERGY(2) = FORCE * V_NORM * DTIME    ! Dissipated energy
C
      RETURN
      END
```

## Input File Example

```abaqus
** User defined element
*User element, type=U1, nodes=2, coordinates=3, properties=4, 
1 variables=3
1, 2, 3
*Element, type=U1, elset=Spring_Elements
1, 1, 2
2, 3, 4
**
*UEL property, elset=Spring_Elements
** k1, k2, F_max, u_sep
1000.0, 10000.0, 500.0, 0.5
```

## Explicit Custom Element (VUEL)

Explicit analysis uses VUEL with similar interface but processes block data.

## References

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 32.15
