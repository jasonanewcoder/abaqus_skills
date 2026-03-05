# Abaqus子程序技能库使用说明

## 目录

1. [总体功能介绍](#总体功能介绍)
2. [技能库结构](#技能库结构)
3. [使用方法](#使用方法)
4. [示例教程](#示例教程)
5. [最佳实践](#最佳实践)
6. [故障排除](#故障排除)

---

## 总体功能介绍

### 什么是Abaqus子程序技能库？

本技能库是一套专门针对Abaqus用户子程序开发的AI辅助编程指南。它提供了标准化的Fortran代码模板、详细的理论说明和完整的工程示例，帮助用户快速、准确地开发自定义子程序。

### 技能库覆盖范围

| 子程序类型 | 功能 | 分析类型 |
|------------|------|----------|
| UMAT | 自定义材料本构 | Standard（隐式）|
| VUMAT | 自定义材料本构 | Explicit（显式）|
| DLOAD | 分布载荷定义 | Standard |
| VDLOAD | 分布载荷定义 | Explicit |
| DISP | 自定义位移边界 | Standard |
| VDISP | 自定义位移边界 | Explicit |
| USDFLD | 自定义场变量 | 通用 |
| SIGINI | 初始应力定义 | 通用 |
| SDVINI | 初始状态变量 | 通用 |
| FRIC | 自定义摩擦 | Standard |
| VRIC | 自定义摩擦 | Explicit |
| HETVAL | 热生成 | 热分析 |
| FILM | 自定义对流 | 热分析 |
| UEL | 自定义单元 | Standard |
| VUEL | 自定义单元 | Explicit |

### 技能库特点

1. **合法性保证**：所有代码严格遵循Abaqus子程序接口规范
2. **正确性验证**：每个模板都经过理论验证和数值测试
3. **分层设计**：从入门到高级，循序渐进
4. **即用即走**：代码可直接复制使用，仅需修改参数
5. **理论支撑**：包含完整的数学公式和物理背景

---

## 技能库结构

```
abaqus_subroutine_skills/
├── material/              # 材料本构子程序
│   ├── skill_umat_elastic.md      # 线弹性UMAT
│   ├── skill_umat_plasticity.md   # 弹塑性UMAT
│   └── skill_vumat_elastic.md     # 线弹性VUMAT
├── load/                  # 载荷子程序
│   └── skill_dload_moving.md      # 移动载荷
├── boundary/              # 边界条件子程序
│   └── skill_disp_control.md      # 自定义位移
├── field/                 # 场变量子程序
│   └── skill_usdfld_spatial.md    # 空间场变量
├── initial/               # 初始条件子程序
│   └── skill_sigini_stress.md     # 初始应力
├── thermal/               # 热分析子程序
│   └── skill_hetval_heat.md       # 热生成
├── friction/              # 摩擦子程序
│   └── skill_fric_contact.md      # 自定义摩擦
├── element/               # 自定义单元
│   └── skill_uel_spring.md        # 非线性弹簧
├── examples/              # 完整示例
│   ├── example_01_basic_umat.md   # 基础UMAT
│   ├── example_02_dload_moving.md # 移动载荷
│   └── example_03_coupled_analysis.md # 耦合分析
└── manual.md              # 本使用说明
```

---

## 使用方法

### 第一步：确定需求

在使用技能库之前，请明确以下问题：

1. **分析类型**：隐式(Standard)还是显式(Explicit)？
2. **物理现象**：需要模拟什么材料行为或边界条件？
3. **耦合需求**：是否需要多个子程序协同工作？
4. **复杂程度**：线性问题还是高度非线性？

### 第二步：选择技能文件

根据需求选择对应的技能文件：

| 您的需求 | 推荐技能文件 |
|----------|--------------|
| 自定义材料模型 | `material/skill_umat_*.md` |
| 移动/变化载荷 | `load/skill_dload_moving.md` |
| 振动/位移控制 | `boundary/skill_disp_control.md` |
| 空间非均匀材料 | `field/skill_usdfld_spatial.md` |
| 地应力/残余应力 | `initial/skill_sigini_stress.md` |
| 摩擦学问题 | `friction/skill_fric_contact.md` |
| 热-力耦合 | `thermal/skill_hetval_heat.md` + UMAT |
| 特殊连接单元 | `element/skill_uel_spring.md` |

### 第三步：阅读技能文件

每个技能文件包含以下部分：

1. **技能描述**：适用场景和主要功能
2. **理论公式**：数学基础和物理模型
3. **接口定义**：子程序参数详细说明
4. **代码模板**：完整、可直接使用的Fortran代码
5. **输入文件示例**：Abaqus关键字参考
6. **验证方法**：如何确认实现正确
7. **扩展建议**：进一步开发的方向

### 第四步：修改和适配

根据您的具体问题修改代码：

```fortran
C  修改材料参数区域
C-----------------------------------------------------------------------
C  读取材料参数
C-----------------------------------------------------------------------
      E  = PROPS(1)    ! 修改为您的参数名
      NU = PROPS(2)
      YOUR_PARAM = PROPS(3)  ! 添加新参数
```

### 第五步：编译和测试

#### 编译命令

```bash
# Windows环境
abaqus make library=your_subroutine.f

# 或直接运行作业
abaqus job=your_job user=your_subroutine.f interactive
```

#### 测试建议

1. **单单元测试**：验证本构关系正确性
2. **简单边界条件测试**：验证子程序被正确调用
3. **与基准解对比**：验证数值精度
4. **收敛性测试**：验证雅可比矩阵正确性

### 第六步：调试和优化

#### 常见调试方法

```fortran
C  添加调试输出（注意：会影响性能）
      WRITE(*,*) 'DEBUG: NOEL=', NOEL, ' STRESS=', STRESS(1)
```

#### 使用Abaqus/Viewer检查结果

```python
# Python脚本检查状态变量
from odbAccess import openOdb
odb = openOdb(path='your_job.odb')
lastFrame = odb.steps['your_step'].frames[-1]
sdv = lastFrame.fieldOutputs['SDV1']
print('Max SDV1:', max([v.data for v in sdv.values]))
```

---

## 示例教程

### 示例1：线弹性UMAT（入门）

**目标**：创建最简单的UMAT，验证接口正确性

**文件**：`examples/example_01_basic_umat.md`

**适用对象**：首次使用Abaqus子程序的用户

**关键学习点**：
- UMAT接口结构
- Fortran固定格式规则
- 雅可比矩阵组装
- 应力更新算法

**预期结果**：与Abaqus内置弹性材料结果一致

**难度**：★☆☆☆☆

### 示例2：移动车轮载荷（中级）

**目标**：模拟车辆在桥面上的移动载荷

**文件**：`examples/example_02_dload_moving.md`

**适用对象**：需要模拟移动载荷的工程师

**关键学习点**：
- DLOAD子程序工作机制
- 时间和坐标的综合使用
- 空间分布载荷定义
- 动态分析设置

**预期结果**：桥面产生随车辆位置变化的动态响应

**难度**：★★★☆☆

### 示例3：热-力耦合分析（高级）

**目标**：实现复合材料固化过程的多物理场耦合

**文件**：`examples/example_03_coupled_analysis.md`

**适用对象**：需要进行多物理场耦合分析的研究人员

**关键学习点**：
- 多个子程序的协同工作
- 状态变量在子程序间的传递
- 热-力耦合分析设置
- 复杂物理过程模拟

**预期结果**：得到温度、固化度、应力场的耦合演化

**难度**：★★★★★

---

## 最佳实践

### 代码编写规范

1. **使用固定格式Fortran**：
   - 第1-5列：语句标号
   - 第6列：续行符（非零字符）
   - 第7-72列：代码主体
   - 第73列后：被忽略

2. **变量声明**：
```fortran
      REAL*8 E, NU, STRESS(6)    ! 使用REAL*8而非REAL
      INTEGER I, J, NDI          ! 显式声明所有变量
```

3. **常数定义**：
```fortran
      REAL*8 PI
      PARAMETER(PI=3.141592653589793D0)  ! 使用D0表示双精度
```

4. **错误检查**：
```fortran
C  参数范围检查
      IF (E .LE. 0.0D0) THEN
        WRITE(*,*) 'ERROR: Young modulus must be positive'
        CALL XIT    ! 终止分析
      END IF
```

### 性能优化

1. **向量化显式子程序**：
   - VUMAT/VUEL使用块循环
   - 避免标量操作

2. **减少状态变量**：
   - 只存储必要的历史变量
   - 及时清理无用变量

3. **优化矩阵运算**：
   - 利用矩阵对称性
   - 避免重复计算

### 子程序选择指南

| 问题类型 | 推荐方案 | 备选方案 |
|----------|----------|----------|
| 新本构模型 | UMAT/VUMAT | 内置材料+场变量 |
| 移动载荷 | DLOAD/VDLOAD | 多节点集中力 |
| 复杂边界 | DISP/VDISP | MPC约束 |
| 非均匀材料 | USDFLD+UMAT | 多层材料 |
| 初始应力 | SIGINI | *Initial Conditions |
| 特殊单元 | UEL/VUEL | 多节点连接器 |

---

## 故障排除

### 编译错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| "Unexpected end of file" | 续行格式错误 | 检查第6列续行符 |
| "Undefined variable" | 变量未声明 | 添加类型声明 |
| "Type mismatch" | 类型不一致 | 使用REAL*8而非REAL |
| "Dimension mismatch" | 数组维数错误 | 检查数组声明和访问 |

### 运行时错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| "Too many attempts" | 不收敛 | 检查雅可比矩阵 |
| "Negative eigenvalues" | 刚度矩阵不正定 | 检查材料稳定性 |
| "Zero pivot" | 约束不足 | 检查边界条件 |
| "NaN in stress" | 数值溢出 | 检查除零和指数运算 |

### 结果异常

| 现象 | 可能原因 | 检查点 |
|------|----------|--------|
| 应力为零 | 未更新STRESS | 检查应力更新语句 |
| 位移过大 | 刚度太小 | 检查材料参数单位 |
| 不收敛 | 雅可比不一致 | 验证DDSDDE推导 |
| 沙漏模态 | 减缩积分 | 添加沙漏控制 |

### 调试技巧

1. **输出中间结果**：
```fortran
      IF (NOEL .EQ. 1 .AND. NPT .EQ. 1) THEN
        WRITE(*,*) 'Step:', KSTEP, 'Inc:', KINC
        WRITE(*,*) 'Stress:', (STRESS(I), I=1,6)
      END IF
```

2. **单步分析**：
```abaqus
*Step, name=Debug
*Static
1.0, 1.0, 1.0e-5, 1.0
```

3. **对比测试**：
   - 与内置材料对比
   - 与理论解对比
   - 与文献结果对比

---

## 参考资源

### Abaqus官方文档

- Abaqus User Subroutines Reference Guide
- Abaqus Analysis User's Guide, Section 26
- Abaqus Example Problems Guide

### 推荐书籍

1. Simo & Hughes, "Computational Inelasticity"
2. Dunne & Petrinic, "Introduction to Computational Plasticity"
3. Belytschko et al., "Nonlinear Finite Elements"

### 在线资源

- Abaqus Learning Community
- SIMULIA Knowledge Base
- 本技能库GitHub仓库

---

## 版本信息

- 技能库版本：1.0
- 适用Abaqus版本：2020及以上
- Fortran编译器：Intel Fortran 19.0+ 或 GNU Fortran 9.0+
- 最后更新：2026-03-04

---

## 贡献和反馈

欢迎通过以下方式贡献：
- 提交新的技能文件
- 报告代码错误
- 提供改进建议
- 分享使用经验

---

**注意**：使用本技能库前请确保您已熟悉Abaqus基本操作和Fortran编程基础。对于复杂问题，建议先在小规模模型上验证子程序正确性。
