# Abaqus FRIC 自定义摩擦子程序技能

## 技能描述

本技能指导AI生成Abaqus的自定义摩擦子程序FRIC，用于定义复杂的接触摩擦行为，如速度依赖摩擦、温度依赖摩擦、磨损模型等。

## 适用场景

- 速度依赖摩擦（Stribeck效应）
- 温度依赖摩擦（热摩擦学）
- 磨损导致的摩擦系数变化
- 各向异性摩擦

## 关键特性

| 特性 | 说明 |
|------|------|
| 分析类型 | 隐式/显式接触分析 |
| 摩擦模型 | 库仑摩擦、速度依赖、温度依赖 |
| 输出 | 摩擦应力、摩擦系数 |

## FRIC 接口定义

```fortran
SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| FRICOUT(2) | 输出 | 切向摩擦应力、摩擦系数 |
| FRICIN(*) | 输入 | 摩擦相关输入数据 |
| SLIP | 输入 | 滑移量 |
| DRDT | 输入 | 滑移速度 |
| TEMP | 输入 | 接触点温度 |
| CPRESS | 输入 | 接触压力 |

## 摩擦模型类型

### 1. 速度依赖摩擦（Stribeck曲线）

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  速度依赖摩擦 - Stribeck模型
C  包含静摩擦、混合润滑、流体动力润滑区域
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 V, MU_S, MU_K, MU_F, V_CRIT, V_TRANSITION
      REAL*8 MU, EXP_TERM
      REAL*8 TAU_MAX
C
C-----------------------------------------------------------------------
C  摩擦参数
C-----------------------------------------------------------------------
      MU_S = 0.5D0           ! 静摩擦系数
      MU_K = 0.3D0           ! 动摩擦系数（中等速度）
      MU_F = 0.05D0          ! 流体动力摩擦系数（高速度）
      V_CRIT = 0.001D0       ! 静动摩擦转换速度 (m/s)
      V_TRANSITION = 1.0D0   ! 混合润滑向流体动力转换速度 (m/s)
C
C-----------------------------------------------------------------------
C  获取滑移速度
C-----------------------------------------------------------------------
      V = ABS(DRDT)
C
C-----------------------------------------------------------------------
C  Stribeck曲线模型
C-----------------------------------------------------------------------
      IF (V .LT. V_CRIT) THEN
C       静摩擦区
        MU = MU_S - (MU_S - MU_K) * (V / V_CRIT)
      ELSE IF (V .LT. V_TRANSITION) THEN
C       混合润滑区（指数衰减）
        EXP_TERM = EXP(-LOG(MU_K/MU_F) * (V - V_CRIT) 
     1           / (V_TRANSITION - V_CRIT))
        MU = MU_K * EXP_TERM
      ELSE
C       流体动力区
        MU = MU_F
      END IF
C
C-----------------------------------------------------------------------
C  计算最大剪切应力
C  τ_max = μ * σ_n
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
C
C-----------------------------------------------------------------------
C  输出
C-----------------------------------------------------------------------
      FRICOUT(1) = TAU_MAX   ! 摩擦应力
      FRICOUT(2) = MU        ! 摩擦系数
C
      RETURN
      END
```

### 2. 温度依赖摩擦（热摩擦学）

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  温度依赖摩擦
C  摩擦系数随接触面温度变化
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 T_CONTACT, MU_0, T_REF, T_CRITICAL
      REAL*8 MU, TAU_MAX
C
C-----------------------------------------------------------------------
C  摩擦参数
C-----------------------------------------------------------------------
      MU_0 = 0.4D0           ! 室温摩擦系数
      T_REF = 20.0D0         ! 参考温度 (°C)
      T_CRITICAL = 400.0D0   ! 临界温度 (°C)
C
C-----------------------------------------------------------------------
C  获取接触面温度
C-----------------------------------------------------------------------
      T_CONTACT = TEMP
C
C-----------------------------------------------------------------------
C  温度依赖摩擦模型
C  温度升高导致摩擦系数下降（氧化膜、材料软化）
C-----------------------------------------------------------------------
      IF (T_CONTACT .LE. T_REF) THEN
        MU = MU_0
      ELSE IF (T_CONTACT .LT. T_CRITICAL) THEN
        MU = MU_0 * (1.0D0 - 0.5D0*(T_CONTACT - T_REF)
     1       / (T_CRITICAL - T_REF))
      ELSE
        MU = 0.5D0 * MU_0
      END IF
C
C-----------------------------------------------------------------------
C  输出
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
      FRICOUT(1) = TAU_MAX
      FRICOUT(2) = MU
C
      RETURN
      END
```

### 3. 磨损导致的摩擦退化

```fortran
      SUBROUTINE FRIC(FRICOUT,FRICIN,TIME,DTIME,DBS,SLIP,DRDT,
     1 TEMP,DTEMP,PREDEF,DPRED,CNORM,CMTN,CPRESS,CRatio,
     1 CMNAME,IPARAM,IPARAM2,NINPT,NINPC,NPRED,NPREDF,NSTRV,
     1 NCYCLE,ILINEAR,FIELD,NFIELD)
C
C  考虑磨损的摩擦模型
C  累积滑移距离导致摩擦系数下降
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), DBS(3), CMTN(3),
     1 PREDEF(*), DPRED(*), FIELD(NFIELD)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
      REAL*8 MU_0, MU_MIN, S_TOTAL, S_CRIT
      REAL*8 DS, MU, TAU_MAX
      INTEGER SV_INDEX
      PARAMETER(SV_INDEX=1)
C
C-----------------------------------------------------------------------
C  参数
C-----------------------------------------------------------------------
      MU_0 = 0.5D0           ! 初始摩擦系数
      MU_MIN = 0.2D0         ! 最小摩擦系数（完全磨损后）
      S_CRIT = 1.0D0         ! 临界累积滑移距离 (m)
C
C-----------------------------------------------------------------------
C  从状态变量读取累积滑移距离
C-----------------------------------------------------------------------
      S_TOTAL = FRICIN(NINPT + SV_INDEX)
C
C-----------------------------------------------------------------------
C  更新累积滑移距离
C-----------------------------------------------------------------------
      DS = ABS(SLIP)
      S_TOTAL = S_TOTAL + DS
C
C-----------------------------------------------------------------------
C  磨损导致的摩擦系数下降
C-----------------------------------------------------------------------
      IF (S_TOTAL .LE. S_CRIT) THEN
        MU = MU_0 - (MU_0 - MU_MIN) * (S_TOTAL / S_CRIT)
      ELSE
        MU = MU_MIN
      END IF
C
C-----------------------------------------------------------------------
C  输出
C-----------------------------------------------------------------------
      TAU_MAX = MU * CPRESS
      FRICOUT(1) = TAU_MAX
      FRICOUT(2) = MU
C
C  存储更新后的累积滑移距离（通过状态变量）
      FRICOUT(3) = S_TOTAL
C
      RETURN
      END
```

## 输入文件示例

```abaqus
*Surface interaction, name=Frictional_Contact
*Friction, user
** 传递摩擦参数（可选）
0.3, 0.1, 1.0
*Surface behavior, pressure-overclosure=hard
```

## 显式摩擦（VRIC）

显式分析使用VRIC子程序，接口略有不同：

```fortran
      SUBROUTINE VRIC(FRICOUT,FRICIN,TIME,DTIME,TEMP,DTEMP,
     1 FIELD,NFIELD,CPRESS,CNORM,CMTN,NPRED,NPREDF,DBS,DRDT,
     1 SLIP,ILINEAR,NSTRV,CMNAME,IPARAM,IPARAM2)
C
      INCLUDE 'VABA_PARAM.INC'
C
      DIMENSION FRICOUT(2), FRICIN(*), TIME(2), FIELD(NFIELD),
     1 CMTN(3), PREDEF(*), DPRED(*), DBS(3)
      CHARACTER*80 CMNAME
      INTEGER IPARAM(*), IPARAM2(*)
C
C  与FRIC类似，但处理块数据
      REAL*8 MU
      MU = 0.3D0
      FRICOUT(1) = MU * CPRESS
      FRICOUT(2) = MU
C
      RETURN
      END
```

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 38.1
