# Abaqus UEL 自定义单元子程序技能

## 技能描述

本技能指导AI生成Abaqus的自定义单元子程序UEL，实现特殊单元类型，如非线性弹簧、阻尼器、零厚度接触单元等。

## 适用场景

- 非线性弹簧单元
- 自定义阻尼器
- 零厚度粘结单元
- 特殊连接单元
- 多点位移约束单元

## 关键特性

| 特性 | 说明 |
|------|------|
| 自由度 | 可定义任意自由度组合 |
| 几何 | 任意节点数、任意维度 |
| 本构 | 完全自定义力-位移关系 |
| 输出 | 自定义单元输出变量 |

## UEL 接口定义

```fortran
SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| RHS(NDOFEL,NRHS) | 输出 | 残差力向量 |
| AMATRX(NDOFEL,NDOFEL) | 输出 | 单元刚度矩阵 |
| SVARS(NSVARS) | 输入/输出 | 单元状态变量 |
| U(NDOFEL) | 输入 | 节点总位移 |
| DU(NDOFEL) | 输入 | 节点位移增量 |
| COORDS | 输入 | 节点坐标 |

## 单元类型

### 1. 非线性弹簧单元（2节点）

```fortran
      SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
C
C  非线性弹簧单元 UEL
C  2节点，每个节点3个平动自由度
C  力-位移关系：F = k1*u + k2*u^3 (硬化型非线性)
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
C  定义自由度映射
C  节点1: DOF 1-3 (Ux, Uy, Uz)
C  节点2: DOF 4-6 (Ux, Uy, Uz)
C-----------------------------------------------------------------------
      DATA DOF_MAP /1, 2, 3, 4, 5, 6/
C
C-----------------------------------------------------------------------
C  读取材料参数
C-----------------------------------------------------------------------
      K1    = PROPS(1)     ! 线性刚度 (N/m)
      K2    = PROPS(2)     ! 非线性刚度系数 (N/m³)
      F_MAX = PROPS(3)     ! 最大承载力 (N)
      U_SEP = PROPS(4)     ! 分离位移 (m)
C
C-----------------------------------------------------------------------
C  计算弹簧初始长度
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
C  计算当前长度和方向余弦
C-----------------------------------------------------------------------
C  节点位移
      DX = (X2 + U(4)) - (X1 + U(1))
      DY = (Y2 + U(5)) - (Y1 + U(2))
      DZ = (Z2 + U(6)) - (Z1 + U(3))
      
      L = SQRT(DX*DX + DY*DY + DZ*DZ)
C
C  方向余弦
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
C  计算相对位移（沿弹簧方向）
C-----------------------------------------------------------------------
      DISP_REL(1) = U(4) - U(1)
      DISP_REL(2) = U(5) - U(2)
      DISP_REL(3) = U(6) - U(3)
      
      STRAIN = L - L0    ! 弹簧变形量（伸长为正）
C
C-----------------------------------------------------------------------
C  非线性本构关系
C  F = k1*u + k2*u^3  (当 |F| < F_MAX)
C  F = 0               (当 |u| > u_sep，分离)
C-----------------------------------------------------------------------
      IF (ABS(STRAIN) .GT. U_SEP) THEN
C       分离
        FORCE = 0.0D0
        STIFFNESS = 0.0D0
      ELSE
C       非线性弹性
        FORCE = K1*STRAIN + K2*STRAIN**3
        
C       限制最大力
        IF (ABS(FORCE) .GT. F_MAX) THEN
          FORCE = SIGN(F_MAX, FORCE)
          STIFFNESS = 0.0D0    ! 完全塑性
        ELSE
          STIFFNESS = K1 + 3.0D0*K2*STRAIN**2
        END IF
      END IF
C
C-----------------------------------------------------------------------
C  组装残差向量（内力）
C-----------------------------------------------------------------------
      DO I = 1, 3
C       节点1的力（负方向）
        RHS(I,1) = -FORCE * DIR_COS(I)
C       节点2的力（正方向）
        RHS(I+3,1) = FORCE * DIR_COS(I)
      END DO
C
C-----------------------------------------------------------------------
C  组装刚度矩阵
C-----------------------------------------------------------------------
C  初始化
      DO I = 1, NDOFEL
        DO J = 1, NDOFEL
          AMATRX(I,J) = 0.0D0
        END DO
      END DO
C
C  几何刚度 + 材料刚度
      DO I = 1, 3
        DO J = 1, 3
C         对角项
          AMATRX(I,I) = AMATRX(I,I) + STIFFNESS * DIR_COS(I)**2
          AMATRX(I+3,I+3) = AMATRX(I+3,I+3) + STIFFNESS * DIR_COS(I)**2
C         耦合项
          AMATRX(I,I+3) = -STIFFNESS * DIR_COS(I)**2
          AMATRX(I+3,I) = -STIFFNESS * DIR_COS(I)**2
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  存储状态变量
C-----------------------------------------------------------------------
      SVARS(1) = STRAIN      ! 弹簧应变
      SVARS(2) = FORCE       ! 弹簧力
      SVARS(3) = L           ! 当前长度
C
C-----------------------------------------------------------------------
C  能量计算（可选）
C-----------------------------------------------------------------------
      ENERGY(1) = 0.5D0*K1*STRAIN**2 + 0.25D0*K2*STRAIN**4  ! 弹性应变能
C
      RETURN
      END
```

### 2. 阻尼器单元

```fortran
      SUBROUTINE UEL(RHS,AMATRX,SVARS,ENERGY,NDOFEL,NRHS,NSVARS,
     1 PROPS,NPROPS,COORDS,MCRD,NNODE,U,DU,V,A,JTYPE,TIME,DTIME,
     2 KSTEP,KINC,JELEM,PARAMS,NDLOAD,JDLTYP,ADLMAG,PREDEF,
     3 NPREDF,LFLAGS,MLVARX,DDLMAG,MDLOAD,PNEWDT,JPROPS,NJPROP,
     4 PERIOD)
C
C  粘滞阻尼器单元
C  力与相对速度成正比
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
C  读取阻尼系数
C-----------------------------------------------------------------------
      C_DAMP = PROPS(1)      ! 阻尼系数 (N·s/m)
C
C-----------------------------------------------------------------------
C  计算方向余弦（假设初始方向）
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
C  计算相对速度
C-----------------------------------------------------------------------
      V_REL(1) = V(4) - V(1)
      V_REL(2) = V(5) - V(2)
      V_REL(3) = V(6) - V(3)
C
C  相对速度在弹簧方向的分量
      V_NORM = V_REL(1)*DIR_COS(1) + V_REL(2)*DIR_COS(2) 
     1       + V_REL(3)*DIR_COS(3)
C
C-----------------------------------------------------------------------
C  阻尼力
C-----------------------------------------------------------------------
      FORCE = C_DAMP * V_NORM
C
C-----------------------------------------------------------------------
C  组装残差
C-----------------------------------------------------------------------
      DO I = 1, 3
        RHS(I,1) = -FORCE * DIR_COS(I)
        RHS(I+3,1) = FORCE * DIR_COS(I)
      END DO
C
C-----------------------------------------------------------------------
C  阻尼刚度矩阵（对隐式分析）
C-----------------------------------------------------------------------
      DO I = 1, NDOFEL
        DO J = 1, NDOFEL
          AMATRX(I,J) = 0.0D0
        END DO
      END DO
C
C  阻尼贡献（乘以适当的积分因子）
      DO I = 1, 3
        AMATRX(I,I) = C_DAMP * DIR_COS(I)**2
        AMATRX(I+3,I+3) = C_DAMP * DIR_COS(I)**2
        AMATRX(I,I+3) = -C_DAMP * DIR_COS(I)**2
        AMATRX(I+3,I) = -C_DAMP * DIR_COS(I)**2
      END DO
C
C-----------------------------------------------------------------------
C  耗散能
C-----------------------------------------------------------------------
      ENERGY(2) = FORCE * V_NORM * DTIME    ! 耗散能量
C
      RETURN
      END
```

## 输入文件示例

```abaqus
** 用户自定义单元
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

## 显式自定义单元（VUEL）

显式分析使用VUEL，接口类似但处理块数据。

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 32.15
