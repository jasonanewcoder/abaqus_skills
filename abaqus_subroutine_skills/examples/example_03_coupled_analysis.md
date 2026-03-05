# 示例3: 高级耦合分析 - 热-力耦合UMAT+USDFLD+HETVAL

## 示例概述

本示例演示如何实现热-力全耦合分析，涉及UMAT（材料本构）、USDFLD（场变量定义）和HETVAL（热生成）三个子程序的协同工作。这是复合材料固化过程模拟的典型应用。

## 学习目标

1. 理解多个子程序间的数据传递机制
2. 掌握状态变量在多子程序间的共享
3. 学习热-力耦合分析的设置方法
4. 实现复杂的物理过程模拟

## 物理问题描述

**复合材料热压罐固化过程**：
- 温度升高引发树脂固化反应
- 固化反应放热改变温度场
- 温度变化影响材料力学性能
- 固化收缩产生残余应力

## 耦合关系图

```
温度场 → USDFLD计算固化度 → UMAT更新材料属性
                ↓                    ↓
         HETVAL计算反应热 ← 固化速率
                ↓
         热传导方程 → 新温度场
```

## 完整Fortran代码

### 1. USDFLD - 固化度场变量

```fortran
C=======================================================================
C  Example 3 Part 1: USDFLD - Cure Degree Field
C=======================================================================
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,
     3 LACCFLA)
C-----------------------------------------------------------------------
      INCLUDE 'ABA_PARAM.INC'
C-----------------------------------------------------------------------
      CHARACTER*80 CMNAME,ORNAME
      CHARACTER*3  FLGRAY(15)
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2),COORD(3)
      DIMENSION JMAC(*),JMATYP(*)
C
      REAL*8 TEMP_CURR, ALPHA_CURR, ALPHA_NEW
      REAL*8 RATE_CURR
      REAL*8 A1, A2, DE1, DE2, M, N, R_GAS
C
C-----------------------------------------------------------------------
C  固化动力学参数
C-----------------------------------------------------------------------
      A1    = 3.5017D7       ! 指前因子1 (1/s)
      A2    = -3.3567D7      ! 指前因子2 (1/s)
      DE1   = 8.07D4         ! 活化能1 (J/mol)
      DE2   = 7.93D4         ! 活化能2 (J/mol)
      M     = 0.8125D0       ! 反应级数m
      N     = 2.7365D0       ! 反应级数n
      R_GAS = 8.314D0        ! 气体常数
C
C-----------------------------------------------------------------------
C  从状态变量读取上一增量步的固化度和温度
C-----------------------------------------------------------------------
      IF (TIME(1) .EQ. 0.0D0) THEN
        ALPHA_CURR = 0.0D0
        TEMP_CURR = 25.0D0 + 273.15D0
      ELSE
        ALPHA_CURR = STATEV(1)
        TEMP_CURR = STATEV(2)
      END IF
C
C-----------------------------------------------------------------------
C  更新温度（从热分析传入，简化处理）
C  实际应用中从场变量或预定义场获取
C-----------------------------------------------------------------------
      TEMP_CURR = TEMP_CURR + 0.5D0  ! 简化：升温速率
C
C-----------------------------------------------------------------------
C  计算固化速率常数
C-----------------------------------------------------------------------
      K1 = A1 * EXP(-DE1/(R_GAS*TEMP_CURR))
      K2 = A2 * EXP(-DE2/(R_GAS*TEMP_CURR))
C
C-----------------------------------------------------------------------
C  自催化固化模型
C-----------------------------------------------------------------------
      IF (ALPHA_CURR .LT. 0.3D0) THEN
        RATE_CURR = (K1 + K2*ALPHA_CURR**M) * (1.0D0-ALPHA_CURR)**N
      ELSE
        RATE_CURR = K1 * (1.0D0-ALPHA_CURR)**N
      END IF
C
C-----------------------------------------------------------------------
C  更新固化度
C-----------------------------------------------------------------------
      ALPHA_NEW = ALPHA_CURR + RATE_CURR * DTIME
      IF (ALPHA_NEW .GT. 0.999D0) ALPHA_NEW = 0.999D0
C
C-----------------------------------------------------------------------
C  输出场变量
C-----------------------------------------------------------------------
      FIELD(1) = ALPHA_NEW          ! 固化度
      FIELD(2) = TEMP_CURR          ! 温度
C
C-----------------------------------------------------------------------
C  更新状态变量供后续使用
C-----------------------------------------------------------------------
      STATEV(1) = ALPHA_NEW
      STATEV(2) = TEMP_CURR
      STATEV(3) = RATE_CURR         ! 固化速率（供HETVAL使用）
C
C-----------------------------------------------------------------------
      RETURN
      END
```

### 2. HETVAL - 固化反应热

```fortran
C=======================================================================
C  Example 3 Part 2: HETVAL - Cure Reaction Heat
C=======================================================================
      SUBROUTINE HETVAL(CMNAME,TEMP,TIME,DTIME,STATEV,FLUX,
     1 PREDEF,DPRED,COORMS,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
C-----------------------------------------------------------------------
      INCLUDE 'ABA_PARAM.INC'
C-----------------------------------------------------------------------
      CHARACTER*80 CMNAME
      DIMENSION FLUX(2), TIME(2), STATEV(*), PREDEF(*), DPRED(*),
     1 COORMS(3)
C
      REAL*8 H_TOTAL, RHO, RATE_CURR
      REAL*8 HEAT_GEN, DHEAT_DT
C
C-----------------------------------------------------------------------
C  材料参数
C-----------------------------------------------------------------------
      H_TOTAL = 4.0D5          ! 总固化热 (J/kg)
      RHO     = 1560.0D0       ! 复合材料密度 (kg/m³)
C
C-----------------------------------------------------------------------
C  从状态变量获取固化速率（由USDFLD计算并存储）
C-----------------------------------------------------------------------
      RATE_CURR = STATEV(3)
C
C-----------------------------------------------------------------------
C  计算热生成率
C  Q = ρ * H_total * dα/dt
C-----------------------------------------------------------------------
      HEAT_GEN = RHO * H_TOTAL * RATE_CURR
C
C-----------------------------------------------------------------------
C  温度导数（简化处理）
C-----------------------------------------------------------------------
      DHEAT_DT = 0.0D0
C
C-----------------------------------------------------------------------
C  输出
C-----------------------------------------------------------------------
      FLUX(1) = HEAT_GEN
      FLUX(2) = DHEAT_DT
C
C-----------------------------------------------------------------------
      RETURN
      END
```

### 3. UMAT - 固化相关材料本构

```fortran
C=======================================================================
C  Example 3 Part 3: UMAT - Cure Dependent Properties
C=======================================================================
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C-----------------------------------------------------------------------
      INCLUDE 'ABA_PARAM.INC'
C-----------------------------------------------------------------------
      CHARACTER*80 CMNAME
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
C
      REAL*8 ALPHA, TEMP_CURR
      REAL*8 E_UNCURED, E_CURED, NU
      REAL*8 E_EFF, LAMBDA, G
      REAL*8 ALPHA_THERMAL, CURE_SHRINKAGE
      REAL*8 STRAIN_THERMAL(6), STRAIN_CURE(6)
      REAL*8 STRAIN_MECH(6)
      INTEGER I, J
C
C-----------------------------------------------------------------------
C  材料参数
C-----------------------------------------------------------------------
      E_UNCURED   = 1.0D3      ! 未固化模量 (MPa)
      E_CURED     = 30.0D3     ! 完全固化模量 (MPa)
      NU          = 0.35D0     ! 泊松比
      ALPHA_THERMAL = 3.5D-5   ! 热膨胀系数 (1/°C)
      BETA_CURE   = 0.02D0     ! 固化收缩系数
C
C-----------------------------------------------------------------------
C  从状态变量获取固化度和温度
C-----------------------------------------------------------------------
      ALPHA = STATEV(1)
      TEMP_CURR = STATEV(2)
C
C-----------------------------------------------------------------------
C  固化度相关的弹性模量（幂律混合）
C-----------------------------------------------------------------------
      IF (ALPHA .LT. 0.3D0) THEN
C       凝胶前阶段 - 低模量
        E_EFF = E_UNCURED
      ELSE
C       凝胶后阶段 - 模量快速增长
        E_EFF = E_UNCURED + (E_CURED - E_UNCURED) 
     1        * ((ALPHA - 0.3D0)/0.7D0)**2
      END IF
C
C-----------------------------------------------------------------------
C  计算弹性常数
C-----------------------------------------------------------------------
      G      = E_EFF / (2.0D0*(1.0D0+NU))
      LAMBDA = E_EFF*NU / ((1.0D0+NU)*(1.0D0-2.0D0*NU))
C
C-----------------------------------------------------------------------
C  计算热应变和固化收缩应变
C-----------------------------------------------------------------------
      DO I = 1, NDI
        STRAIN_THERMAL(I) = ALPHA_THERMAL * (TEMP_CURR - 25.0D0)
        STRAIN_CURE(I) = BETA_CURE * ALPHA
      END DO
      DO I = NDI+1, NTENS
        STRAIN_THERMAL(I) = 0.0D0
        STRAIN_CURE(I) = 0.0D0
      END DO
C
C-----------------------------------------------------------------------
C  计算机械应变
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        STRAIN_MECH(I) = STRAN(I) + DSTRAN(I) 
     1                 - STRAIN_THERMAL(I) - STRAIN_CURE(I)
      END DO
C
C-----------------------------------------------------------------------
C  组装雅可比矩阵
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C
      DO I = 1, NDI
        DO J = 1, NDI
          DDSDDE(I,J) = LAMBDA
        END DO
        DDSDDE(I,I) = LAMBDA + 2.0D0*G
      END DO
      DO I = NDI+1, NTENS
        DDSDDE(I,I) = G
      END DO
C
C-----------------------------------------------------------------------
C  应力更新
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        STRESS(I) = 0.0D0
        DO J = 1, NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J)*STRAIN_MECH(J)
        END DO
      END DO
C
C-----------------------------------------------------------------------
      RETURN
      END
```

## Abaqus输入文件

```abaqus
*Heading
** 示例3: 热-力耦合固化分析
*Preprint, echo=NO, model=NO, history=NO, contact=NO
**
** 节点和单元定义（略）
**
** 材料定义 - 耦合材料
*Material, name=Cure_Material
*Conductivity
0.5, 
*Specific heat
1200.0, 
*Density
1560.0, 
*Heat generation
*User defined field
*Depvar
5
** 状态变量说明：
** 1 - 固化度
** 2 - 温度
** 3 - 固化速率
** 4-5 - 预留
**
** 力学属性通过UMAT定义
**
** 固化循环温度边界
*Amplitude, name=Cure_Cycle, definition=tabular
0.0, 25.0
600.0, 120.0
3600.0, 180.0
7200.0, 180.0
10800.0, 25.0
**
** 分析步
*Step, name=Cure_Analysis, inc=1000
*Coupled temp-displacement
0.1, 12000.0, 1.0e-5, 10.0
**
** 边界条件
*Boundary, amplitude=Cure_Cycle
Top_Surface, 11, 11, 1.0
**
** 对称边界
*Boundary
Sym_Plane, 1, 1, 0.0
**
** 输出
*Output, field
*Node output
NT, U
*Element output
S, E, SDV, HFL
*Output, history
*Node output, nset=Monitor_Point
NT, U3
*Element output, elset=Center_Element
SDV1, SDV2, S33
*End step
```

## 结果解读

### 1. 固化度演化

```python
import matplotlib.pyplot as plt

# 从.odb文件提取数据
time = [...]  # 时间序列
alpha = [...]  # 固化度

plt.plot(time, alpha)
plt.xlabel('Time (s)')
plt.ylabel('Degree of Cure')
plt.title('Cure Evolution')
plt.grid(True)
plt.show()
```

### 2. 温度-固化耦合效应

- 固化放热导致温度超过设定值
- 高温加速固化形成正反馈
- 厚截面中心可能出现热失控

### 3. 残余应力分布

- 固化收缩导致压缩应力
- 冷却不均匀导致弯曲应力
- 脱模后应力重新分布

## 验证清单

| 检查项 | 方法 |
|--------|------|
| 固化度范围 | 0 ≤ α ≤ 1 |
| 温度物理合理性 | 与环境温度对比 |
| 能量守恒 | 输入热量 = 材料储能 + 反应热 |
| 残余应力自平衡 | 截面合力为零 |

## 扩展方向

1. **纤维体积分数影响**：将Vf作为场变量
2. **粘弹性效应**：添加Prony级数
3. **损伤演化**：固化应力导致微裂纹
4. **多尺度分析**：微观固化收缩到宏观残余应力

## 参考

- 本技能库: 
  - `field/skill_usdfld_spatial.md`
  - `thermal/skill_hetval_heat.md`
  - `material/skill_umat_elastic.md`
- Bogetti & Gillespie, "Process-Induced Stress and Deformation"
