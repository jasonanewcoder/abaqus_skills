# 技能：非线性静力分析 (Nonlinear Static Analysis)

## 📖 功能描述

处理几何非线性、材料非线性、接触非线性等复杂静力问题。

## 🎯 适用场景

- 大变形分析（变形 > 特征尺寸的 5%）
- 材料塑性分析
- 接触问题
- 屈曲后分析

## 💻 完整脚本模板

```python
# -*- coding: utf-8 -*-
"""
分析类型: 非线性静力分析
描述: 包含几何和材料非线性的静力分析

用户输入参数:
- length: 100.0 mm
- width: 50.0 mm
- height: 10.0 mm
- load_magnitude: 5000.0 N (可能导致屈服)
- material: Steel_Q235 (含塑性数据)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
length = 100.0       # mm
width = 50.0         # mm
height = 10.0        # mm

# 材料参数 (Steel_Q235 含塑性)
E = 210000.0         # MPa
nu = 0.3
rho = 7.85e-09       # tonne/mm^3
yield_stress = 235.0 # MPa
ultimate_stress = 375.0  # MPa

# 载荷参数
load_magnitude = 5000.0  # N

# 非线性控制参数
initial_inc = 0.05   # 小初始增量
min_inc = 1e-08      # 最小增量
max_inc = 0.1        # 最大增量
max_num_inc = 1000   # 最大增量数

# ========== 2. 创建模型 ==========
model_name = 'Nonlinear-Static-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# 创建部件
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']

# ========== 3. 材料（含塑性） ==========
material = model.Material(name='Steel-Plastic')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 塑性数据（双线性）
plastic_data = (
    (yield_stress, 0.0),
    (ultimate_stress, 0.2),    # 假设20%应变
)
material.Plastic(table=plastic_data)

# 截面
section = model.HomogeneousSolidSection(name='Section-1', material='Steel-Plastic')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 5. 非线性分析步 ==========
model.StaticStep(
    name='Nonlinear-Step',
    previous='Initial',
    description='Nonlinear static analysis',
    timePeriod=1.0,
    initialInc=initial_inc,
    minInc=min_inc,
    maxInc=max_inc,
    maxNumInc=max_num_inc,
    nlgeom=ON,                   # 开启几何非线性
    amplitude=RAMP
)

# 设置场输出（包含塑性应变）
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Nonlinear-Step',
    variables=('S', 'E', 'PE', 'PEEQ', 'U', 'RF'),
    frequency=10                 # 每10个增量输出
)

# 历史输出（跟踪特定点）
mid_node = instance.nodes.getByBoundingSphere((length/2, width/2, height/2), 1.0)
region = assembly.Set(name='Monitor-Node', nodes=mid_node)
model.HistoryOutputRequest(
    name='H-Output-1',
    createStepName='Nonlinear-Step',
    variables=('U1', 'U2', 'U3', 'RF1', 'RF2', 'RF3'),
    region=region
)

# ========== 6. 边界条件 ==========
fixed_faces = instance.faces.findAt(((0.0, width/2, height/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(name='BC-Fixed', createStepName='Initial', 
                     region=region, u1=0.0, u2=0.0, u3=0.0)

# ========== 7. 载荷（使用幅值曲线） ==========
# 创建平滑幅值曲线
model.SmoothStepAmplitude(
    name='Ramp-Amplitude',
    timeSpan=STEP,
    data=((0.0, 0.0), (1.0, 1.0))
)

load_faces = instance.faces.findAt(((length, width/2, height/2),))
region = assembly.Set(name='Load-End', faces=load_faces)
model.ConcentratedForce(
    name='Load-Force',
    createStepName='Nonlinear-Step',
    region=region,
    cf3=-load_magnitude,
    amplitude='Ramp-Amplitude'
)

# ========== 8. 网格 ==========
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=2.0, deviationFactor=0.1)

# 减缩积分单元（适合大变形）
elem_type = mesh.ElemType(
    elemCode=C3D8R,
    elemLibrary=STANDARD,
    hourglassControl=ENHANCED    # 增强沙漏控制
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 9. 作业提交 ==========
job_name = 'Nonlinear-Static-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    numCpus=4,
    numDomains=4
)

job.submit(consistencyChecking=OFF)
job.waitForCompletion()

print("非线性静力分析完成!")
```

## 🔧 非线性控制参数

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| initialInc | 初始增量 | 0.01 - 0.1 |
| minInc | 最小增量 | 1e-8 - 1e-5 |
| maxInc | 最大增量 | 0.1 - 0.5 |
| nlgeom | 几何非线性 | ON |
| amplitude | 幅值类型 | RAMP 或 STEP |

## 📊 收敛诊断

### 检查收敛

```python
# 查看状态文件
with open('Nonlinear-Static-Job.sta', 'r') as f:
    lines = f.readlines()
    for line in lines[-20:]:
        print(line.strip())
```

### 常见收敛问题及解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 增量步反复减小 | 载荷过大或约束不足 | 减小初始增量，启用稳定化 |
| 达到最大增量数 | 收敛太慢 | 增加 maxNumInc |
| 奇异矩阵 | 刚体位移 | 检查约束是否足够 |
| 沙漏模式 | 减缩积分单元变形 | 启用沙漏控制，使用 C3D8I |

## 💡 稳定化技术

```python
# 自动稳定化（用于后屈曲或接触）
model.StaticStep(
    name='Stabilized-Step',
    previous='Initial',
    stabilizationMagnitude=0.0002,
    stabilizationMethod=DAMPING_FACTOR,
    continueDampingFactors=False
)
```

## 🎯 验证清单

- [ ] 检查 PEEQ（等效塑性应变）分布
- [ ] 确认变形是否合理
- [ ] 检查接触状态（如有接触）
- [ ] 验证能量平衡
- [ ] 检查沙漏能占比（应 < 5%）
