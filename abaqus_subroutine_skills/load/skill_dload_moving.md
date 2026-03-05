# Abaqus DLOAD 移动载荷子程序技能

## 技能描述

本技能指导AI生成Abaqus Standard的分布载荷子程序DLOAD，实现移动载荷（如车轮、切削力、激光扫描等）。

## 适用场景

- 移动车轮载荷（桥梁、路面分析）
- 切削加工模拟
- 激光/电子束扫描加热
- 移动压力载荷

## 关键特性

| 特性 | 说明 |
|------|------|
| 分析类型 | 隐式/显式静态或动力学 |
| 载荷类型 | 分布压力、集中力等 |
| 运动方式 | 匀速/变速/沿路径移动 |
| 载荷分布 | 均匀/高斯分布/自定义 |

## DLOAD 接口定义

```fortran
SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
```

## 关键参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| F | 输出 | 载荷大小（压力为正）|
| TIME(1) | 输入 | 当前步时间 |
| TIME(2) | 输入 | 总时间 |
| COORDS(3) | 输入 | 积分点坐标 |
| NOEL | 输入 | 单元编号 |
| NPT | 输入 | 积分点编号 |
| JLTYP | 输入 | 载荷类型标识 |

## 移动载荷类型

### 1. 匀速直线移动

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  匀速直线移动载荷 - DLOAD
C  载荷沿X方向匀速移动
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, V, X0, X, T, LOAD_WIDTH, DIST
      REAL*8 GAUSS_CENTER, GAUSS_WIDTH, LOAD_SHAPE
C
C-----------------------------------------------------------------------
C  载荷参数（应通过PROPS或COMMON块传入）
C-----------------------------------------------------------------------
      F0 = 1000.0D0          ! 载荷峰值 (N/m² 或 N/m)
      V  = 10.0D0            ! 移动速度 (m/s)
      X0 = 0.0D0             ! 初始位置
      GAUSS_WIDTH = 0.1D0    ! 载荷分布宽度
C
C-----------------------------------------------------------------------
C  计算当前载荷中心位置
C-----------------------------------------------------------------------
      T = TIME(2)            ! 总时间
      GAUSS_CENTER = X0 + V * T
C
C-----------------------------------------------------------------------
C  计算到载荷中心的距离
C-----------------------------------------------------------------------
      X = COORDS(1)          ! 当前积分点X坐标
      DIST = X - GAUSS_CENTER
C
C-----------------------------------------------------------------------
C  高斯分布载荷
C-----------------------------------------------------------------------
      LOAD_SHAPE = EXP(-DIST*DIST / (2.0D0*GAUSS_WIDTH*GAUSS_WIDTH))
      F = F0 * LOAD_SHAPE
C
      RETURN
      END
```

### 2. 圆形移动载荷（旋转台）

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  圆周运动移动载荷
C  载荷在半径为R的圆周上匀速运动
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, R, OMEGA, T, THETA, X_CENTER, Y_CENTER
      REAL*8 X, Y, X_LOAD, Y_LOAD, DIST, LOAD_RADIUS
C
C-----------------------------------------------------------------------
C  载荷参数
C-----------------------------------------------------------------------
      F0 = 1000.0D0          ! 载荷峰值
      R = 1.0D0              ! 圆周半径
      OMEGA = 1.0D0          ! 角速度 (rad/s)
      X_CENTER = 0.0D0       ! 圆心X坐标
      Y_CENTER = 0.0D0       ! 圆心Y坐标
      LOAD_RADIUS = 0.05D0   ! 载荷作用半径
C
C-----------------------------------------------------------------------
C  计算载荷中心位置
C-----------------------------------------------------------------------
      T = TIME(2)
      THETA = OMEGA * T
      X_LOAD = X_CENTER + R * COS(THETA)
      Y_LOAD = Y_CENTER + R * SIN(THETA)
C
C-----------------------------------------------------------------------
C  计算到载荷中心的距离
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      DIST = SQRT((X-X_LOAD)**2 + (Y-Y_LOAD)**2)
C
C-----------------------------------------------------------------------
C  均匀圆盘载荷（在LOAD_RADIUS范围内）
C-----------------------------------------------------------------------
      IF (DIST .LE. LOAD_RADIUS) THEN
        F = F0
      ELSE
        F = 0.0D0
      END IF
C
      RETURN
      END
```

### 3. 沿曲线路径移动

```fortran
      SUBROUTINE DLOAD(F,KSTEP,KINC,TIME,NOEL,NPT,LAYER,KSPT,
     1 COORDS,JLTYP,SNAME)
C
C  沿曲线路径移动载荷
C  路径由节点坐标定义（从外部文件读取）
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C
      REAL*8 F0, V, T, S, TOTAL_PATH
      REAL*8 X, Y, Z, X_LOAD, Y_LOAD, Z_LOAD
      REAL*8 DIST, LOAD_SIZE
      INTEGER NSEG, ISEG, MAXSEG
      PARAMETER(MAXSEG=100)
C
C  路径节点（可从文件读取）
      REAL*8 PATH_X(MAXSEG), PATH_Y(MAXSEG), PATH_Z(MAXSEG)
      REAL*8 SEG_LEN(MAXSEG)
      COMMON /PATHDATA/ PATH_X, PATH_Y, PATH_Z, SEG_LEN, NSEG
C
C-----------------------------------------------------------------------
C  参数
C-----------------------------------------------------------------------
      F0 = 1000.0D0
      V = 5.0D0
      LOAD_SIZE = 0.02D0
      T = TIME(2)
C
C-----------------------------------------------------------------------
C  计算当前沿路径的弧长位置
C-----------------------------------------------------------------------
      S = V * T
      IF (S .GT. TOTAL_PATH) S = TOTAL_PATH
C
C-----------------------------------------------------------------------
C  确定当前线段
C-----------------------------------------------------------------------
      S_TEMP = 0.0D0
      ISEG = 1
      DO I = 1, NSEG-1
        IF (S .LE. S_TEMP + SEG_LEN(I)) THEN
          ISEG = I
          GOTO 100
        END IF
        S_TEMP = S_TEMP + SEG_LEN(I)
      END DO
      ISEG = NSEG - 1
100   CONTINUE
C
C-----------------------------------------------------------------------
C  在当前线段上线性插值求载荷位置
C-----------------------------------------------------------------------
      RATIO = (S - S_TEMP) / SEG_LEN(ISEG)
      X_LOAD = PATH_X(ISEG) + RATIO * (PATH_X(ISEG+1) - PATH_X(ISEG))
      Y_LOAD = PATH_Y(ISEG) + RATIO * (PATH_Y(ISEG+1) - PATH_Y(ISEG))
      Z_LOAD = PATH_Z(ISEG) + RATIO * (PATH_Z(ISEG+1) - PATH_Z(ISEG))
C
C-----------------------------------------------------------------------
C  计算距离并施加载荷
C-----------------------------------------------------------------------
      X = COORDS(1)
      Y = COORDS(2)
      Z = COORDS(3)
      DIST = SQRT((X-X_LOAD)**2 + (Y-Y_LOAD)**2 + (Z-Z_LOAD)**2)
C
      IF (DIST .LE. LOAD_SIZE) THEN
        F = F0 * (1.0D0 - DIST/LOAD_SIZE)  ! 线性衰减
      ELSE
        F = 0.0D0
      END IF
C
      RETURN
      END
```

## 输入文件示例

```abaqus
** 移动载荷定义
*Dload, amplitude=MoveLoad
Surface-1, P, 1.0
** 
** 需要配合振幅定义载荷时间历程
*Amplitude, name=MoveLoad, definition=USER
```

## 注意事项

1. **网格密度**：载荷移动区域需要足够密的网格
2. **时间步长**：显式分析中，载荷移动速度会影响稳定性
3. **平滑过渡**：建议使用高斯分布或余弦分布避免应力集中
4. **多载荷**：可通过JLTYPE区分多个移动载荷

## 与VDLOAD的区别

| 特性 | DLOAD (Standard) | VDLOAD (Explicit) |
|------|------------------|-------------------|
| 调用方式 | 每个积分点每次增量 | 每个积分点每时间步 |
| 块处理 | 否 | 是（向量化）|
| 适用分析 | 隐式 | 显式 |

## 扩展方向

- 多轮车载荷叠加
- 随机不平度路面
- 热源移动（与热分析耦合）
- 变载荷幅值（制动/加速过程）

## 参考

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 34.4
