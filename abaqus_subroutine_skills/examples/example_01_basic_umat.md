# 示例1: 基础UMAT - 线弹性材料验证

## 示例概述

本示例演示如何创建和使用最简单的UMAT子程序——各向同性线弹性材料。这个示例适合初学者验证UMAT接口是否正确工作。

## 学习目标

1. 理解UMAT的基本结构
2. 掌握Fortran固定格式编码规则
3. 学会编译和链接子程序
4. 验证UMAT结果与内置材料的一致性

## 文件结构

```
example_01/
├── umat_elastic.f       # UMAT源代码
├── job_elastic.inp      # Abaqus输入文件
├── verify_results.py    # 结果验证脚本
└── README.md            # 说明文档
```

## 完整Fortran代码

```fortran
C=======================================================================
C  Example 1: Linear Elastic UMAT
C  最简单的UMAT实现 - 各向同性线弹性材料
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
      REAL*8 E, NU, LAMBDA, G, FAC
      INTEGER I, J
C-----------------------------------------------------------------------
C  材料参数读取
C-----------------------------------------------------------------------
      E  = PROPS(1)    ! 杨氏模量 (MPa)
      NU = PROPS(2)    ! 泊松比
C-----------------------------------------------------------------------
C  计算拉梅常数
C-----------------------------------------------------------------------
      LAMBDA = E*NU / ((1.0D0+NU)*(1.0D0-2.0D0*NU))
      G      = E / (2.0D0*(1.0D0+NU))
      FAC    = LAMBDA + 2.0D0*G
C-----------------------------------------------------------------------
C  初始化雅可比矩阵
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          DDSDDE(I,J) = 0.0D0
        END DO
      END DO
C-----------------------------------------------------------------------
C  组装3D弹性矩阵
C-----------------------------------------------------------------------
      IF (NDI .EQ. 3) THEN
        DDSDDE(1,1) = FAC
        DDSDDE(2,2) = FAC
        DDSDDE(3,3) = FAC
        DDSDDE(1,2) = LAMBDA
        DDSDDE(1,3) = LAMBDA
        DDSDDE(2,1) = LAMBDA
        DDSDDE(2,3) = LAMBDA
        DDSDDE(3,1) = LAMBDA
        DDSDDE(3,2) = LAMBDA
        DDSDDE(4,4) = G
        DDSDDE(5,5) = G
        DDSDDE(6,6) = G
      ELSE IF (NDI .EQ. 2) THEN
C       平面应变
        DDSDDE(1,1) = FAC
        DDSDDE(2,2) = FAC
        DDSDDE(1,2) = LAMBDA
        DDSDDE(2,1) = LAMBDA
        DDSDDE(3,3) = G
      END IF
C-----------------------------------------------------------------------
C  应力更新
C-----------------------------------------------------------------------
      DO I = 1, NTENS
        DO J = 1, NTENS
          STRESS(I) = STRESS(I) + DDSDDE(I,J)*DSTRAN(J)
        END DO
      END DO
C-----------------------------------------------------------------------
C  应变能计算
C-----------------------------------------------------------------------
      SSE = 0.0D0
      DO I = 1, NTENS
        SSE = SSE + STRESS(I)*(STRAN(I)+0.5D0*DSTRAN(I))
      END DO
      SSE = 0.5D0*SSE
C-----------------------------------------------------------------------
      RETURN
      END
C=======================================================================
```

## Abaqus输入文件

```abaqus
*Heading
** 示例1: 线弹性UMAT验证
*Preprint, echo=NO, model=NO, history=NO, contact=NO
**
*Node
1, 0.0, 0.0, 0.0
2, 1.0, 0.0, 0.0
3, 1.0, 1.0, 0.0
4, 0.0, 1.0, 0.0
5, 0.0, 0.0, 1.0
6, 1.0, 0.0, 1.0
7, 1.0, 1.0, 1.0
8, 0.0, 1.0, 1.0
**
*Element, type=C3D8R, elset=Solid
1, 1, 2, 3, 4, 5, 6, 7, 8
**
*Solid section, elset=Solid, material=Elastic_UMAT
**
*Material, name=Elastic_UMAT
*User material, constants=2
** PROPS(1)=E, PROPS(2)=NU
210000.0, 0.3
*Depvar
1
**
*Boundary
1, 1, 3, 0.0
2, 2, 3, 0.0
4, 1, 1, 0.0
4, 3, 3, 0.0
5, 1, 2, 0.0
8, 2, 3, 0.0
**
*Step, name=Loading, nlgeom=NO
*Static
1.0, 1.0, 1.0e-5, 1.0
**
*Dload
1, P2, -100.0
**
*Output, field
*Node output
U, RF
*Element output
S, E, SDV
*Output, history
*End step
```

## 编译和运行

### 1. 编译命令

```bash
# Windows (Intel Fortran)
abaqus make library=umat_elastic.f

# 或在作业提交时编译
abaqus job=job_elastic user=umat_elastic.f
```

### 2. 运行分析

```bash
abaqus job=job_elastic user=umat_elastic.f interactive
```

## 结果验证

### 理论解

单轴拉伸（σ_x = 100 MPa）：
- ε_x = σ_x / E = 100 / 210000 = 4.76e-4
- ε_y = ε_z = -ν * ε_x = -1.43e-4

### 验证检查清单

| 检查项 | 期望值 | 容差 |
|--------|--------|------|
| σ_xx | 100.0 MPa | < 0.1% |
| ε_xx | 4.76e-4 | < 0.1% |
| σ_yy | 0.0 MPa | < 1.0 MPa |
| 位移U2 | 4.76e-4 m | < 0.1% |

## 常见问题

### 1. 编译错误 "Unexpected end of file"

**原因**: Fortran固定格式要求第6列为续行符

**解决**: 确保续行行的第6列有字符（如`1`）

### 2. 结果为零

**原因**: 未正确更新应力或雅可比矩阵

**解决**: 检查`STRESS(I) = STRESS(I) + ...`语句

### 3. 与内置材料结果不一致

**原因**: 平面应力/平面应变处理不正确

**解决**: 确认`NDI`的值并正确处理

## 扩展练习

1. 修改代码实现平面应力条件
2. 添加温度相关弹性模量
3. 实现正交各向异性弹性

## 参考

- Abaqus User Subroutines Reference Guide
- 本技能库: `material/skill_umat_elastic.md`
