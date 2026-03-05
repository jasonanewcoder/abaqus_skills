# 示例2: 中级DLOAD - 移动车轮载荷分析

## 示例概述

本示例演示如何使用DLOAD子程序模拟移动车轮载荷在桥面上的作用。这是一个典型的工程应用，涉及载荷的空间分布和时间变化。

## 学习目标

1. 理解DLOAD子程序的工作机制
2. 掌握移动载荷的空间分布定义
3. 学习坐标和时间的综合使用
4. 验证移动载荷的准确性

## 工程背景

移动车轮载荷是桥梁工程、路面工程和轨道工程中的常见问题。实际车轮载荷具有以下特征：
- 接触面积内的非均匀分布（近似抛物线或高斯分布）
- 随时间移动的位置变化
- 多车轮的叠加效应

## 完整Fortran代码

```fortran
C=======================================================================
C  Example 2: Moving Wheel Load DLOAD
C  移动车轮载荷 - 双轮组高斯分布载荷
C=======================================================================
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C-----------------------------------------------------------------------
      INCLUDE 'ABA_PARAM.INC'
C-----------------------------------------------------------------------
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, V, X0, Y_TRACK
      REAL*8 WHEEL_SPACING, WHEEL_WIDTH
      REAL*8 GAUSS_WIDTH_X, GAUSS_WIDTH_Y
      REAL*8 T, X, Y
      REAL*8 X_WHEEL1, X_WHEEL2
      REAL*8 DIST1_SQ, DIST2_SQ
      REAL*8 LOAD_SHAPE1, LOAD_SHAPE2
      REAL*8 PI
      PARAMETER(PI=3.141592653589793D0)
C
C-----------------------------------------------------------------------
C  载荷参数定义
C-----------------------------------------------------------------------
      F0 = 50000.0D0           ! 单个车轮峰值载荷 (N/m²)
      V = 10.0D0               ! 移动速度 (m/s) = 36 km/h
      X0 = -5.0D0              ! 初始X位置 (m)
      Y_TRACK = 2.0D0          ! 车道中心线Y坐标 (m)
      WHEEL_SPACING = 1.8D0    ! 轮距 (m)
      GAUSS_WIDTH_X = 0.15D0   ! X方向分布宽度 (m)
      GAUSS_WIDTH_Y = 0.12D0   ! Y方向分布宽度 (m)
C
C-----------------------------------------------------------------------
C  计算当前时间的车轮位置
C-----------------------------------------------------------------------
      T = TIME(2)              ! 总时间
      
C     前轮位置（双轮组）
      X_WHEEL1 = X0 + V * T
      X_WHEEL2 = X_WHEEL1      ! 同轴双轮
C
C-----------------------------------------------------------------------
C  获取当前积分点坐标
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
C
C-----------------------------------------------------------------------
C  计算到两个车轮中心的距离平方
C-----------------------------------------------------------------------
C     左轮 (Y_TRACK - WHEEL_SPACING/2)
      DIST1_SQ = ((X - X_WHEEL1)/GAUSS_WIDTH_X)**2 
     1         + ((Y - (Y_TRACK - WHEEL_SPACING/2.0D0))/GAUSS_WIDTH_Y)**2
C
C     右轮 (Y_TRACK + WHEEL_SPACING/2)
      DIST2_SQ = ((X - X_WHEEL2)/GAUSS_WIDTH_X)**2 
     1         + ((Y - (Y_TRACK + WHEEL_SPACING/2.0D0))/GAUSS_WIDTH_Y)**2
C
C-----------------------------------------------------------------------
C  高斯分布载荷形状
C-----------------------------------------------------------------------
      LOAD_SHAPE1 = EXP(-0.5D0 * DIST1_SQ)
      LOAD_SHAPE2 = EXP(-0.5D0 * DIST2_SQ)
C
C-----------------------------------------------------------------------
C  总载荷（两个车轮叠加）
C-----------------------------------------------------------------------
      F = F0 * (LOAD_SHAPE1 + LOAD_SHAPE2)
C
C     载荷已经离开桥面时归零（可选）
      IF (X_WHEEL1 .GT. 15.0D0) THEN
        F = 0.0D0
      END IF
C
C-----------------------------------------------------------------------
      RETURN
      END
C=======================================================================
```

## Abaqus输入文件

```abaqus
*Heading
** 示例2: 移动车轮载荷分析
*Preprint, echo=NO, model=NO, history=NO, contact=NO
**
** 参数设置
*Parameter
Bridge_Length = 20.0
Bridge_Width = 6.0
Wheel_Load = 50000.0
Vehicle_Speed = 10.0
**
** 节点定义（简支桥面板）
*Node, nset=All_Nodes
** (使用网格生成命令或外部文件)
*NGEN, nset=Edge1
1, 21, 1
*NGEN, nset=Edge2
101, 121, 1
*Nfill, nset=All_Nodes
Edge1, Edge2, 10, 20
**
** 单元定义
*Element, type=S4R, elset=Deck
1, 1, 2, 22, 21
*ELGEN, elset=Deck
1, 20, 1, 1, 10, 20, 20
**
*Shell section, elset=Deck, material=Concrete
0.3, 5
**
*Material, name=Concrete
*Elastic
30.0e9, 0.2
*Density
2500.0
**
** 边界条件（简支）
*Boundary
Edge1, 3, 3, 0.0
*Boundary
Edge2, 1, 1, 0.0
Edge2, 3, 3, 0.0
**
** 分析步 - 车辆通过
*Step, name=Vehicle_Passing, nlgeom=NO
*Dynamic, explicit
, 2.5
**
** 用户自定义载荷
*Dload, user
Deck, P, 1.0
**
** 输出设置
*Output, field, variable=PRESELECT
*Output, history
*Node output, nset=Deck_Center
U3, V3, A3
*End step
```

## 结果分析

### 关键输出变量

| 变量 | 说明 | 单位 |
|------|------|------|
| U3 | 桥面竖向位移 | m |
| S11, S22 | 桥面平面应力 | Pa |
| SF1, SF2 | 壳单元剪力 | N/m |

### 期望结果特征

1. **位移时程**：随着车轮接近、通过、离开，位移先增大后减小
2. **动态效应**：高速时产生明显动力放大效应
3. **包络图**：多位置传感器可绘制最大响应包络

## 扩展功能

### 1. 多车叠加

```fortran
C  添加第二辆车
X_VEHICLE2 = X0_2 + V * T
IF (ABS(X_VEHICLE2 - X_WHEEL1) .GT. Safe_Distance) THEN
  F = F + F0 * (LOAD_SHAPE3 + LOAD_SHAPE4)
END IF
```

### 2. 制动工况

```fortran
C  速度递减
IF (T .GT. Brake_Start) THEN
  V_EFF = V - Decel * (T - Brake_Start)
ELSE
  V_EFF = V
END IF
```

### 3. 路面不平度

```fortran
C  添加随机不平度
Call Random_Number(Rand)
Roughness = Amplitude * Sin(Wave_Number * X_WHEEL1 + Rand)
F = F * (1.0 + Roughness)
```

## 验证方法

1. **静态验证**：将速度设为极小值，与静力解对比
2. **能量验证**：检查总能量平衡
3. **质量检验**：验证等效总载荷

```python
# Python后处理验证
odb = openOdb(path='job_dload.odb')
lastFrame = odb.steps['Vehicle_Passing'].frames[-1]
stress = lastFrame.fieldOutputs['S']
max_stress = max([value.maxPrincipal for value in stress.values])
print(f'Maximum principal stress: {max_stress/1e6:.2f} MPa')
```

## 常见问题

### 1. 载荷突然消失

**原因**: 网格过粗，车轮移动到单元间隙

**解决**: 细化网格或增大载荷分布宽度

### 2. 高频振荡

**原因**: 显式分析时间步长过大

**解决**: 减小时间步长或增加质量缩放

### 3. 不合理的位移

**原因**: 边界条件约束不足

**解决**: 检查刚体位移约束

## 参考

- 本技能库: `load/skill_dload_moving.md`
- Abaqus Analysis User's Guide, Section 34.4
