# Abaqus SIGINI 初始应力子程序技能

## 技能描述

本技能指导AI生成Abaqus的初始应力子程序SIGINI，用于定义初始应力状态，如地应力平衡、残余应力等。

## 适用场景

- 地应力平衡（岩土工程）
- 残余应力初始化（焊接、铸造）
- 预应力结构
- 重力平衡初始步

## 关键特性

| 特性 | 说明 |
|------|------|
| 调用时机 | 分析开始时每个积分点 |
| 输出 | 初始应力张量（6个分量）|
| 依赖 | 坐标、单元编号等 |

## SIGINI 接口定义

```fortran
SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| SIGMA(NTENS) | 输出 | 初始应力分量 |
| COORDS(NCRDS) | 输入 | 积分点坐标 |
| NTENS | 输入 | 应力分量数 |
| NOEL | 输入 | 单元编号 |
| LREBAR | 输入 | 钢筋标志 |

## 初始应力类型

### 1. 静水压力分布（地应力）

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  地应力初始化 - 随深度线性增加的静水压力
C  适用于岩土工程分析
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, DEPTH
      REAL*8 GAMMA, K0, SV, SH
C
C-----------------------------------------------------------------------
C  地应力参数
C-----------------------------------------------------------------------
      GAMMA = 20.0D3       ! 土体重度 (N/m³)
      K0    = 0.5D0        ! 静止土压力系数
      GROUND_LEVEL = 0.0D0 ! 地表高程
C
C-----------------------------------------------------------------------
C  计算深度
C-----------------------------------------------------------------------
      Z = COORDS(3)
      DEPTH = GROUND_LEVEL - Z
      IF (DEPTH .LT. 0.0D0) DEPTH = 0.0D0
C
C-----------------------------------------------------------------------
C  计算垂直应力和水平应力
C-----------------------------------------------------------------------
      SV = GAMMA * DEPTH          ! 垂直应力 (压为负)
      SH = K0 * SV                ! 水平应力
C
C-----------------------------------------------------------------------
C  设置初始应力（压应力为负）
C-----------------------------------------------------------------------
      SIGMA(1) = SH               ! S11
      SIGMA(2) = SH               ! S22
      SIGMA(3) = SV               ! S33
      SIGMA(4) = 0.0D0            ! S12
      IF (NTENS .GT. 4) THEN
        SIGMA(5) = 0.0D0          ! S13
        SIGMA(6) = 0.0D0          ! S23
      END IF
C
      RETURN
      END
```

### 2. 预应力筋初始应力

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  预应力筋初始应力
C  用于模拟预应力混凝土结构
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, TENDON_FORCE, AREA
      REAL*8 SIGMA_PRESTRESS
      INTEGER TENDON_ID
C
C-----------------------------------------------------------------------
C  判断是否为钢筋/预应力筋
C-----------------------------------------------------------------------
      IF (LREBAR .EQ. 1) THEN
C       预应力参数
        TENDON_FORCE = 1000.0D3    ! 预应力 (N)
        AREA = 500.0D-6            ! 筋截面积 (m²)
        SIGMA_PRESTRESS = TENDON_FORCE / AREA
C
C       根据筋名称判断
        IF (REBARN .EQ. 'TENDON_1') THEN
          SIGMA(1) = SIGMA_PRESTRESS
        ELSE IF (REBARN .EQ. 'TENDON_2') THEN
          SIGMA(1) = SIGMA_PRESTRESS * 0.9D0
        ELSE
          SIGMA(1) = 0.0D0
        END IF
      ELSE
C       混凝土部分无初始应力
        DO I = 1, NTENS
          SIGMA(I) = 0.0D0
        END DO
      END IF
C
      RETURN
      END
```

### 3. 焊接残余应力

```fortran
      SUBROUTINE SIGINI(SIGMA,COORDS,NTENS,NCRDS,NOEL,NPT,LAYER,
     1 KSPT,LREBAR,REBARN)
C
C  焊接残余应力分布
C  基于双椭圆形分布模型
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION SIGMA(NTENS),COORDS(NCRDS)
      CHARACTER*80 REBARN
C
      REAL*8 X, Y, Z, WELD_CENTER, WELD_WIDTH
      REAL*8 DIST, SIGMA_MAX, SIGMA_RESIDUAL
      REAL*8 WIDTH_1, WIDTH_2
C
C-----------------------------------------------------------------------
C  焊接参数
C-----------------------------------------------------------------------
      WELD_CENTER = 0.0D0          ! 焊缝中心X坐标
      WELD_WIDTH  = 0.02D0         ! 焊缝宽度 (m)
      SIGMA_MAX   = 200.0D6        ! 最大残余应力 (Pa)
      WIDTH_1     = 0.01D0         ! 热影响区宽度1
      WIDTH_2     = 0.05D0         ! 热影响区宽度2
C
C-----------------------------------------------------------------------
C  计算到焊缝中心的距离
C-----------------------------------------------------------------------
      X = COORDS(1)
      DIST = ABS(X - WELD_CENTER)
C
C-----------------------------------------------------------------------
C  双椭圆残余应力分布
C-----------------------------------------------------------------------
      IF (DIST .LE. WIDTH_1) THEN
C       焊缝区（拉应力）
        SIGMA_RESIDUAL = SIGMA_MAX * SQRT(1.0D0 - (DIST/WIDTH_1)**2)
      ELSE IF (DIST .LE. WIDTH_2) THEN
C       热影响区（压应力）
        SIGMA_RESIDUAL = -SIGMA_MAX * 0.3D0 
     1                 * SQRT(1.0D0 - ((DIST-WIDTH_1)/(WIDTH_2-WIDTH_1))**2)
      ELSE
C       母材区（应力释放）
        SIGMA_RESIDUAL = 0.0D0
      END IF
C
C-----------------------------------------------------------------------
C  设置应力（纵向残余应力为主）
C-----------------------------------------------------------------------
      SIGMA(1) = SIGMA_RESIDUAL    ! S11 - 纵向
      SIGMA(2) = 0.0D0             ! S22
      SIGMA(3) = 0.0D0             ! S33
      SIGMA(4) = 0.0D0             ! S12
      IF (NTENS .GT. 4) THEN
        SIGMA(5) = 0.0D0
        SIGMA(6) = 0.0D0
      END IF
C
      RETURN
      END
```

## 输入文件示例

```abaqus
** 初始应力
*Initial Conditions, type=STRESS, user
Whole_Model,
```

## 注意事项

1. **平衡检查**：初始应力应尽可能接近平衡状态
2. **应力协调**：不同区域初始应力应连续
3. **第一步分析**：通常设为静力通用步进行平衡
4. **输出验证**：检查初始应力是否正确施加

## SDVINI（初始状态变量）

用于初始化UMAT状态变量：

```fortran
      SUBROUTINE SDVINI(STATEV,COORDS,NSTATV,NCRDS,NOEL,NPT,
     1 LAYER,KSPT)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION STATEV(NSTATV),COORDS(NCRDS)
C
C     初始化等效塑性应变
      STATEV(1) = 0.0D0
C
C     初始化其他状态变量
      DO I = 2, NSTATV
        STATEV(I) = 0.0D0
      END DO
C
      RETURN
      END
```

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 19.2
