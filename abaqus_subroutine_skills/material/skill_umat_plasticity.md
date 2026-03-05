# Abaqus UMAT 弹塑性材料子程序技能

## 技能描述

本技能指导AI生成基于von Mises屈服准则的各向同性硬化弹塑性UMAT子程序，采用径向返回算法（Radial Return Mapping）。

## 适用场景

- 金属材料的塑性变形分析
- 大变形小应变问题
- 各向同性硬化材料

## 关键特性

| 特性 | 说明 |
|------|------|
| 屈服准则 | von Mises |
| 硬化模型 | 各向同性硬化（线性/幂律）|
| 流动法则 | 关联流动法则 |
| 算法 | 径向返回算法（精确/一致切线）|
| 大变形 | 支持（基于Jaumann率）|

## 理论公式

### 1. 屈服函数

```
f = ||s|| - √(2/3) * σ_y(ε̄^p) ≤ 0
```

其中s为偏应力，σ_y为屈服应力，ε̄^p为等效塑性应变。

### 2. 流动法则

```
Δε^p = Δγ * ∂f/∂σ = Δγ * (3/2) * s/||s||
```

### 3. 硬化定律（幂律）

```
σ_y = σ_0 + K*(ε̄^p)^n
```

### 4. 径向返回算法

```
1. 弹性预测：σ^trial = σ_n + C:Δε
2. 偏应力：s^trial = dev(σ^trial)
3. 屈服判断：f^trial = ||s^trial|| - √(2/3)*σ_y
4. 若f^trial > 0:
   Δγ = f^trial / (2*G + (2/3)*H)
   s_{n+1} = s^trial * (1 - 2*G*Δγ/||s^trial||)
   ε̄^p_{n+1} = ε̄^p_n + √(2/3)*Δγ
```

## 材料参数

| 参数 | 符号 | 单位 | 说明 |
|------|------|------|------|
| 杨氏模量 | E | MPa | 弹性模量 |
| 泊松比 | ν | - | 泊松比 |
| 初始屈服应力 | σ_0 | MPa | 屈服起始点 |
| 硬化系数 | K | MPa | 硬化曲线参数 |
| 硬化指数 | n | - | 幂律硬化指数 |

## Fortran代码

```fortran
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,
     6 KSTEP,KINC)
C
C  von Mises弹塑性UMAT - 径向返回算法
C  各向同性硬化，关联流动法则
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
      REAL*8 E, NU, SIGMA_Y, HARD_K, HARD_N
      REAL*8 G, KMOD, LAM, FAC
C  应力/应变相关
      REAL*8 STRESS_TRIAL(6), STRESS_DEV(6)
      REAL*8 STRAIN_ELAS(6)
      REAL*8 EQPLAS, DEQPL, SMIS_EFF, SMIS_TRIAL
      REAL*8 YIELD_STRESS, HARD_MOD
      REAL*8 DGAMMA, FACTOR, ONEMFAC
      REAL*8 TERM1, TERM2, TERM3
      INTEGER I, J
      PARAMETER(TOLER=1.0D-10, SQRT_2_3=0.8164965809D0)
C
C-----------------------------------------------------------------------
C  读取材料参数
C-----------------------------------------------------------------------
      E        = PROPS(1)    ! 杨氏模量
      NU       = PROPS(2)    ! 泊松比
      SIGMA_Y  = PROPS(3)    ! 初始屈服应力
      HARD_K   = PROPS(4)    ! 硬化系数K
      HARD_N   = PROPS(5)    ! 硬化指数n
C
C-----------------------------------------------------------------------
C  计算弹性常数
C-----------------------------------------------------------------------
      G    = E / (2.0D0*(1.0D0+NU))         ! 剪切模量
      KMOD = E / (3.0D0*(1.0D0-2.0D0*NU))   ! 体积模量
      LAM  = KMOD - 2.0D0*G/3.0D0            ! 拉梅常数
C
C-----------------------------------------------------------------------
C  读取状态变量
C  STATEV(1) = 等效塑性应变
C-----------------------------------------------------------------------
      EQPLAS = STATEV(1)
C
C-----------------------------------------------------------------------
C  弹性预测：计算试应力
C-----------------------------------------------------------------------
C  体积应变增量
      TRACE = DSTRAN(1) + DSTRAN(2) + DSTRAN(3)
      P_TRIAL = (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0 + KMOD*TRACE
C
C  偏应变增量和试偏应力
      DO I = 1, NDI
        STRESS_DEV(I) = STRESS(I) - (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0
     1                + 2.0D0*G*(DSTRAN(I) - TRACE/3.0D0)
      END DO
      DO I = NDI+1, NTENS
        STRESS_DEV(I) = STRESS(I) + 2.0D0*G*DSTRAN(I)
      END DO
C
C-----------------------------------------------------------------------
C  计算试应力的等效偏应力
C-----------------------------------------------------------------------
      SMIS_TRIAL = SQRT(STRESS_DEV(1)**2 + STRESS_DEV(2)**2 
     1           + STRESS_DEV(3)**2 + 2.0D0*(STRESS_DEV(4)**2
     2           + STRESS_DEV(5)**2 + STRESS_DEV(6)**2))
C
C-----------------------------------------------------------------------
C  计算当前屈服应力
C-----------------------------------------------------------------------
      IF (EQPLAS .LE. TOLER) THEN
        YIELD_STRESS = SIGMA_Y
        HARD_MOD = 0.0D0
      ELSE
        YIELD_STRESS = SIGMA_Y + HARD_K*(EQPLAS**HARD_N)
        HARD_MOD = HARD_K*HARD_N*(EQPLAS**(HARD_N-1.0D0))
      END IF
C
C-----------------------------------------------------------------------
C  屈服判断
C-----------------------------------------------------------------------
      PHI = SMIS_TRIAL - SQRT_2_3*YIELD_STRESS
C
      IF (PHI .LE. TOLER) THEN
C       弹性步
        DEQPL = 0.0D0
        DO I = 1, NTENS
          STRESS(I) = STRESS_DEV(I)
        END DO
        DO I = 1, NDI
          STRESS(I) = STRESS(I) + P_TRIAL
        END DO
      ELSE
C       塑性步 - 径向返回
C-----------------------------------------------------------------------
C  计算塑性乘子增量
C-----------------------------------------------------------------------
        DEQPL = PHI / (2.0D0*G + 2.0D0*HARD_MOD/3.0D0)
        DGAMMA = 1.5D0*DEQPL
C
C-----------------------------------------------------------------------
C  更新等效塑性应变
C-----------------------------------------------------------------------
        EQPLAS = EQPLAS + DEQPL
        STATEV(1) = EQPLAS
C
C-----------------------------------------------------------------------
C  更新应力
C-----------------------------------------------------------------------
        FACTOR = 1.0D0 - 2.0D0*G*DGAMMA/SMIS_TRIAL
        ONEMFAC = 1.0D0 - FACTOR
C
        DO I = 1, NTENS
          STRESS(I) = FACTOR*STRESS_DEV(I)
        END DO
        DO I = 1, NDI
          STRESS(I) = STRESS(I) + P_TRIAL
        END DO
C
      END IF
C
C-----------------------------------------------------------------------
C  计算一致切线模量（雅可比矩阵）
C-----------------------------------------------------------------------
C  初始化
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C
      IF (PHI .LE. TOLER) THEN
C       弹性雅可比
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = LAM
          END DO
          DDSDDE(I,I) = LAM + 2.0D0*G
        END DO
        DO I = NDI+1, NTENS
          DDSDDE(I,I) = G
        END DO
      ELSE
C       弹塑性一致切线
        TERM1 = 2.0D0*G*FACTOR
        TERM2 = 2.0D0*G*(ONEMFAC - DGAMMA/SMIS_TRIAL)
     1        / (1.0D0 + HARD_MOD/(3.0D0*G))
C
C       偏应力部分的雅可比
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = -TERM1/3.0D0 - TERM2*STRESS_DEV(I)
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)
          END DO
          DDSDDE(I,I) = DDSDDE(I,I) + TERM1
        END DO
C
C       体积部分
        DO I = 1, NDI
          DO J = 1, NDI
            DDSDDE(I,J) = DDSDDE(I,J) + KMOD
          END DO
        END DO
C
C       剪切部分
        DO I = NDI+1, NTENS
          DDSDDE(I,I) = TERM1/2.0D0
          DO J = NDI+1, NTENS
            DDSDDE(I,J) = DDSDDE(I,J) - TERM2*STRESS_DEV(I)
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)
          END DO
        END DO
      END IF
C
C-----------------------------------------------------------------------
C  塑性耗散功
C-----------------------------------------------------------------------
      SPD = YIELD_STRESS*DEQPL/DTIME
C
      RETURN
      END
```

## 输入文件示例

```abaqus
*Material, name=Steel_Plastic
*User Material, constants=5
** E, NU, SIGMA_Y, K, n
210000.0, 0.3, 250.0, 500.0, 0.3
*Depvar
1
** 状态变量：
** 1 - 等效塑性应变
```

## 算法验证要点

1. **屈服面一致性**：确保应力点始终位于屈服面上
2. **能量一致性**：检查塑性耗散非负
3. **切线一致性**：雅可比矩阵应与数值微分一致
4. **对象性**：在大转动下保持应力更新对象性

## 扩展方向

- 随动硬化（Armstrong-Frederick模型）
- 混合硬化（各向同性+随动）
- 各向异性屈服（Hill48、Barlat）
- 温度依赖性
- 应变率效应（Johnson-Cook）

## 参考文献

- Simo & Hughes, "Computational Inelasticity", Springer
- Dunne & Petrinic, "Introduction to Computational Plasticity"
- Abaqus User Subroutines Reference Guide
