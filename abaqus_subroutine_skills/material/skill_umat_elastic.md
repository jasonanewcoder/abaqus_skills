# Abaqus UMAT 线弹性材料子程序技能

## 技能描述

本技能指导AI生成Abaqus Standard隐式分析的线弹性材料UMAT子程序。这是最简单的UMAT实现，适合作为入门示例。

## 适用场景

- 各向同性线弹性材料
- 验证UMAT接口和编译
- 作为更复杂材料模型的基础模板

## 关键特性

| 特性 | 说明 |
|------|------|
| 分析类型 | 隐式静态/动态 (Standard) |
| 材料模型 | 线弹性，各向同性 |
| 输入参数 | 杨氏模量E，泊松比ν |
| 状态变量 | 无 |
| 应力更新 | 直接计算，无条件稳定 |

## 理论公式

### 本构关系（三维）

```
σ = D : ε
```

其中弹性矩阵D（各向同性材料）：

```
D = E/((1+ν)(1-2ν)) ×
    [1-ν   ν     ν     0        0        0    ]
    [ν     1-ν   ν     0        0        0    ]
    [ν     ν     1-ν   0        0        0    ]
    [0     0     0     (1-2ν)/2 0        0    ]
    [0     0     0     0        (1-2ν)/2 0    ]
    [0     0     0     0        0        (1-2ν)/2]
```

## UMAT 接口定义

```fortran
SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| STRESS(NTENS) | 输入/输出 | 应力张量（Voigt记法）|
| STATEV(NSTATV) | 输入/输出 | 状态变量数组 |
| DDSDDE(NTENS,NTENS) | 输出 | 材料雅可比矩阵 ∂Δσ/∂Δε |
| STRAN(NTENS) | 输入 | 总应变（增量步开始时）|
| DSTRAN(NTENS) | 输入 | 应变增量 |
| PROPS(NPROPS) | 输入 | 材料参数数组 |
| NTENS | 输入 | 应力/应变分量数(=NDI+NSHR) |

## Fortran代码模板

```fortran
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C
C  线弹性材料UMAT子程序
C  各向同性线弹性，适用于Abaqus/Standard
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
C
C  材料参数
C  PROPS(1) = 杨氏模量 E
C  PROPS(2) = 泊松比  NU
      REAL*8 E, NU, EG, EG2, ELAM, FAC
      INTEGER I, J
C
C-----------------------------------------------------------------------
C  读取材料参数
C-----------------------------------------------------------------------
      E    = PROPS(1)    ! 杨氏模量
      NU   = PROPS(2)    ! 泊松比
C
C-----------------------------------------------------------------------
C  计算弹性常数
C-----------------------------------------------------------------------
      EG2  = E / (1.0D0 + NU)        ! 2*G
      EG   = EG2 / 2.0D0              ! G
      ELAM = E * NU / ((1.0D0 + NU) * (1.0D0 - 2.0D0*NU))  ! 拉梅常数
C
C-----------------------------------------------------------------------
C  初始化雅可比矩阵
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  组装雅可比矩阵（三维/平面应变/轴对称）
C-----------------------------------------------------------------------
      IF (NDI .EQ. 3) THEN
C       三维或平面应变情况
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
C       平面应力情况
        FAC = E / (1.0D0 - NU*NU)
        DDSDDE(1,1) = FAC
        DDSDDE(2,2) = FAC
        DDSDDE(1,2) = FAC * NU
        DDSDDE(2,1) = FAC * NU
        DDSDDE(3,3) = FAC * (1.0D0 - NU) / 2.0D0
      END IF
C
C-----------------------------------------------------------------------
C  应力更新：σ_new = σ_old + D : Δε
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J) * DSTRAN(J)
        END DO
      END DO
C
C-----------------------------------------------------------------------
C  计算应变能（可选）
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

## Abaqus输入文件示例

```abaqus
** 材料定义
*Material, name=Elastic_UMAT
*User Material, constants=2
** E, NU
210000.0, 0.3
```

## 验证方法

1. **简单拉伸测试**：与Abaqus内置弹性材料对比应力-应变曲线
2. **单单元测试**：检查应力更新是否正确
3. **对称性测试**：验证雅可比矩阵对称性

## 常见错误与解决

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 编译错误 | Fortran语法错误 | 检查固定格式（第6列续行符）|
| 结果异常 | 雅可比矩阵不正确 | 验证DDSDDE的对称性和数值 |
| 收敛困难 | 雅可比不一致 | 确保DDSDDE = ∂Δσ/∂Δε |

## 扩展建议

此模板可扩展为：
- 各向异性弹性（正交各向异性、横观各向同性）
- 温度相关弹性模量
- 非线性弹性（超弹性）

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26.7
