# 技能：复合材料层合板分析 (Composite Laminate Analysis)

## 📖 功能描述

使用经典层合板理论(CLT)分析多层复合材料层合板的刚度、强度和失效。

## 🎯 适用场景

- 飞机结构（机翼、机身）
- 风力发电机叶片
- 汽车车身面板
- 船舶结构

## 💻 完整脚本模板

```python
# -*- coding: utf-8 -*-
"""
分析类型: 复合材料层合板分析
描述: 多层复合材料层合板的应力和失效分析

用户输入参数:
- layup: [(0, 0.25), (45, 0.25), (-45, 0.25), (90, 0.25)] mm (铺层角度和厚度)
- panel_length: 200.0 mm
- panel_width: 100.0 mm
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
panel_length = 200.0   # mm
panel_width = 100.0    # mm

# 铺层定义: (角度°, 厚度mm)
# 示例: [0/45/-45/90]s 对称铺层
layup = [
    (0, 0.25),
    (45, 0.25),
    (-45, 0.25),
    (90, 0.25),
    (90, 0.25),      # 对称
    (-45, 0.25),
    (45, 0.25),
    (0, 0.25),
]

# 计算总厚度
total_thickness = sum([layer[1] for layer in layup])
print(f"层合板总厚度: {total_thickness} mm")

# 单向复合材料性能 (T300/5208 典型值)
E1 = 181000.0        # MPa, 纵向弹性模量
E2 = 10300.0         # MPa, 横向弹性模量
E3 = 10300.0         # MPa
nu12 = 0.28          # 主泊松比
nu13 = 0.28
nu23 = 0.5
G12 = 7170.0         # MPa, 面内剪切模量
G13 = 7170.0
G23 = 3600.0

# 密度
rho = 1.6e-09        # tonne/mm^3

# 载荷参数
axial_load = 1000.0  # N/mm, 轴向载荷

# ========== 2. 创建模型 ==========
model_name = 'Composite-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# 创建壳体部件
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(panel_length, panel_width))

part = model.Part(name='Laminate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseShell(sketch=sketch)
del model.sketches['__profile__']

# ========== 3. 定义复合材料材料 ==========
composite_material = model.Material(name='T300-5208')

# 弹性属性（各向异性）
composite_material.Elastic(
    type=LAMINA,
    table=((E1, E2, nu12, G12, G13, G23),)
)

# 密度
composite_material.Density(table=((rho),))

# 失效准则（Hashin）
Xt = 1500.0          # MPa, 纵向拉伸强度
Xc = 1500.0          # MPa, 纵向压缩强度
Yt = 40.0            # MPa, 横向拉伸强度
Yc = 246.0           # MPa, 横向压缩强度
S = 68.0             # MPa, 面内剪切强度

composite_material.HashinDamageInitiation(
    table=((Xt, Xc, Yt, Yc, S),)
)

# 损伤演化
composite_material.hashinDamageInitiation.DamageEvolution(
    type=ENERGY,
    mixedModeBehavior=MODE_INDEPENDENT,
    table=((10.0, 1.0, 1.0),)  # 断裂能
)

# ========== 4. 创建复合材料铺层 ==========
# 创建铺层
compositeLayup = part.CompositeLayup(
    name='Laminate-Layup',
    description='Composite laminate',
    elementType=SHELL,           # 或 CONTINUUM_SHELL, SOLID
    offset=MIDDLE_SURFACE,
    symmetric=False,
    thicknessAssignment=FROM_SECTION
)

# 添加铺层
for i, (angle, thickness) in enumerate(layup):
    # 创建参考方向（通常沿长度方向）
    region = regionToolset.Region(faces=part.faces)
    
    compositeLayup.CompositePly(
        name=f'Ply-{i+1}',
        region=region,
        material='T300-5208',
        thicknessType=SPECIFY_THICKNESS,
        thickness=thickness,
        orientationType=SPECIFY_ORIENT,
        orientationValue=angle,
        axis=AXIS_3,
        angle=0.0
    )

# 设置单元类型
elem_type = mesh.ElemType(elemCode=S8R, elemLibrary=STANDARD)
part.setElementType(regions=(part.faces,), elemTypes=(elem_type,))

# ========== 5. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Laminate-1', part=part, dependent=ON)

# ========== 6. 分析步 ==========
model.StaticStep(
    name='Static-Step',
    previous='Initial',
    description='Composite laminate analysis',
    nlgeom=OFF
)

# 场输出（包含层间应力）
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Step',
    variables=('S', 'E', 'U', 'SF', 'SM', 'SDEG', 'HSNFTCRT', 'HSNFCCRT', 'HSNMTCRT', 'HSNMCCRT'),
    frequency=1
)
# SF: 层合板面内应力结果
# SM: 层合板弯矩结果
# HS*CRT: Hashin失效准则输出

# ========== 7. 边界条件 ==========
# 固定端
fixed_edges = instance.edges.findAt(((0.0, panel_width/2, 0.0),))
region = assembly.Set(name='Fixed-End', edges=fixed_edges)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=region)

# 对称约束（简化一半模型）
sym_edges = instance.edges.findAt(((panel_length/2, 0.0, 0.0),))
region = assembly.Set(name='Symmetry', edges=sym_edges)
model.DisplacementBC(name='BC-Sym', createStepName='Initial',
                     region=region, u2=0.0)

# ========== 8. 载荷 ==========
# 分布载荷（轴向拉伸）
loaded_edges = instance.edges.findAt(((panel_length, panel_width*3/4, 0.0),))
region = assembly.Set(name='Loaded-End', edges=loaded_edges)

# 壳体使用 edge load
model.ShellEdgeLoad(
    name='Load-Axial',
    createStepName='Static-Step',
    region=region,
    magnitude=axial_load,
    directionVector=(1.0, 0.0, 0.0),
    follower=OFF
)

# ========== 9. 网格 ==========
part.seedPart(size=5.0, deviationFactor=0.1)
part.generateMesh()

print(f"网格单元数: {len(part.elements)}")

# ========== 10. 作业提交 ==========
job_name = 'Composite-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit(consistencyChecking=OFF)
job.waitForCompletion()

# ========== 11. 结果处理 ==========
from odbAccess import openOdb

odb = openOdb(path=f'{job_name}.odb')
last_frame = odb.steps['Static-Step'].frames[-1]

# 获取层合板应力
# 注意：复合材料需要查询特定层的结果
stress_field = last_frame.fieldOutputs['S']

# 获取Hashin失效指标
hashin_tensile_fiber = last_frame.fieldOutputs['HSNFTCRT']
hashin_compressive_fiber = last_frame.fieldOutputs['HSNFCCRT']

max_tensile_fiber = max([v.data for v in hashin_tensile_fiber.values if v.data is not None] or [0])
max_compressive_fiber = max([v.data for v in hashin_compressive_fiber.values if v.data is not None] or [0])

print("="*50)
print("复合材料层合板分析结果")
print("="*50)
print(f"纤维拉伸失效指标: {max_tensile_fiber:.4f}")
print(f"纤维压缩失效指标: {max_compressive_fiber:.4f}")

if max(max_tensile_fiber, max_compressive_fiber) > 1.0:
    print("警告: 发生纤维失效!")
else:
    print("状态: 纤维未失效")
print("="*50)

odb.close()
```

## 🔧 铺层方向约定

| 角度 | 方向 | 应用 |
|------|------|------|
| 0° | 沿参考方向（通常为长度） | 承受轴向载荷 |
| 90° | 垂直参考方向 | 横向刚度 |
| ±45° | 斜交 | 剪切刚度，冲击阻抗 |

## 📊 典型铺层序列

```python
# 准各向同性
quasi_isotropic = [(0, t), (45, t), (-45, t), (90, t)]

# 对称铺层 [0/45/-45/90]s
symmetric = [(0, t), (45, t), (-45, t), (90, t), (90, t), (-45, t), (45, t), (0, t)]

# 角度铺层 [+45/-45]2s
angle_ply = [(45, t), (-45, t), (45, t), (-45, t), (-45, t), (45, t), (-45, t), (45, t)]

# 单向强化 [0/90]4s
cross_ply = [(0, t), (90, t)] * 4 + [(90, t), (0, t)] * 4
```

## 💡 最佳实践

1. **铺层设计原则**：
   - 保持铺层对称避免耦合
   - ±45° 层成对出现
   - 避免多于4层同方向连续铺层

2. **网格要求**：
   - 每个单元至少一个积分点
   - 使用 S8R 二阶单元提高精度

3. **失效准则选择**：
   - Hashin：区分纤维和基体失效
   - Puck：考虑角度效应
   - LaRC：更精确但复杂

4. **结果解读**：
   - HSNFTCRT > 1: 纤维拉伸失效
   - HSNFCCRT > 1: 纤维压缩失效
   - HSNMTCRT > 1: 基体拉伸失效
   - HSNMCCRT > 1: 基体压缩失效

## ⚠️ 使用限制

- 层合板理论假设层间正应力可忽略
- 厚层合板需使用实体单元
- 考虑层间失效需要内聚力单元
