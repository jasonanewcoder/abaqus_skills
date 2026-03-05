# 技能：线性静力分析 (Linear Static Analysis)

## 📖 功能描述

执行线弹性小变形静力分析，适用于应力、应变、变形计算。

## 🎯 适用场景

- 小变形结构分析（变形 < 特征尺寸的 5%）
- 线弹性材料（应力 < 屈服强度）
- 刚度计算、强度校核
- 位移和反力计算

## 💻 完整脚本模板

```python
# -*- coding: utf-8 -*-
"""
分析类型: 线性静力分析
描述: 结构在线弹性范围内的应力变形分析

用户输入参数:
- length: 100.0 mm (长度)
- width: 50.0 mm (宽度)
- height: 10.0 mm (高度)
- load_magnitude: 1000.0 N (载荷)
- material: Steel_Q235
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
length = 100.0       # mm
width = 50.0         # mm
height = 10.0        # mm

# 材料参数 (Steel_Q235)
E = 210000.0         # MPa, 弹性模量
nu = 0.3             # 泊松比
rho = 7.85e-09       # tonne/mm^3

# 载荷参数
load_magnitude = 1000.0  # N, 集中力

# 网格参数
element_size = 2.0   # mm

# ========== 2. 创建模型 ==========
model_name = 'Linear-Static-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# 创建草图
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))

# 创建部件
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']

# ========== 3. 材料和截面 ==========
# 创建材料
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 创建截面
section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
region = (part.cells,)
part.SectionAssignment(region=region, sectionName='Section-1')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 5. 分析步 ==========
# 线性静力分析步
model.StaticStep(
    name='Static-Step',
    previous='Initial',
    description='Linear static analysis',
    timePeriod=1.0,
    initialInc=1.0,
    minInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF              # 关闭几何非线性
)

# 设置场输出
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Static-Step',
    variables=('S', 'E', 'U', 'RF', 'MISES'),
    frequency=1
)

# ========== 6. 边界条件 ==========
# 固定端
fixed_faces = instance.faces.findAt(((0.0, width/2, height/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0, u2=0.0, u3=0.0
)

# ========== 7. 载荷 ==========
# 集中力
load_faces = instance.faces.findAt(((length, width/2, height/2),))
region = assembly.Set(name='Load-End', faces=load_faces)
model.ConcentratedForce(
    name='Load-Force',
    createStepName='Static-Step',
    region=region,
    cf3=-load_magnitude    # Z方向向下
)

# ========== 8. 网格 ==========
# 设置网格控制
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)

# 设置种子
part.seedPart(size=element_size, deviationFactor=0.1)

# 设置单元类型（完全积分）
elem_type = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

# 生成网格
part.generateMesh()

# ========== 9. 作业提交 ==========
job_name = 'Linear-Static-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    numCpus=4,
    numDomains=4
)

# 提交作业
job.submit(consistencyChecking=OFF)
job.waitForCompletion()

print("线性静力分析完成!")
```

## 🔧 关键参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| nlgeom | 几何非线性 | OFF（线性分析）|
| initialInc | 初始增量 | 1.0（线性可一步完成）|
| elemCode | 单元类型 | C3D8（完全积分）或 C3D8R |
| 求解器 | 矩阵求解器 | DIRECT |

## 📊 结果解读

### 查看结果

```python
from odbAccess import openOdb

# 打开结果文件
odb = openOdb(path='Linear-Static-Job.odb')

# 获取最后一步最后一增量
last_step = odb.steps.values()[-1]
last_frame = last_step.frames[-1]

# 获取应力场
stress_field = last_frame.fieldOutputs['S']

# 获取最大Mises应力
max_stress = 0.0
for value in stress_field.values:
    mises = value.mises
    if mises > max_stress:
        max_stress = mises

print(f"最大Mises应力: {max_stress:.2f} MPa")

# 获取最大位移
u_field = last_frame.fieldOutputs['U']
max_disp = max([value.magnitude for value in u_field.values])
print(f"最大位移: {max_disp:.4f} mm")

odb.close()
```

## ⚠️ 使用限制

1. 变形必须足够小（不影响平衡方程）
2. 材料必须处于线弹性范围
3. 边界条件不随变形变化
4. 不考虑接触非线性

## 🎯 验证清单

- [ ] 应力值 < 材料屈服强度
- [ ] 最大变形 < 特征尺寸的 5%
- [ ] 网格足够细化（应力集中区）
- [ ] 边界条件约束足够
- [ ] 载荷方向正确
