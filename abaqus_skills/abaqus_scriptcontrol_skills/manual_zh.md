# Abaqus 技能语料库使用手册

## 目录

1. [总体功能介绍](#一总体功能介绍)
2. [使用方法](#二使用方法)
3. [技能模块说明](#三技能模块说明)
4. [示例教程](#四示例教程)

---

## 一、总体功能介绍

### 1.1 什么是 Abaqus 技能语料库？

Abaqus 技能语料库是一套结构化的 Abaqus 二次开发知识库，旨在帮助用户和 AI 助手快速生成高质量、可运行的 Abaqus Python 脚本。通过模块化的技能文件，用户可以用自然语言描述分析需求，AI 自动组合相应的技能模块生成完整代码。

### 1.2 核心功能

| 功能模块 | 描述 | 包含技能 |
|---------|------|---------|
| **通用技能** | 所有分析类型的基础操作 | 建模、材料、边界条件、网格、作业提交等 |
| **静力分析** | 静态载荷下的结构响应 | 线弹性分析、大变形/塑性分析 |
| **疲劳分析** | 循环载荷下的寿命预测 | 高周疲劳（S-N曲线）、损伤累积 |
| **XFEM 分析** | 裂纹萌生和扩展模拟 | 扩展有限元方法、损伤演化 |
| **热分析** | 温度场和热应力计算 | 稳态/瞬态热传导、热-力耦合 |
| **复合材料** | 层合板结构分析 | 铺层定义、失效准则 |

### 1.3 适用对象

- **工程师**：快速生成标准分析脚本，减少重复劳动
- **研究人员**：作为复杂分析的起点模板
- **学生**：学习 Abaqus 脚本编程的最佳实践
- **AI 助手**：提供结构化的知识库以生成准确代码

### 1.4 主要优势

1. **模块化设计**：技能可自由组合，适应不同分析需求
2. **即用即取**：每个技能文件包含可直接运行的代码模板
3. **最佳实践**：遵循 Abaqus 官方推荐的建模流程和参数设置
4. **错误预防**：包含常见错误提示和解决方案
5. **渐进学习**：从简单到复杂的示例帮助用户逐步掌握

---

## 二、使用方法

### 2.1 与 AI 助手配合使用

#### 步骤 1：描述需求

用自然语言描述你的分析需求，例如：

> "我需要分析一个悬臂梁在端部载荷下的应力和变形，梁长 1 米，截面是 50mm x 100mm 的矩形，材料是 Q235 钢，端部载荷 5000N。"

#### 步骤 2：AI 澄清

AI 会根据技能库中的 `prompts/ai_guide.md` 指导，通过简洁的对话确认关键信息：

> 确认几个问题：
> 1. 分析类型是线弹性静力分析吗？
> 2. 需要多大的网格密度？
> 3. 结果需要保存哪些变量？

#### 步骤 3：生成脚本

AI 根据确认的需求，从技能库中提取相应模块组合成完整脚本：

- 从 [`general/SKILL.md`](general/SKILL.md) 获取建模代码
- 从 [`general/reference/material.md`](general/reference/material.md) 获取材料定义
- 从 [`static/SKILL.md`](static/SKILL.md) 获取静力分析设置

#### 步骤 4：运行验证

将生成的脚本保存为 `.py` 文件，在 Abaqus 中运行：

```
文件 → 运行脚本 → 选择脚本文件
```

### 2.2 直接使用技能文件

#### 方法 A：复制代码模板

1. 打开对应技能的 SKILL.md 文件（如 [`general/SKILL.md`](general/SKILL.md)）
2. 找到所需功能模块
3. 查看详细文档 [`reference/`](general/reference/) 目录中的代码模板
4. 复制到脚本中并修改参数

#### 方法 B：组合多个技能

```python
# 导入 Abaqus 模块
from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 建模（引用 general/reference/modeling.md）==========
# ... 复制建模代码 ...

# ========== 2. 材料（引用 general/reference/material.md）==========
# ... 复制材料代码 ...

# ========== 3. 分析步（引用 general/reference/step.md）==========
# ... 复制分析步代码 ...

# ... 其他步骤 ...
```

### 2.3 文件查找速查表

| 想做什么 | 查看文件 |
|---------|---------|
| 创建几何模型 | [`general/SKILL.md`](general/SKILL.md) → [`reference/modeling.md`](general/reference/modeling.md) |
| 定义材料属性 | [`general/SKILL.md`](general/SKILL.md) → [`reference/material.md`](general/reference/material.md) |
| 设置分析步和输出 | [`general/SKILL.md`](general/SKILL.md) → [`reference/step.md`](general/reference/step.md) |
| 施加边界条件和载荷 | [`general/SKILL.md`](general/SKILL.md) → [`reference/bc_load.md`](general/reference/bc_load.md) |
| 划分网格 | [`general/SKILL.md`](general/SKILL.md) → [`reference/mesh.md`](general/reference/mesh.md) |
| 提交计算作业 | [`general/SKILL.md`](general/SKILL.md) → [`reference/job.md`](general/reference/job.md) |
| 静力分析（线性） | [`static/SKILL.md`](static/SKILL.md) → [`reference/linear.md`](static/reference/linear.md) |
| 静力分析（非线性） | [`static/SKILL.md`](static/SKILL.md) → [`reference/nonlinear.md`](static/reference/nonlinear.md) |
| 疲劳分析 | [`fatigue/SKILL.md`](fatigue/SKILL.md) |
| 裂纹分析（XFEM） | [`xfem/SKILL.md`](xfem/SKILL.md) |
| 热应力分析 | [`thermal/SKILL.md`](thermal/SKILL.md) |
| 复合材料分析 | [`composite/SKILL.md`](composite/SKILL.md) |

### 2.4 常用参数速查

#### 单位制

| 物理量 | N-mm-MPa 制 |
|-------|-------------|
| 长度 | mm |
| 力 | N |
| 应力 | MPa |
| 弹性模量 | MPa |
| 密度 | tonne/mm³ |
| 重力加速度 | 9800 mm/s² |

#### 材料参数（常用）

| 材料 | E (MPa) | ν | 密度 (tonne/mm³) | 屈服强度 (MPa) |
|------|---------|---|------------------|----------------|
| Q235 钢 | 210000 | 0.3 | 7.85e-09 | 235 |
| Q345 钢 | 210000 | 0.3 | 7.85e-09 | 345 |
| 铝合金 6061 | 69000 | 0.33 | 2.70e-09 | 276 |

---

## 三、技能模块说明

### 3.1 通用技能 (general/)

通用技能是所有分析类型的基础，包括：

- **几何建模** ([`modeling.md`](general/reference/modeling.md))：创建部件、草图绘制、特征操作
- **材料定义** ([`material.md`](general/reference/material.md))：弹性、塑性、超弹性材料
- **分析步设置** ([`step.md`](general/reference/step.md))：静力、动力、热分析步
- **边界条件与载荷** ([`bc_load.md`](general/reference/bc_load.md))：位移约束、力、压力、温度载荷
- **网格划分** ([`mesh.md`](general/reference/mesh.md))：单元类型选择、网格控制
- **作业提交** ([`job.md`](general/reference/job.md))：作业创建、提交、监控

### 3.2 静力分析 (static/)

- **线性静力分析** ([`linear.md`](static/reference/linear.md))：小变形、线弹性
- **非线性静力分析** ([`nonlinear.md`](static/reference/nonlinear.md))：大变形、塑性、接触

### 3.3 疲劳分析 (fatigue/)

- **高周疲劳**：基于 S-N 曲线的寿命预测

### 3.4 XFEM 裂纹分析 (xfem/)

- **裂纹萌生和扩展**：扩展有限元方法、损伤准则

### 3.5 热应力分析 (thermal/)

- **热应力分析**：稳态/瞬态热传导、热-力耦合

### 3.6 复合材料分析 (composite/)

- **层合板分析**：铺层定义、Hashin 失效准则

---

## 四、示例教程

### 示例 1：简单悬臂梁分析（入门）

**难度**：⭐（简单）  
**目标**：掌握最基本的分析流程  
**涉及技能**：建模 → 材料 → 边界条件 → 载荷 → 网格 → 作业

#### 场景描述

一根矩形截面悬臂梁，固定端完全约束，自由端施加垂直向下的集中力，计算应力和变形。

#### 关键参数

- 梁长：1000 mm
- 截面：50 mm × 100 mm
- 材料：Q235 钢
- 载荷：5000 N

#### 完整脚本

```python
# -*- coding: utf-8 -*-
"""
示例 1: 简单悬臂梁分析（入门）
分析类型: 线弹性静力分析
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 参数定义 ==========
length = 1000.0      # mm
width = 50.0         # mm
height = 100.0       # mm

E = 210000.0         # MPa
nu = 0.3

load = 5000.0        # N

# ========== 创建模型 ==========
model = mdb.Model(name='Cantilever-Beam')

# 创建梁（拉伸）
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(width, height))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=length)
del model.sketches['__profile__']

# ========== 材料和截面 ==========
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
section = model.HomogeneousSolidSection(name='Section', material='Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section')

# ========== 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 分析步 ==========
model.StaticStep(name='Load-Step', previous='Initial', nlgeom=OFF)

# ========== 边界条件（固定端）==========
fixed_face = instance.faces.findAt(((width/2, height/2, 0.0),))
region = assembly.Set(name='Fixed', faces=fixed_face)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=region)

# ========== 载荷（自由端集中力）==========
load_face = instance.faces.findAt(((width/2, height/2, length),))
region = assembly.Set(name='Load', faces=load_face)
model.ConcentratedForce(name='Force', createStepName='Load-Step',
                        region=region, cf2=-load)

# ========== 网格 ==========
part.seedPart(size=20.0)
part.setMeshControls(regions=(part.cells,), elemShape=HEX)
elem_type = mesh.ElemType(elemCode=C3D8R)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 作业 ==========
job = mdb.Job(name='Beam-Job', model='Cantilever-Beam')
job.submit()
job.waitForCompletion()

print("分析完成！")
```

#### 理论验证

- 最大弯曲应力（理论）：σ = M·y/I = 30 MPa
- 最大挠度（理论）：δ = FL³/(3EI) = 2.86 mm
- 与有限元结果对比，误差应 < 5%

---

### 示例 2：带孔板的应力集中分析（进阶）

**难度**：⭐⭐（中等）  
**目标**：学习局部网格加密、结果后处理  
**涉及技能**：几何切割 → 局部加密 → 应力提取 → 理论对比

详见 [examples/example_pressure_vessel.md](examples/example_pressure_vessel.md)

---

### 示例 3：压力容器热应力耦合分析（高级）

**难度**：⭐⭐⭐（困难）  
**目标**：掌握多物理场耦合分析、顺序耦合方法  
**涉及技能**：热传导 → 温度场传递 → 热应力 → 结果对比

详见 [thermal/SKILL.md](thermal/SKILL.md)

---

## 五、CLI Code Skill 格式说明

本技能库按照 Claude Code 的 Skill 格式组织：

### 目录结构

每个技能分类包含：

- **SKILL.md**：技能的主文件，包含：
  - 技能概述
  - 功能列表（每个功能对应 reference 中的详细文档）
  - 代码片段
  - 快速参考

- **reference/**：详细参考文档目录，包含：
  - 完整的 API 参考
  - 详细的代码模板
  - 最佳实践
  - 常见错误及解决方案

### 使用建议

1. 首先查看 SKILL.md 了解技能的整体功能和结构
2. 根据需要深入查看 reference 目录中的详细文档
3. 复制代码模板并根据具体需求修改参数
4. 遵循最佳实践，避免常见错误
