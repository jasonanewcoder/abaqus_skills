# 技能：XFEM 裂纹分析 (Extended Finite Element Method)

## 📖 功能描述

使用扩展有限元方法(XFEM)模拟裂纹萌生和扩展，无需网格与裂纹面吻合。

## 🎯 适用场景

- 裂纹萌生位置未知
- 裂纹扩展路径复杂
- 动态裂纹扩展
- 避免复杂的裂纹网格重划分

## 💻 完整脚本模板

```python
# -*- coding: utf-8 -*-
"""
分析类型: XFEM 裂纹分析
描述: 使用 XFEM 模拟结构中的裂纹萌生和扩展

用户输入参数:
- crack_initiation_stress: 500.0 MPa (裂纹萌生应力)
- fracture_energy: 1000.0 N/m (断裂能)
- max_degradation: 0.9 (最大刚度退化)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
plate_length = 200.0   # mm
plate_width = 100.0    # mm
plate_thickness = 10.0 # mm
notch_length = 20.0    # mm, 初始缺口

# 材料参数
E = 210000.0           # MPa
nu = 0.3
rho = 7.85e-09

# XFEM 损伤参数
crack_initiation_stress = 500.0   # MPa, 裂纹萌生应力
fracture_energy = 1000.0          # N/m, 断裂能
max_degradation = 0.9             # 最大刚度退化

# 载荷参数
tensile_load = 10000.0   # N

# ========== 2. 创建带缺口的板 ==========
model_name = 'XFEM-Crack-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# 创建带缺口的板
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
# 外轮廓
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
# 左侧缺口（裂纹起始点）
sketch.Line(point1=(0.0, plate_width/2), point2=(notch_length, plate_width/2))

part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del model.sketches['__profile__']

# ========== 3. 材料定义（含损伤） ==========
material = model.Material(name='Steel-XFEM')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 定义 Maxps 损伤准则（最大主应力准则）
material.MaxpsDamageInitiation(
    table=((crack_initiation_stress,),),
    definition=VALUE  # 直接指定应力值
)

# 设置损伤演化（基于断裂能）
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,
    mixedModeBehavior=MODE_INDEPENDENT,
    table=((fracture_energy,),)  # 断裂能 Gc
)

# 设置最大刚度退化
material.maxpsDamageInitiation.DamageStabilization(
    cohesiveCoefficient=0.001
)

# 截面
section = model.HomogeneousSolidSection(name='Section-1', material='Steel-XFEM')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. 创建 XFEM 裂纹域 ==========
# 选择整个部件作为 XFEM 域
xfem_region = regionToolset.Region(cells=part.cells)

# 创建 XFEM 裂纹
mdb.models[model_name].XFEMCrack(
    name='Crack-1',
    crackDomain=xfem_region,
    crackLocation=xfem_region,
    allowSelfHealing=OFF
)

# ========== 5. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 6. 非线性分析步 ==========
model.StaticStep(
    name='XFEM-Step',
    previous='Initial',
    description='XFEM crack propagation analysis',
    timePeriod=1.0,
    initialInc=0.01,
    minInc=1e-08,
    maxInc=0.05,
    maxNumInc=1000,
    nlgeom=ON
)

# 设置场输出（包含损伤变量）
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='XFEM-Step',
    variables=('S', 'E', 'U', 'SDEG', 'PHILSM', 'STATUS'),
    frequency=1
)
# SDEG: 刚度退化
# PHILSM: 水平集函数（裂纹位置）
# STATUS: 单元状态

# 历史输出
model.HistoryOutputRequest(
    name='H-Output-1',
    createStepName='XFEM-Step',
    variables=('ALLSE', 'ALLPD', 'ALLWK'),  # 能量输出
)

# ========== 7. 边界条件 ==========
# 固定左侧
fixed_faces = instance.faces.findAt(((0.0, plate_width/4, plate_thickness/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(name='BC-Fixed', createStepName='Initial',
                     region=region, u1=0.0, u2=0.0, u3=0.0)

# 对称约束（Y方向）
sym_faces = instance.faces.findAt(((plate_length/2, 0.0, plate_thickness/2),))
region = assembly.Set(name='Symmetry', faces=sym_faces)
model.SymmetryBC(name='BC-Sym', createStepName='Initial',
                 region=region, axis=AXIS_2)

# ========== 8. 载荷 ==========
loaded_faces = instance.faces.findAt(((plate_length, plate_width*3/4, plate_thickness/2),))
region = assembly.Set(name='Loaded-End', faces=loaded_faces)
model.ConcentratedForce(
    name='Load-Tension',
    createStepName='XFEM-Step',
    region=region,
    cf1=tensile_load
)

# ========== 9. 网格 ==========
# XFEM 需要较细网格
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=TET, technique=FREE)

# 缺口附近加密
notch_region = part.cells.getByBoundingCylinder(
    center1=(0.0, plate_width/2, 0.0),
    center2=(notch_length*3, plate_width/2, plate_thickness),
    radius=plate_width/4
)
part.seedPart(size=2.0)

# 局部加密
notch_edges = part.edges.getByBoundingBox(
    xMin=0, xMax=notch_length*2,
    yMin=plate_width/2-10, yMax=plate_width/2+10,
    zMin=0, zMax=plate_thickness
)
part.seedEdgeBySize(edges=notch_edges, size=0.5, constraint=FINER)

# 使用二阶单元（推荐用于 XFEM）
elem_type = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

part.generateMesh()

print(f"网格单元数: {len(part.elements)}")

# ========== 10. 作业提交 ==========
job_name = 'XFEM-Crack-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    description='XFEM crack propagation',
    numCpus=4,
    numDomains=4
)

job.submit(consistencyChecking=OFF)
job.waitForCompletion()

# ========== 11. 后处理 ==========
from odbAccess import openOdb
import visualization

odb = openOdb(path=f'{job_name}.odb')

# 获取最后一步
last_step = odb.steps['XFEM-Step']
last_frame = last_step.frames[-1]

# 获取损伤变量
sdeg_field = last_frame.fieldOutputs['SDEG']
philsm_field = last_frame.fieldOutputs['PHILSM']

# 统计完全损伤单元
fully_damaged = 0
max_degradation = 0.0

for value in sdeg_field.values:
    if value.data is not None:
        degradation = value.data
        max_degradation = max(max_degradation, degradation)
        if degradation > 0.99:
            fully_damaged += 1

print("="*50)
print("XFEM 裂纹分析结果")
print("="*50)
print(f"最大刚度退化: {max_degradation:.4f}")
print(f"完全损伤单元数: {fully_damaged}")
print("="*50)

odb.close()
```

## 🔧 XFEM 关键参数

### 损伤萌生准则

| 准则 | 适用场景 | 参数 |
|------|---------|------|
| MaxpsDamage | 脆性断裂，拉伸主导 | 最大主应力 |
| MaxpeDamage | 延性材料 | 最大主应变 |
| QuadsDamage | 剪切断裂 | 等效塑性应变 |
| MaxeDamage | 多轴应力 | 最大名义应变 |

### 损伤演化类型

```python
# 基于断裂能（推荐）
material.maxpsDamageInitiation.DamageEvolution(
    type=ENERGY,
    softening=LINEAR,        # 或 EXPONENTIAL, TABULAR
    mixedModeBehavior=MODE_INDEPENDENT,  # 或 MODE_DEPENDENT, POWER_LAW
    power=1.0,
    table=((fracture_energy,),)
)

# 基于位移
material.maxpsDamageInitiation.DamageEvolution(
    type=DISPLACEMENT,
    softening=LINEAR,
    table=((critical_displacement,),)
)
```

## 📊 裂纹追踪

```python
# 输出水平集函数（裂纹位置）
# PHILSM > 0: 材料未断裂
# PHILSM < 0: 材料已断裂
# PHILSM = 0: 裂纹前沿

# 在后处理中可视化裂纹
def visualize_crack(odb_path):
    odb = openOdb(path=odb_path)
    
    # 创建裂纹可视化视图
    viewport = session.viewports['Viewport: 1']
    viewport.setValues(displayedObject=odb)
    
    # 显示损伤云图
    viewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
    viewport.odbDisplay.setPrimaryVariable(
        variableLabel='SDEG',
        outputPosition=INTEGRATION_POINT
    )
    
    # 显示水平集（裂纹面）
    viewport.odbDisplay.setSymbolVariable(
        variableLabel='PHILSM',
        outputPosition=NODAL
    )
```

## 💡 最佳实践

1. **网格要求**：
   - 裂纹区域需要足够细化（最小3-4层单元）
   - 使用二阶单元提高精度
   - 避免极端长宽比的单元

2. **损伤参数标定**：
   - 通过试验确定萌生应力和断裂能
   - 进行网格敏感性分析

3. **收敛控制**：
   - 使用小增量步（initialInc < 0.01）
   - 启用稳定化
   - 密切监控能量平衡

## ⚠️ 使用限制

- 不适用于压剪主导的裂纹
- 需要较细的网格捕获裂纹前沿
- 材料软化可能导致收敛困难
- 裂纹路径预测可能不精确
