# Abaqus USDFLD 自定义场变量子程序技能

## 技能描述

本技能指导AI生成Abaqus的自定义场变量子程序USDFLD，用于定义随时间或空间变化的材料属性场，如温度场、损伤场、初始缺陷分布等。

## 适用场景

- 温度相关的材料属性
- 空间非均匀材料（如FGM功能梯度材料）
- 初始缺陷/孔隙分布
- 固化度分布（复合材料固化）
- 湿度分布

## 关键特性

| 特性 | 说明 |
|------|------|
| 调用时机 | 每个材料点每次增量开始时 |
| 输出 | 场变量数组，用于后续材料计算 |
| 依赖 | 可依赖时间、坐标、其他场变量 |
| 传递 | 场变量可传递给UMAT等子程序 |

## USDFLD 接口定义

```fortran
SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| FIELD(NFIELD) | 输出 | 场变量值 |
| STATEV(NSTATV) | 输入/输出 | 状态变量 |
| TIME(1) | 输入 | 当前步时间 |
| TIME(2) | 输入 | 总时间 |
| COORD(3) | 输入 | 材料点坐标 |
| NFIELD | 输入 | 场变量数量 |
| NSTATV | 输入 | 状态变量数量 |

## 场变量类型

### 1. 空间线性分布（梯度场）

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  空间线性梯度场变量
C  用于功能梯度材料(FGM)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      CHARACTER*3  FLGRAY(15)
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 X, Y, Z, F0, F1, X_MIN, X_MAX, GRADIENT
C
C-----------------------------------------------------------------------
C  定义线性梯度参数
C-----------------------------------------------------------------------
      F0    = 0.0D0        ! X_MIN处的场变量值
      F1    = 1.0D0        ! X_MAX处的场变量值
      X_MIN = 0.0D0        ! 梯度起始X坐标
      X_MAX = 10.0D0       ! 梯度终止X坐标
C
C-----------------------------------------------------------------------
C  获取当前点坐标
C-----------------------------------------------------------------------
      X = COORD(1)
      Y = COORD(2)
      Z = COORD(3)
C
C-----------------------------------------------------------------------
C  计算线性插值
C-----------------------------------------------------------------------
      IF (X .LE. X_MIN) THEN
        FIELD(1) = F0
      ELSE IF (X .GE. X_MAX) THEN
        FIELD(1) = F1
      ELSE
        GRADIENT = (X - X_MIN) / (X_MAX - X_MIN)
        FIELD(1) = F0 + (F1 - F0) * GRADIENT
      END IF
C
C-----------------------------------------------------------------------
C  状态变量存储（可选）
C-----------------------------------------------------------------------
      STATEV(1) = FIELD(1)
C
      RETURN
      END
```

### 2. 高斯分布场（局部热点）

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  高斯分布场变量 - 模拟局部温度热点或损伤集中区
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 X, Y, Z, X_CENTER, Y_CENTER, Z_CENTER
      REAL*8 AMP, SIGMA_X, SIGMA_Y, SIGMA_Z
      REAL*8 DIST_SQ, FIELD_VAL
      INTEGER N_HOTSPOTS, I
      PARAMETER(N_HOTSPOTS=3)
      REAL*8 XC(N_HOTSPOTS), YC(N_HOTSPOTS), ZC(N_HOTSPOTS)
C
C-----------------------------------------------------------------------
C  定义热点位置（可从文件读取）
C-----------------------------------------------------------------------
      DATA XC /1.0D0, 3.0D0, 5.0D0/
      DATA YC /1.0D0, 2.0D0, 1.5D0/
      DATA ZC /0.0D0, 0.0D0, 0.0D0/
      
      AMP = 100.0D0         ! 峰值场变量值
      SIGMA_X = 0.5D0       ! X方向分布宽度
      SIGMA_Y = 0.5D0       ! Y方向分布宽度
      SIGMA_Z = 0.5D0       ! Z方向分布宽度
C
C-----------------------------------------------------------------------
C  获取当前点坐标
C-----------------------------------------------------------------------
      X = COORD(1)
      Y = COORD(2)
      Z = COORD(3)
C
C-----------------------------------------------------------------------
C  计算多热点叠加的高斯场
C-----------------------------------------------------------------------
      FIELD_VAL = 0.0D0
      DO I = 1, N_HOTSPOTS
        DIST_SQ = ((X-XC(I))/SIGMA_X)**2 
     1          + ((Y-YC(I))/SIGMA_Y)**2 
     2          + ((Z-ZC(I))/SIGMA_Z)**2
        FIELD_VAL = FIELD_VAL + AMP * EXP(-0.5D0*DIST_SQ)
      END DO
C
      FIELD(1) = FIELD_VAL
C
C-----------------------------------------------------------------------
C  存储状态变量
C-----------------------------------------------------------------------
      STATEV(1) = FIELD(1)
C
      RETURN
      END
```

### 3. 时间相关的固化度场

```fortran
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C
C  复合材料固化度场
C  基于Arrhenius方程的固化动力学
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 T_TEMP, T_CURR, T_PREV
      REAL*8 A1, A2, DE1, DE2, M, N, R
      REAL*8 ALPHA, DALPHA, RATE
      REAL*8 K1, K2
C
C-----------------------------------------------------------------------
C  固化动力学参数
C-----------------------------------------------------------------------
      A1  = 2.08D7           ! 指前因子1 (1/s)
      A2  = -1.85D7          ! 指前因子2 (1/s)
      DE1 = 8.07D4           ! 活化能1 (J/mol)
      DE2 = 7.88D4           ! 活化能2 (J/mol)
      M   = 0.51D0           ! 反应级数m
      N   = 1.47D0           ! 反应级数n
      R   = 8.314D0          ! 气体常数 (J/(mol*K))
C
C-----------------------------------------------------------------------
C  从状态变量读取上一增量步的固化度
C-----------------------------------------------------------------------
      IF (TIME(1) .EQ. 0.0D0) THEN
        ALPHA = 0.0D0        ! 初始固化度
      ELSE
        ALPHA = STATEV(1)
      END IF
C
C-----------------------------------------------------------------------
C  获取当前温度（假设场变量2为温度）
C  实际应用中应从热分析结果获取
C-----------------------------------------------------------------------
      T_CURR = 180.0D0 + 273.15D0   ! 当前温度(K)，示例值
C
C-----------------------------------------------------------------------
C  计算反应速率常数（Arrhenius方程）
C-----------------------------------------------------------------------
      K1 = A1 * EXP(-DE1/(R*T_CURR))
      K2 = A2 * EXP(-DE2/(R*T_CURR))
C
C-----------------------------------------------------------------------
C  计算固化速率（自催化模型）
C-----------------------------------------------------------------------
      IF (ALPHA .LT. 0.3D0) THEN
        RATE = (K1 + K2*ALPHA**M) * (1.0D0-ALPHA)**N
      ELSE
        RATE = K1 * (1.0D0-ALPHA)**N
      END IF
C
C-----------------------------------------------------------------------
C  更新固化度
C-----------------------------------------------------------------------
      DALPHA = RATE * DTIME
      ALPHA = ALPHA + DALPHA
C
C  限制范围
      IF (ALPHA .GT. 0.999D0) ALPHA = 0.999D0
C
C-----------------------------------------------------------------------
C  输出场变量
C-----------------------------------------------------------------------
      FIELD(1) = ALPHA       ! 固化度
      FIELD(2) = T_CURR      ! 温度
C
C-----------------------------------------------------------------------
C  更新状态变量
C-----------------------------------------------------------------------
      STATEV(1) = ALPHA
      STATEV(2) = RATE
C
      RETURN
      END
```

## 与材料属性关联

在输入文件中关联场变量：

```abaqus
*Material, name=FGM_Material
*Elastic
** E随场变量变化
100000.0, 0.3, , , FIELD(1)
200000.0, 0.3, , , 1.0
**
*User Defined Field
*Depvar
2
```

## 注意事项

1. **调用顺序**：USDFLD在每个增量步开始时调用，早于UMAT
2. **场变量数量**：NFIELD需在输入文件中定义
3. **传递机制**：场变量通过STATEV或直接传递给UMAT
4. **更新频率**：可通过PNEWDT控制时间步

## 扩展方向

- 与外部数据文件耦合（实测温度场）
- 随机场生成（蒙特卡洛分析）
- 多物理场耦合（热-化-力）
- 损伤场演化

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26.7.2
