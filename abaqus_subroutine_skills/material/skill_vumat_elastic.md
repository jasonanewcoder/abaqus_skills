# Abaqus VUMAT 线弹性材料子程序技能

## 技能描述

本技能指导AI生成Abaqus Explicit显式分析的线弹性材料VUMAT子程序。显式分析对稳定性有特殊要求。

## 适用场景

- 冲击动力学分析
- 高速碰撞模拟
- 瞬态动力学问题
- 大变形分析

## 关键特性

| 特性 | 说明 |
|------|------|
| 分析类型 | 显式动力学 (Explicit) |
| 材料模型 | 线弹性，各向同性 |
| 应力更新 | 基于变形梯度 |
| 大变形 | 支持（基于Jaumann率或Green-Naghdi率）|

## VUMAT与UMAT的关键区别

| 特性 | UMAT (Standard) | VUMAT (Explicit) |
|------|-----------------|------------------|
| 时间积分 | 隐式 | 显式 |
| 雅可比矩阵 | 需要 | 不需要 |
| 变形梯度 | 提供 | 提供 |
| 应力更新 | 增量形式 | 基于变形梯度 |
| 稳定性 | 无条件（收敛前提下）| 有条件（CFL条件）|

## VUMAT 接口定义

```fortran
subroutine vumat(
     1 nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2 stepTime, totalTime, dt, cmname, coordMp, charLength,
     3 props, density, strainInc, relSpinInc,
     4 tempOld, stretchOld, defgradOld, fieldOld,
     5 stressOld, stateOld, enerInternOld, enerInelasOld,
     6 tempNew, stretchNew, defgradNew, fieldNew,
     7 stressNew, stateNew, enerInternNew, enerInelasNew)
```

## 关键参数说明

| 参数 | 说明 |
|------|------|
| nblock | 积分点块的数量 |
| ndir | 直接应力/应变分量数 |
| nshr | 剪切应力/应变分量数 |
| defgradOld/New | 增量开始/结束时的变形梯度 |
| strainInc | 应变增量 |
| stressOld/New | 增量开始/结束时的应力 |
| relSpinInc | 相对旋率增量 |

## 理论公式

### 基于Jaumann率的应力更新

```
σ^∇ = C : D
σ_{n+1} = σ_n + Δt * σ^∇ + Ω·σ_n - σ_n·Ω
```

其中：
- D为变形率张量（应变增量/Δt）
- Ω为旋率张量
- σ^∇为Jaumann率

## Fortran代码

```fortran
      subroutine vumat(
     1 nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     2 stepTime, totalTime, dt, cmname, coordMp, charLength,
     3 props, density, strainInc, relSpinInc,
     4 tempOld, stretchOld, defgradOld, fieldOld,
     5 stressOld, stateOld, enerInternOld, enerInelasOld,
     6 tempNew, stretchNew, defgradNew, fieldNew,
     7 stressNew, stateNew, enerInternNew, enerInelasNew)
C
C  显式动力学线弹性VUMAT
C  基于Jaumann率的应力更新
C
      include 'vaba_param.inc'
C
      dimension props(nprops), density(nblock), coordMp(nblock,*),
     1 charLength(nblock), strainInc(nblock,ndir+nshr),
     2 relSpinInc(nblock,nshr), tempOld(nblock),
     3 stretchOld(nblock,ndir+nshr),
     4 defgradOld(nblock,ndir+nshr+nshr),
     5 fieldOld(nblock,nfieldv), stressOld(nblock,ndir+nshr),
     6 stateOld(nblock,nstatev), enerInternOld(nblock),
     7 enerInelasOld(nblock), tempNew(nblock),
     8 stretchNew(nblock,ndir+nshr),
     9 defgradNew(nblock,ndir+nshr+nshr),
     1 fieldNew(nblock,nfieldv),
     2 stressNew(nblock,ndir+nshr), stateNew(nblock,nstatev),
     3 enerInternNew(nblock), enerInelasNew(nblock)
C
      character*80 cmname
C
C  局部变量
      integer i, j, k, nDirDim, nShem, nblock
      real*8 E, nu, lambda, twoMu, mu, bulkMod
      real*8 traceEps, stressRate(6), spin(3,3)
      real*8 stressRot(3,3), stressTemp(3,3)
      real*8 F(3,3), detF, J, FInv(3,3)
      real*8 C(6,6)
C
C-----------------------------------------------------------------------
C  读取材料参数
C-----------------------------------------------------------------------
      E        = props(1)    ! 杨氏模量
      nu       = props(2)    ! 泊松比
C
C-----------------------------------------------------------------------
C  计算弹性常数
C-----------------------------------------------------------------------
      mu       = E / (2.0D0*(1.0D0+nu))      ! 剪切模量
      twoMu    = 2.0D0*mu
      lambda   = E*nu / ((1.0D0+nu)*(1.0D0-2.0D0*nu))
      bulkMod  = lambda + twoMu/3.0D0
C
C-----------------------------------------------------------------------
C  组装弹性矩阵C（6x6）
C-----------------------------------------------------------------------
      do i = 1, 6
        do j = 1, 6
          C(i,j) = 0.0D0
        end do
      end do
C
      do i = 1, ndir
        do j = 1, ndir
          C(i,j) = lambda
        end do
        C(i,i) = lambda + twoMu
      end do
      do i = ndir+1, ndir+nshr
        C(i,i) = mu
      end do
C
C-----------------------------------------------------------------------
C  循环处理每个积分点
C-----------------------------------------------------------------------
      do k = 1, nblock
C
C       计算应力率
        do i = 1, ndir+nshr
          stressRate(i) = 0.0D0
          do j = 1, ndir+nshr
            stressRate(i) = stressRate(i) + C(i,j)*strainInc(k,j)
          end do
        end do
C
C       应力旋转（Jaumann率）
C       构建旋率张量
        if (nshr .eq. 1) then
          spin(1,2) = relSpinInc(k,1)
          spin(2,1) = -relSpinInc(k,1)
        else if (nshr .eq. 3) then
          spin(1,2) = relSpinInc(k,1)
          spin(1,3) = relSpinInc(k,2)
          spin(2,3) = relSpinInc(k,3)
          spin(2,1) = -relSpinInc(k,1)
          spin(3,1) = -relSpinInc(k,2)
          spin(3,2) = -relSpinInc(k,3)
        end if
        spin(1,1) = 0.0D0
        spin(2,2) = 0.0D0
        spin(3,3) = 0.0D0
C
C       将旧应力转换为3x3矩阵
        stressTemp(1,1) = stressOld(k,1)
        stressTemp(2,2) = stressOld(k,2)
        stressTemp(3,3) = stressOld(k,3)
        if (nshr .eq. 1) then
          stressTemp(1,2) = stressOld(k,4)
          stressTemp(2,1) = stressOld(k,4)
          stressTemp(1,3) = 0.0D0
          stressTemp(3,1) = 0.0D0
          stressTemp(2,3) = 0.0D0
          stressTemp(3,2) = 0.0D0
        else
          stressTemp(1,2) = stressOld(k,4)
          stressTemp(2,1) = stressOld(k,4)
          stressTemp(1,3) = stressOld(k,5)
          stressTemp(3,1) = stressOld(k,5)
          stressTemp(2,3) = stressOld(k,6)
          stressTemp(3,2) = stressOld(k,6)
        end if
C
C       计算旋转后的应力
        do i = 1, 3
          do j = 1, 3
            stressRot(i,j) = stressTemp(i,j)
            do i1 = 1, 3
              stressRot(i,j) = stressRot(i,j) 
     1                       + spin(i,i1)*stressTemp(i1,j)
     2                       - stressTemp(i,i1)*spin(i1,j)
            end do
          end do
        end do
C
C       更新应力
        stressNew(k,1) = stressRot(1,1) + stressRate(1)
        stressNew(k,2) = stressRot(2,2) + stressRate(2)
        stressNew(k,3) = stressRot(3,3) + stressRate(3)
        if (nshr .ge. 1) then
          stressNew(k,4) = stressRot(1,2) + stressRate(4)
        end if
        if (nshr .ge. 2) then
          stressNew(k,5) = stressRot(1,3) + stressRate(5)
          stressNew(k,6) = stressRot(2,3) + stressRate(6)
        end if
C
C       更新内能
        enerInternNew(k) = enerInternOld(k)
        do i = 1, ndir+nshr
          enerInternNew(k) = enerInternNew(k) 
     1                     + 0.5D0*(stressOld(k,i)+stressNew(k,i))
     2                     *strainInc(k,i)/density(k)
        end do
C
C       状态变量更新（如有）
        do i = 1, nstatev
          stateNew(k,i) = stateOld(k,i)
        end do
C
      end do  ! end k loop
C
      return
      end
```

## 输入文件示例

```abaqus
*Material, name=Elastic_VUMAT
*Density
7850.0
*User Material, constants=2
** E, NU
210.e9, 0.3
```

## 显式分析注意事项

1. **时间步长限制**：必须满足CFL条件
2. **沙漏控制**：一阶减缩积分单元需要沙漏控制
3. **能量平衡**：监控总能量（内能+动能+耗散能）
4. **接触设置**：显式分析的接触算法与隐式不同

## 稳定性检查

```fortran
C  计算波速（用于稳定性检查）
waveSpeed = sqrt((bulkMod + 4.0D0*mu/3.0D0)/density(k))
stableDt = charLength(k)/waveSpeed
```

## 扩展方向

- Johnson-Cook本构（应变率、温度效应）
- 损伤演化（失效模型）
- 状态方程（高压物理）

## 参考

- Abaqus User Subroutines Reference Guide
- Belytschko et al., "Nonlinear Finite Elements for Continua and Structures"
