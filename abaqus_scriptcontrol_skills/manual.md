# Abaqus 技能语料库使用手册

## 📖 目录

1. [总体功能介绍](#一总体功能介绍)
2. [使用方法](#二使用方法)
3. [示例教程](#三示例教程)
   - [示例 1：简单悬臂梁分析（入门）](#示例1-简单悬臂梁分析入门)
   - [示例 2：带孔板的应力集中分析（进阶）](#示例2-带孔板的应力集中分析进阶)
   - [示例 3：压力容器热应力耦合分析（高级）](#示例3-压力容器热应力耦合分析高级)

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
| **复合材料** | 层合板结构分析 | 铺层定义、失效准则、渐进损伤 |

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
- 从 `general/skill_modeling.md` 获取建模代码
- 从 `general/skill_material.md` 获取材料定义
- 从 `static/skill_static_linear.md` 获取静力分析设置

#### 步骤 4：运行验证
将生成的脚本保存为 `.py` 文件，在 Abaqus 中运行：
```
文件 → 运行脚本 → 选择脚本文件
```

### 2.2 直接使用技能文件

#### 方法 A：复制代码模板
1. 打开对应技能文件（如 `general/skill_modeling.md`）
2. 找到所需代码模板（如"长方体"模板）
3. 复制到脚本中并修改参数

#### 方法 B：组合多个技能
```python
# 导入 Abaqus 模块
from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 建模（引用 skill_modeling.md）==========
# ... 复制建模代码 ...

# ========== 2. 材料（引用 skill_material.md）==========
# ... 复制材料代码 ...

# ========== 3. 分析步（引用 skill_step.md）==========
# ... 复制分析步代码 ...

# ... 其他步骤 ...
```

### 2.3 文件查找速查表

| 想做什么 | 查看文件 |
|---------|---------|
| 创建几何模型 | `general/skill_modeling.md` |
| 定义材料属性 | `general/skill_material.md` |
| 设置分析步和输出 | `general/skill_step.md` |
| 施加边界条件和载荷 | `general/skill_bc_load.md` |
| 划分网格 | `general/skill_mesh.md` |
| 提交计算作业 | `general/skill_job.md` |
| 静力分析（线性） | `static/skill_static_linear.md` |
| 静力分析（非线性） | `static/skill_static_nl.md` |
| 疲劳分析 | `fatigue/skill_fatigue_high_cycle.md` |
| 裂纹分析（XFEM） | `xfem/skill_xfem_crack.md` |
| 热应力分析 | `thermal/skill_thermal_stress.md` |
| 复合材料分析 | `composite/skill_composite_shell.md` |

### 2.4 常用参数速查

#### 单位制
| 物理量 | N-mm-MPa 制 | N-m-Pa 制 |
|-------|-------------|-----------|
| 长度 | mm | m |
| 力 | N | N |
| 应力 | MPa (N/mm²) | Pa (N/m²) |
| 弹性模量 | MPa | Pa |
| 密度 | tonne/mm³ | kg/m³ |
| 重力加速度 | 9800 mm/s² | 9.8 m/s² |

#### 材料参数（常用）
| 材料 | E (MPa) | ν | 密度 (tonne/mm³) | 屈服强度 (MPa) |
|------|---------|---|------------------|----------------|
| Q235 钢 | 210000 | 0.3 | 7.85e-09 | 235 |
| Q345 钢 | 210000 | 0.3 | 7.85e-09 | 345 |
| 铝合金 6061 | 69000 | 0.33 | 2.70e-09 | 276 |

---

## 三、示例教程

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

#### 场景描述
一块带中心圆孔的平板承受单向拉伸载荷，分析孔边应力集中现象。

#### 关键参数
- 板尺寸：200 mm × 100 mm × 5 mm
- 孔径：20 mm
- 材料：铝合金 6061
- 拉伸载荷：100 MPa

#### 完整脚本

```python
# -*- coding: utf-8 -*-
"""
示例 2: 带孔板的应力集中分析（进阶）
分析类型: 线弹性静力分析 + 局部网格加密
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 参数定义 ==========
plate_length = 200.0
plate_width = 100.0
plate_thickness = 5.0
hole_radius = 10.0

E = 69000.0          # 铝合金
nu = 0.33

applied_stress = 100.0   # MPa

# ========== 创建模型 ==========
model = mdb.Model(name='Plate-with-Hole')

# 创建带孔平板
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
sketch.CircleByCenterPerimeter(center=(plate_length/2, plate_width/2), 
                                point1=(plate_length/2 + hole_radius, plate_width/2))
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del model.sketches['__profile__']

# ========== 材料 ==========
material = model.Material(name='Al-6061')
material.Elastic(table=((E, nu),))
section = model.HomogeneousSolidSection(name='Section', material='Al-6061')
part.SectionAssignment(region=(part.cells,), sectionName='Section')

# ========== 装配和对称约束 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

model.StaticStep(name='Tension', previous='Initial', nlgeom=OFF)

# 利用对称性（1/4模型）
# X-Z 平面
faces_xz = instance.faces.getByBoundingBox(yMin=-0.1, yMax=0.1)
region = assembly.Set(name='Sym-XZ', faces=faces_xz)
model.DisplacementBC(name='BC-Sym1', createStepName='Initial', 
                     region=region, u2=0.0, ur1=0.0, ur3=0.0)

# Y-Z 平面  
faces_yz = instance.faces.getByBoundingBox(xMin=plate_length/2-0.1, 
                                           xMax=plate_length/2+0.1)
region = assembly.Set(name='Sym-YZ', faces=faces_yz)
model.DisplacementBC(name='BC-Sym2', createStepName='Initial',
                     region=region, u1=0.0, ur2=0.0, ur3=0.0)

# ========== 载荷 ==========
load_face = instance.faces.getByBoundingBox(xMin=-0.1, xMax=0.1)
region = assembly.Set(name='Load', faces=load_face)
total_force = applied_stress * plate_width * plate_thickness / 2  # 1/4模型
model.ConcentratedForce(name='Tension', createStepName='Tension',
                        region=region, cf1=-total_force)

# ========== 网格（局部加密）==========
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=FREE)

# 全局网格
part.seedPart(size=5.0)

# 孔边局部加密
hole_edges = part.edges.getByBoundingCylinder(
    center1=(plate_length/2, plate_width/2, 0),
    center2=(plate_length/2, plate_width/2, plate_thickness),
    radius=hole_radius*1.5
)
part.seedEdgeBySize(edges=hole_edges, size=0.5, constraint=FINER)

# 二阶单元提高精度
elem_type = mesh.ElemType(elemCode=C3D10)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 作业和后处理 ==========
job = mdb.Job(name='Plate-Job', model='Plate-with-Hole')
job.submit()
job.waitForCompletion()

# 后处理
from odbAccess import openOdb
odb = openOdb(path='Plate-Job.odb')
frame = odb.steps['Tension'].frames[-1]
stress = frame.fieldOutputs['S']

max_stress = max([v.mises for v in stress.values])
print(f"最大Mises应力: {max_stress:.2f} MPa")

# 应力集中系数
Kt = max_stress / applied_stress
print(f"应力集中系数 Kt: {Kt:.2f}")
print(f"理论 Kt (无限大板): 3.0")

odb.close()
```

#### 关键知识点
1. **对称简化**：利用对称性减少计算量
2. **局部加密**：孔边应力梯度大，需要细化网格
3. **二阶单元**：提高应力计算精度
4. **应力集中系数**：Kt = σ_max / σ_nominal

---

### 示例 3：压力容器热应力耦合分析（高级）

**难度**：⭐⭐⭐（困难）  
**目标**：掌握多物理场耦合分析、顺序耦合方法  
**涉及技能**：热传导 → 温度场传递 → 热应力 → 结果对比

#### 场景描述
一个内压容器在工作时内壁温度高于外壁，需要同时考虑内压和热载荷的作用。

#### 关键参数
- 几何：内径 400mm，壁厚 20mm，长度 1000mm
- 内压：10 MPa
- 内壁温度：200°C
- 外壁温度：80°C（对流冷却）
- 材料：16MnR 钢

#### 完整脚本

```python
# -*- coding: utf-8 -*-
"""
示例 3: 压力容器热应力耦合分析（高级）
分析类型: 顺序耦合热应力分析
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import math

# ========== 参数定义 ==========
inner_r = 400.0
outer_r = 420.0
length = 1000.0

E = 210000.0
nu = 0.3
rho = 7.85e-09
alpha = 1.2e-05      # 热膨胀系数
conductivity = 45.0   # W/(m·K)
specific_heat = 460.0 # J/(kg·K)

inner_pressure = 10.0   # MPa
inner_temp = 200.0      # °C
outer_temp = 80.0       # °C

# ========== 第一阶段：稳态热传导 ==========
print("=== 第一阶段：热传导分析 ===")

thermal_model = mdb.Model(name='Thermal-Phase')

# 创建圆筒
sketch = thermal_model.ConstrainedSketch(name='__profile__', sheetSize=1000.0)
sketch.rectangle(point1=(inner_r, 0.0), point2=(outer_r, length))
part = thermal_model.Part(name='Vessel', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=sketch, angle=90.0)  # 1/4模型
del thermal_model.sketches['__profile__']

# 热材料
mat = thermal_model.Material(name='Steel-Thermal')
mat.Conductivity(table=((conductivity,),))
mat.SpecificHeat(table=((specific_heat*1e9,),))
mat.Density(table=((rho),))
section = thermal_model.HomogeneousSolidSection(name='Section', material='Steel-Thermal')
part.SectionAssignment(region=(part.cells,), sectionName='Section')

# 装配
assembly = thermal_model.rootAssembly
instance = assembly.Instance(name='Vessel-1', part=part, dependent=ON)

# 稳态热传导步
thermal_model.HeatTransferStep(name='Steady-State', previous='Initial', 
                               response=STEADY_STATE)

# 内壁温度
inner_faces = instance.faces.getByBoundingCylinder(
    center1=(0,0,0), center2=(0,0,length), radius=inner_r+1)
inner_faces = [f for f in inner_faces 
               if abs(math.sqrt(f.getCentroid()[0]**2 + f.getCentroid()[1]**2) - inner_r) < 5]
region = assembly.Set(name='Inner-Wall', faces=inner_faces)
thermal_model.TemperatureBC(name='Inner-Temp', createStepName='Steady-State',
                            region=region, magnitude=inner_temp)

# 外壁对流
outer_faces = instance.faces.getByBoundingCylinder(
    center1=(0,0,0), center2=(0,0,length), radius=outer_r+1)
outer_faces = [f for f in outer_faces 
               if abs(math.sqrt(f.getCentroid()[0]**2 + f.getCentroid()[1]**2) - outer_r) < 5]
region = assembly.Surface(name='Outer-Surf', side1Faces=outer_faces)
thermal_model.FilmCondition(name='Convection', createStepName='Steady-State',
                            surface=region, filmCoeff=100.0, 
                            sinkTemperature=outer_temp)

# 网格
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=SWEEP)
part.seedPart(size=10.0)
elem_type = mesh.ElemType(elemCode=DC3D8)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交热分析
thermal_job = mdb.Job(name='Thermal-Job', model='Thermal-Phase')
thermal_job.submit()
thermal_job.waitForCompletion()
print("热传导分析完成")

# ========== 第二阶段：热应力分析 ==========
print("=== 第二阶段：热应力分析 ===")

stress_model = mdb.Model(name='Stress-Phase')

# 复制几何
sketch = stress_model.ConstrainedSketch(name='__profile__', sheetSize=1000.0)
sketch.rectangle(point1=(inner_r, 0.0), point2=(outer_r, length))
part = stress_model.Part(name='Vessel', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=sketch, angle=90.0)
del stress_model.sketches['__profile__']

# 热弹性材料
mat = stress_model.Material(name='Steel-Elastic')
mat.Elastic(table=((E, nu),))
mat.Expansion(table=((alpha,),))  # 热膨胀系数
mat.Density(table=((rho),))
section = stress_model.HomogeneousSolidSection(name='Section', material='Steel-Elastic')
part.SectionAssignment(region=(part.cells,), sectionName='Section')

# 装配
assembly = stress_model.rootAssembly
instance = assembly.Instance(name='Vessel-1', part=part, dependent=ON)

# 静力分析步
stress_model.StaticStep(name='Combined-Loading', previous='Initial')

# 对称约束
faces_xz = instance.faces.getByBoundingBox(yMin=-0.1, yMax=0.1)
region = assembly.Set(name='Sym1', faces=faces_xz)
stress_model.DisplacementBC(name='BC-Sym1', createStepName='Initial',
                            region=region, u2=0.0, ur1=0.0, ur3=0.0)

faces_yz = instance.faces.getByBoundingBox(xMin=-0.1, xMax=0.1)
region = assembly.Set(name='Sym2', faces=faces_yz)
stress_model.DisplacementBC(name='BC-Sym2', createStepName='Initial',
                            region=region, u1=0.0, ur2=0.0, ur3=0.0)

# 端部约束
end_faces = instance.faces.getByBoundingBox(zMin=length-0.1, zMax=length+0.1)
region = assembly.Set(name='End', faces=end_faces)
stress_model.DisplacementBC(name='BC-End', createStepName='Initial',
                            region=region, u3=0.0)

# 内压载荷
region = assembly.Surface(name='Inner-Surf', side1Faces=inner_faces)
stress_model.Pressure(name='Internal-Pressure', createStepName='Combined-Loading',
                      region=region, magnitude=inner_pressure)

# 从热分析导入温度场
all_cells = instance.cells
region = assembly.Set(name='Body', cells=all_cells)
stress_model.Temperature(name='Temp-Field', createStepName='Combined-Loading',
                         region=region, distributionType=FROM_FILE,
                         fileName='Thermal-Job.odb', endStep=0, endIncrement=0)

# 网格
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=SWEEP)
part.seedPart(size=10.0)
elem_type = mesh.ElemType(elemCode=C3D8R)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交应力分析
stress_job = mdb.Job(name='Stress-Job', model='Stress-Phase')
stress_job.submit()
stress_job.waitForCompletion()
print("热应力分析完成")

# ========== 结果分析 ==========
print("=== 结果分析 ===")

from odbAccess import openOdb

odb = openOdb(path='Stress-Job.odb')
frame = odb.steps['Combined-Loading'].frames[-1]
stress = frame.fieldOutputs['S']

max_mises = max([v.mises for v in stress.values])

print(f"最大Mises应力: {max_mises:.2f} MPa")
print(f"包含压力应力和热应力的综合效应")

odb.close()
```

#### 关键知识点
1. **顺序耦合**：先热传导 → 再热应力
2. **温度场传递**：使用 `FROM_FILE` 从热分析结果读取
3. **热膨胀**：材料必须定义 `Expansion` 属性
4. **单位注意**：热传导系数和比热的单位转换

---

## 四、故障排除

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 模型不收敛 | 增量太大 | 减小 `initialInc` |
| 奇异矩阵 | 约束不足 | 添加更多边界条件 |
| 单元质量差 | 网格太粗 | 减小种子尺寸 |
| 内存不足 | 模型太大 | 使用并行计算或简化模型 |
| 结果异常 | 单位错误 | 检查单位制一致性 |

### 获取帮助

1. 查看技能文件中的"常见错误"部分
2. 参考 `examples/` 目录下的综合示例
3. 查阅 Abaqus 官方文档

---

## 五、扩展学习

掌握了以上三个示例后，可以尝试：

1. **疲劳分析**：修改示例 2，添加循环载荷和 S-N 曲线
2. **裂纹分析**：在示例 2 的孔边添加 XFEM 裂纹
3. **复合材料**：将示例 1 的钢梁改为碳纤维层合板
4. **优化设计**：结合 Abaqus 优化模块进行尺寸优化

---

**文档版本**：1.0  
**最后更新**：2026-03-04  
**适用 Abaqus 版本**：2016 及以上
