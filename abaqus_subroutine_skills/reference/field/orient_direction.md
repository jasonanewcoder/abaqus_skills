# ORIENT — Custom Material Orientation — Detailed Reference

## Skill Description

ORIENT defines the **material orientation** (local coordinate system) at each integration
point for anisotropic materials (composites, crystals, wood, AM parts) where the
orientation varies spatially or follows the deformation.

> 中文提示：复合材料/各向异性材料需要在积分点定义材料方向。ORIENT 常用于
> 变角度铺层(VAT)、缠绕结构、大变形下方向随纤维转动的场景。

## Interface

```fortran
      SUBROUTINE ORIENT(COORDS,NNODE,NODE,NOEL,JMATYP,LAYER,KSPT,
     1 SHELLS,COORDSS)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*8 JMATYP(2)
      DIMENSION COORDS(3,*),NODE(*),COORDSS(3,*)
      REAL*8 T(3,3)
      REAL*8 ROT(3,3)
```

| Argument | Meaning |
|----------|---------|
| COORDS | Input: node coordinates of the element (current config.) |
| NNODE, NODE | Input: number / labels of nodes |
| JMATYP | Input: material type keyword ('SOLID', 'SHELL', ...) |
| LAYER, KSPT | Input: layer / section point number |
| SHELLS | Output: 1 → COORDSS holds the shell section directions |
| COORDSS | Output: two vectors for shell section local 1-2 directions |
| T | Output: **transformation matrix** (global → material) |
| ROT | Output: rotation matrix for state variables (usually = T) |

## Template 1: Radial–Tangential Orientation (cylinder / axisymmetric-like)

```fortran
      SUBROUTINE ORIENT(COORDS,NNODE,NODE,NOEL,JMATYP,LAYER,KSPT,
     1 SHELLS,COORDSS)
C
C  Material 1-axis = radial, 2-axis = circumferential, 3-axis = Z
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*8 JMATYP(2)
      DIMENSION COORDS(3,*),NODE(*),COORDSS(3,*)
      DIMENSION T(3,3), ROT(3,3)
      REAL*8 XC, YC, R
      INTEGER I, J
C
      XC = 0.0D0
      YC = 0.0D0
      DO I = 1, NNODE
        XC = XC + COORDS(1,I)
        YC = YC + COORDS(2,I)
      END DO
      XC = XC/NNODE
      YC = YC/NNODE
C
      R = SQRT(XC*XC + YC*YC)
      IF (R .LT. 1.0D-12) R = 1.0D-12
C
C  T rows = local axes in global coordinates (orthonormal, det=+1)
      T(1,1) =  XC/R          ! radial
      T(1,2) =  YC/R
      T(1,3) =  0.0D0
      T(2,1) = -YC/R          ! circumferential
      T(2,2) =  XC/R
      T(2,3) =  0.0D0
      T(3,1) =  0.0D0         ! axial
      T(3,2) =  0.0D0
      T(3,3) =  1.0D0
C
      DO I = 1, 3
        DO J = 1, 3
          ROT(I,J) = T(I,J)
        END DO
      END DO
C
      SHELLS = 0
      RETURN
      END
```

> **T layout convention**: `e_material_i = T_ij · e_global_j` (rows are the local
> axes). Verify with a single-element test when using anisotropic materials —
> sign errors flip material axes silently.

## Template 2: Deformation-Following Orientation (fiber rotation)

```fortran
      SUBROUTINE ORIENT(COORDS,NNODE,NODE,NOEL,JMATYP,LAYER,KSPT,
     1 SHELLS,COORDSS)
C
C  1-axis follows the fiber direction (node 1 -> node 2, current geometry)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*8 JMATYP(2)
      DIMENSION COORDS(3,*),NODE(*),COORDSS(3,*)
      DIMENSION T(3,3), ROT(3,3)
      REAL*8 DX, DY, DZ, L, L2
      INTEGER I, J
C
      DX = COORDS(1,2) - COORDS(1,1)
      DY = COORDS(2,2) - COORDS(2,1)
      DZ = COORDS(3,2) - COORDS(3,1)
      L  = SQRT(DX*DX + DY*DY + DZ*DZ)
      IF (L .LT. 1.0D-12) L = 1.0D-12
C
      T(1,1) = DX/L
      T(1,2) = DY/L
      T(1,3) = DZ/L
C
C  2-axis: project global Y onto the plane normal to the fiber (Gram-Schmidt)
      T(2,1) = -T(1,2)*T(1,1)
      T(2,2) =  1.0D0 - T(1,2)*T(1,2)
      T(2,3) = -T(1,2)*T(1,3)
      L2 = SQRT(T(2,1)**2 + T(2,2)**2 + T(2,3)**2)
      IF (L2 .GT. 1.0D-12) THEN
        T(2,1) = T(2,1)/L2
        T(2,2) = T(2,2)/L2
        T(2,3) = T(2,3)/L2
      END IF
C
C  3-axis: cross product 1 x 2
      T(3,1) = T(1,2)*T(2,3) - T(1,3)*T(2,2)
      T(3,2) = T(1,3)*T(2,1) - T(1,1)*T(2,3)
      T(3,3) = T(1,1)*T(2,2) - T(1,2)*T(2,1)
C
      DO I = 1, 3
        DO J = 1, 3
          ROT(I,J) = T(I,J)
        END DO
      END DO
C
      SHELLS = 0
      RETURN
      END
```

## Input File Example

```abaqus
*Orientation, system=USER, definition=COORDINATES
User-Orient,
** then: *Solid Section, elset=..., material=..., orientation=User-Orient
```

## Guidance

1. `T` must be orthonormal with det = +1 — check every time you edit it
2. Provide `ROT = T` (or identity) unless you need special state-variable rotation
3. Validate with a single anisotropic element loaded along the material axes
4. For simple constant angles use CAE `*Orientation` (`SPECIFY ORIENT`); ORIENT is
   for spatially varying / deformation-dependent fields only

## Related

- `usdfld_spatial.md` — field-variable alternative for property variation
- `composite/reference/layup_definition.md` — layup orientations
