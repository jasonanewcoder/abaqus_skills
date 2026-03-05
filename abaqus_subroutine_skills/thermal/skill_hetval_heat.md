# Abaqus HETVAL 热生成子程序技能

## 技能描述

本技能指导AI生成Abaqus的热生成子程序HETVAL，用于定义材料内部的热生成，如固化放热、焦耳热、化学反应热等。

## 适用场景

- 复合材料固化放热
- 电池充放电热生成
- 粘塑性耗散热
- 化学反应热

## 关键特性

| 特性 | 说明 |
|------|------|
| 调用时机 | 热传导分析每个积分点 |
| 输出 | 单位体积热生成率 |
| 依赖 | 温度、状态变量、场变量 |

## HETVAL 接口定义

```fortran
SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| FLUX(1) | 输出 | 热生成率（单位体积）|
| FLUX(2) | 输出 | 热生成率对温度的导数 |
| TEMP | 输入 | 当前温度 |
| STATEV(*) | 输入/输出 | 状态变量 |
| TIME(1) | 输入 | 当前步时间 |

## 热生成类型

### 1. 固化放热（复合材料）

```fortran
      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  复合材料固化放热
C  基于固化度和Arrhenius动力学
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION FLUX(2), TIME(2), STATEV(*), PREDEF(*), DPRED(*),
     1 COORMS(3)
C
      REAL*8 T, ALPHA, DALPHA_DT, RATE
      REAL*8 A1, A2, DE1, DE2, M, N, R
      REAL*8 K1, K2, DH_DT
      REAL*8 TOTAL_HEAT
C
C-----------------------------------------------------------------------
C  固化参数
C-----------------------------------------------------------------------
      A1  = 2.08D7           ! 指前因子1 (1/s)
      A2  = -1.85D7          ! 指前因子2 (1/s)
      DE1 = 8.07D4           ! 活化能1 (J/mol)
      DE2 = 7.88D4           ! 活化能2 (J/mol)
      M   = 0.51D0           ! 反应级数m
      N   = 1.47D0           ! 反应级数n
      R   = 8.314D0          ! 气体常数
      TOTAL_HEAT = 4.0D5     ! 总固化热 (J/kg)
      RHO = 1500.0D0         ! 密度 (kg/m³)
C
C-----------------------------------------------------------------------
C  获取温度和固化度
C-----------------------------------------------------------------------
      T = TEMP + 273.15D0    ! 转换为绝对温度
      ALPHA = STATEV(1)      ! 从状态变量获取固化度
C
C-----------------------------------------------------------------------
C  计算反应速率常数
C-----------------------------------------------------------------------
      K1 = A1 * EXP(-DE1/(R*T))
      K2 = A2 * EXP(-DE2/(R*T))
C
C-----------------------------------------------------------------------
C  计算固化速率
C-----------------------------------------------------------------------
      IF (ALPHA .LT. 0.3D0) THEN
        RATE = (K1 + K2*ALPHA**M) * (1.0D0-ALPHA)**N
      ELSE
        RATE = K1 * (1.0D0-ALPHA)**N
      END IF
C
C-----------------------------------------------------------------------
C  计算热生成率
C-----------------------------------------------------------------------
      FLUX(1) = RHO * TOTAL_HEAT * RATE
C
C-----------------------------------------------------------------------
C  计算温度导数（近似）
C-----------------------------------------------------------------------
      DH_DT = FLUX(1) * DE1 / (R*T*T)
      FLUX(2) = DH_DT
C
C-----------------------------------------------------------------------
C  更新状态变量（固化度）
C-----------------------------------------------------------------------
      STATEV(1) = STATEV(1) + RATE * DTIME
      IF (STATEV(1) .GT. 0.999D0) STATEV(1) = 0.999D0
C
      RETURN
      END
```

### 2. 粘塑性耗散热

```fortran
      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C
C  粘塑性耗散热生成
C  基于塑性功转化
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME
      DIMENSION FLUX(2), TIME(2), STATEV(*), PREDEF(*), DPRED(*),
     1 COORMS(3)
C
      REAL*8 ETA, SIGMA_EQ, EPS_PLAS, RATE_PLAS
      REAL*8 HEAT_GENERATION
C
C-----------------------------------------------------------------------
C  参数
C-----------------------------------------------------------------------
      ETA = 0.9D0            ! 塑性功转化为热的比例（Taylor-Quinney系数）
C
C-----------------------------------------------------------------------
C  从状态变量获取等效塑性应变和应变率
C  假设STATEV(1)=等效塑性应变，STATEV(2)=塑性应变率
C-----------------------------------------------------------------------
      EPS_PLAS = STATEV(1)
      RATE_PLAS = STATEV(2)
C
C-----------------------------------------------------------------------
C  计算等效应力（从状态变量或本构关系）
C  这里假设简单的幂律硬化
C-----------------------------------------------------------------------
      SIGMA_Y = 200.0D6      ! 屈服应力 (Pa)
      K = 500.0D6            ! 硬化系数
      N_HARD = 0.3D0         ! 硬化指数
C
      SIGMA_EQ = SIGMA_Y + K * (EPS_PLAS**N_HARD)
C
C-----------------------------------------------------------------------
C  计算热生成率（塑性功率）
C  Q = η * σ_eq * ε̇_plas
C-----------------------------------------------------------------------
      HEAT_GENERATION = ETA * SIGMA_EQ * RATE_PLAS
C
      FLUX(1) = HEAT_GENERATION
      FLUX(2) = 0.0D0        ! 简化为零
C
      RETURN
      END
```

## 输入文件示例

```abaqus
*Material, name=Composite
*Conductivity
0.5, 
*Specific heat
1200.0, 
*Density
1500.0, 
*Heat generation
*Depvar
2
```

## FILM（自定义对流系数）

```fortran
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
C  自定义对流系数 - 温度依赖或位置依赖
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION H(2), TIME(2), COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C
      REAL*8 T, H_CONST, H_COEFF
      REAL*8 X, Y, Z, DIST
C
C-----------------------------------------------------------------------
C  基础对流系数
C-----------------------------------------------------------------------
      H_CONST = 10.0D0       ! W/(m²·K)
C
C-----------------------------------------------------------------------
C  温度依赖对流系数（自然对流）
C-----------------------------------------------------------------------
      T = TEMP
      H_COEFF = H_CONST * (1.0D0 + 0.01D0*(T-20.0D0))
C
C-----------------------------------------------------------------------
C  位置依赖（冷却通道附近增强换热）
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      DIST = SQRT(X*X + Y*Y)
C
      IF (DIST .LT. 0.1D0) THEN
        H_COEFF = H_COEFF * 2.0D0
      END IF
C
C-----------------------------------------------------------------------
C  输出
C-----------------------------------------------------------------------
      H(1) = H_COEFF         ! 对流系数
      H(2) = 0.01D0*H_CONST  ! 对温度的导数（近似）
      SINK = 20.0D0          ! 环境温度
C
      RETURN
      END
```

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 29.3
