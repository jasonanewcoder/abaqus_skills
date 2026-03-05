# 技能：高周疲劳分析 (High Cycle Fatigue)

## 📖 功能描述

基于 S-N 曲线的高周疲劳寿命预测，适用于应力水平低于屈服强度的循环载荷。

## 🎯 适用场景

- 应力水平 σ_max < σ_y（屈服强度）
- 循环次数 N > 10^4 ~ 10^6
- 弹性变形主导的疲劳问题
- 机械零件、连接件的寿命预测

## 💻 完整脚本模板

```python
# -*- coding: utf-8 -*-
"""
分析类型: 高周疲劳分析
描述: 基于 S-N 曲线的高周疲劳寿命预测

用户输入参数:
- load_amplitude: 500.0 N (载荷幅值)
- load_mean: 1000.0 N (平均载荷)
- stress_concentration: 3.0 (应力集中系数)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
notch_radius = 5.0   # mm, 缺口半径
specimen_width = 50.0  # mm
specimen_thickness = 10.0  # mm

# 材料参数 (Steel)
E = 210000.0         # MPa
nu = 0.3
rho = 7.85e-09

# S-N 曲线参数 (Steel典型值)
# 双对数坐标下 S = Sf * (2N)^b
Sf_prime = 1000.0    # MPa, 疲劳强度系数
b = -0.085           # 疲劳强度指数
Se = 200.0           # MPa, 疲劳极限 (10^6 循环)

# 载荷参数
load_amplitude = 500.0   # N, 载荷幅值
load_mean = 1000.0       # N, 平均载荷
stress_concentration = 3.0  # 应力集中系数

# ========== 2. 创建带缺口试样 ==========
model_name = 'HCF-Model'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

# 创建几何（简化平板带圆孔）
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# 外轮廓
sketch.rectangle(point1=(0.0, 0.0), point2=(100.0, specimen_width))
# 中心圆孔（应力集中源）
sketch.CircleByCenterPerimeter(center=(50.0, specimen_width/2), point1=(50.0 + notch_radius, specimen_width/2))

part = model.Part(name='Specimen', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=specimen_thickness)
del model.sketches['__profile__']

# ========== 3. 材料定义 ==========
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 截面
section = model.HomogeneousSolidSection(name='Section-1', material='Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Specimen-1', part=part, dependent=ON)

# ========== 5. 疲劳分析步 ==========
# 静力分析步（用于获取应力幅值）
model.StaticStep(
    name='Fatigue-Step',
    previous='Initial',
    description='Static step for fatigue analysis',
    nlgeom=OFF
)

# 设置场输出
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Fatigue-Step',
    variables=('S', 'E', 'U', 'MISES'),
    frequency=1
)

# ========== 6. 边界条件 ==========
# 固定端
fixed_faces = instance.faces.findAt(((0.0, specimen_width/2, specimen_thickness/2),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)
model.DisplacementBC(name='BC-Fixed', createStepName='Initial',
                     region=region, u1=0.0, u2=0.0, u3=0.0)

# ========== 7. 载荷（最大载荷） ==========
max_load = load_mean + load_amplitude
loaded_faces = instance.faces.findAt(((100.0, specimen_width/2, specimen_thickness/2),))
region = assembly.Set(name='Loaded-End', faces=loaded_faces)
model.ConcentratedForce(
    name='Load-Max',
    createStepName='Fatigue-Step',
    region=region,
    cf1=max_load
)

# ========== 8. 网格（关键区域加密） ==========
# 缺口附近加密
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=TET, technique=FREE)

# 全局种子
part.seedPart(size=5.0)

# 缺口附近边加密
notch_edges = part.edges.getByBoundingCylinder(
    center1=(50.0, specimen_width/2, 0.0),
    center2=(50.0, specimen_width/2, specimen_thickness),
    radius=notch_radius * 2
)
part.seedEdgeBySize(edges=notch_edges, size=0.5, constraint=FINER)

# 二阶单元（精度更高）
elem_type = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# ========== 9. 作业提交 ==========
job_name = 'HCF-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(name=job_name, model=model_name, numCpus=4)
job.submit(consistencyChecking=OFF)
job.waitForCompletion()

# ========== 10. 疲劳后处理 ==========
from odbAccess import openOdb
import math

odb = openOdb(path=f'{job_name}.odb')
last_frame = odb.steps['Fatigue-Step'].frames[-1]
stress_field = last_frame.fieldOutputs['S']

# 获取最大应力
max_stress = 0.0
max_stress_location = None

for value in stress_field.values:
    mises = value.mises
    if mises > max_stress:
        max_stress = mises
        max_stress_location = value.elementLabel

# 考虑应力集中系数
max_stress_kt = max_stress * stress_concentration

# S-N 曲线计算寿命 (Basquin 方程)
# S = Sf * (2N)^b
# log(S) = log(Sf) + b * log(2N)
# log(2N) = (log(S) - log(Sf)) / b
# N = 10^((log(S) - log(Sf)) / b) / 2

if max_stress_kt > Se:
    log_S = math.log10(max_stress_kt)
    log_Sf = math.log10(Sf_prime)
    log_2N = (log_S - log_Sf) / b
    cycles_to_failure = int(10**log_2N / 2)
else:
    cycles_to_failure = 'Infinite (>10^6)'

print("="*50)
print("高周疲劳分析结果")
print("="*50)
print(f"最大名义应力: {max_stress:.2f} MPa")
print(f"应力集中系数 Kt: {stress_concentration}")
print(f"最大局部应力: {max_stress_kt:.2f} MPa")
print(f"疲劳极限: {Se:.2f} MPa")
print(f"预测寿命: {cycles_to_failure} 循环")
print("="*50)

odb.close()
```

## 📊 疲劳损伤累积

### Miner 线性累积损伤理论

```python
def miner_damage(stress_cycles_list, Sf, b, Se):
    """
    计算 Miner 累积损伤
    stress_cycles_list: [(应力幅值, 循环次数), ...]
    """
    total_damage = 0.0
    
    for stress_amp, n_i in stress_cycles_list:
        if stress_amp > Se:
            # 计算该应力水平下的失效循环数
            N_i = int(10**((math.log10(stress_amp) - math.log10(Sf)) / b) / 2)
            damage = n_i / N_i
            total_damage += damage
            print(f"应力 {stress_amp:.1f} MPa: {n_i}/{N_i} 循环, 损伤 = {damage:.4f}")
    
    print(f"总累积损伤: {total_damage:.4f}")
    print(f"预测寿命系数: {1.0/total_damage:.2f}")
    
    return total_damage

# 示例：雨流计数后的应力谱
stress_spectrum = [
    (300.0, 10000),    # (应力幅值 MPa, 实际循环数)
    (250.0, 50000),
    (200.0, 100000),
    (150.0, 500000),
]

D = miner_damage(stress_spectrum, Sf_prime, b, Se)
```

## 🎯 影响因素

| 因素 | 影响 | 处理方法 |
|------|------|---------|
| 表面粗糙度 | 降低疲劳强度 | 表面finish系数 |
| 尺寸效应 | 大尺寸降低强度 | 尺寸系数 |
| 载荷类型 | 弯曲 > 拉压 > 扭转 | 载荷系数 |
| 环境温度 | 高温降低强度 | 温度修正 |

## 💡 最佳实践

1. **应力集中处理**：
   - 缺口处网格足够细化
   - 使用二阶单元提高精度
   - 考虑实际 Kt 值

2. **平均应力修正**：
   - Goodman 公式：σ_a / σ_N + σ_m / σ_u = 1
   - Gerber 公式：σ_a / σ_N + (σ_m / σ_u)^2 = 1
   - Soderberg 公式：σ_a / σ_N + σ_m / σ_y = 1

3. **安全系数**：
   - 关键部件：n = 2.0 ~ 3.0
   - 一般部件：n = 1.5 ~ 2.0

## ⚠️ 使用限制

- 仅适用于弹性应力范围
- 不考虑裂纹扩展阶段
- 需要准确的 S-N 曲线数据
- Miner 理论为线性累积，实际有交互作用
