# 技能：热应力分析 (Thermal Stress Analysis)

## 📖 功能描述

分析温度变化引起的结构热应力和变形，包括顺序耦合和完全耦合两种方法。

## 🎯 适用场景

- 焊接残余应力分析
- 热机耦合载荷
- 温度梯度引起的变形
- 热冲击分析

## 💻 完整脚本模板：顺序耦合热应力

```python
# -*- coding: utf-8 -*-
"""
分析类型: 顺序耦合热应力分析
描述: 先进行热传导分析，再将温度场作为体载荷进行应力分析

用户输入参数:
- initial_temp: 20.0 °C (初始温度)
- applied_temp: 200.0 °C (施加温度)
- heat_transfer_coeff: 50.0 W/(m²·K) (对流系数)
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数
plate_length = 100.0   # mm
plate_width = 50.0     # mm
plate_thickness = 5.0  # mm

# 材料参数 (Steel)
E = 210000.0           # MPa
nu = 0.3
rho = 7.85e-09         # tonne/mm^3

# 热物性参数
thermal_conductivity = 45.0   # W/(m·K)
specific_heat = 460.0         # J/(kg·K)
expansion_coeff = 1.2e-05     # /°C

# 温度参数
initial_temp = 20.0      # °C
applied_temp = 200.0     # °C

# 时间参数
heating_time = 600.0     # s (10分钟)

# ========== 第一阶段：热传导分析 ==========
print("="*50)
print("第一阶段：热传导分析")
print("="*50)

# 创建热传导模型
thermal_model_name = 'Thermal-Model'
if thermal_model_name in mdb.models.keys():
    del mdb.models[thermal_model_name]
thermal_model = mdb.Model(name=thermal_model_name)

# 创建几何
sketch = thermal_model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = thermal_model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del thermal_model.sketches['__profile__']

# 热传导材料
thermal_material = thermal_model.Material(name='Steel-Thermal')
thermal_material.Density(table=((rho),))
thermal_material.Conductivity(table=((thermal_conductivity,),))
thermal_material.SpecificHeat(table=((specific_heat * 1e9,),))  # 单位转换

# 截面
section = thermal_model.HomogeneousSolidSection(name='Section-1', material='Steel-Thermal')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# 装配
thermal_assembly = thermal_model.rootAssembly
instance = thermal_assembly.Instance(name='Plate-1', part=part, dependent=ON)

# 瞬态热传导分析步
thermal_model.HeatTransferStep(
    name='Heating-Step',
    previous='Initial',
    response=TRANSIENT,
    timePeriod=heating_time,
    initialInc=10.0,
    minInc=0.1,
    maxInc=60.0,
    maxNumInc=10000,
    deltmx=50.0           # 最大温度增量
)

# 场输出（温度）
thermal_model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Heating-Step',
    variables=('NT', 'TEMP', 'HFL'),  # 温度、热流
    frequency=10
)

# 初始温度
all_cells = instance.cells
region = thermal_assembly.Set(name='Whole-Body', cells=all_cells)
thermal_model.Temperature(
    name='Initial-Temp',
    createStepName='Initial',
    region=region,
    distributionType=UNIFORM,
    magnitudes=(initial_temp,)
)

# 边界温度（加热区域）
heated_faces = instance.faces.findAt(((plate_length, plate_width/2, plate_thickness/2),))
region = thermal_assembly.Set(name='Heated-Surface', faces=heated_faces)
thermal_model.TemperatureBC(
    name='Temp-BC',
    createStepName='Heating-Step',
    region=region,
    magnitude=applied_temp
)

# 对流边界（其他表面）
convection_faces = [f for f in instance.faces if f not in heated_faces]
region = thermal_assembly.Surface(name='Convection-Surf', side1Faces=convection_faces)
thermal_model.FilmCondition(
    name='Convection',
    createStepName='Heating-Step',
    surface=region,
    definition=EMBEDDED_COEFF,
    filmCoeff=50.0,          # W/(m²·K)
    filmCoeffAmplitude='',
    sinkTemperature=initial_temp,
    sinkAmplitude='',
    sinkDistributionType=UNIFORM
)

# 网格
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=2.0)

# 热传导单元
elem_type = mesh.ElemType(elemCode=DC3D8, elemLibrary=STANDARD)  # 纯热传导单元
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交热传导分析
thermal_job_name = 'Thermal-Job'
if thermal_job_name in mdb.jobs.keys():
    del mdb.jobs[thermal_job_name]

thermal_job = mdb.Job(name=thermal_job_name, model=thermal_model_name, numCpus=4)
thermal_job.submit(consistencyChecking=OFF)
thermal_job.waitForCompletion()

print("热传导分析完成!")

# ========== 第二阶段：应力分析 ==========
print("="*50)
print("第二阶段：应力分析")
print("="*50)

# 创建应力模型
stress_model_name = 'Stress-Model'
if stress_model_name in mdb.models.keys():
    del mdb.models[stress_model_name]
stress_model = mdb.Model(name=stress_model_name)

# 复制几何
sketch = stress_model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length, plate_width))
part = stress_model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)
del stress_model.sketches['__profile__']

# 热弹性材料（含热膨胀）
stress_material = stress_model.Material(name='Steel-Thermal-Elastic')
stress_material.Elastic(table=((E, nu),))
stress_material.Density(table=((rho),))
stress_material.Expansion(table=((expansion_coeff,),))  # 热膨胀系数

# 截面
section = stress_model.HomogeneousSolidSection(name='Section-1', material='Steel-Thermal-Elastic')
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')

# 装配
stress_assembly = stress_model.rootAssembly
instance = stress_assembly.Instance(name='Plate-1', part=part, dependent=ON)

# 静力分析步（用于热应力）
stress_model.StaticStep(
    name='Thermal-Stress-Step',
    previous='Initial',
    description='Thermal stress analysis',
    nlgeom=OFF
)

# 场输出
stress_model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Thermal-Stress-Step',
    variables=('S', 'E', 'U', 'RF', 'NT', 'MISES'),
    frequency=1
)

# 固定约束（避免刚体位移）
fixed_faces = instance.faces.findAt(((0.0, plate_width/2, plate_thickness/2),))
region = stress_assembly.Set(name='Fixed-End', faces=fixed_faces)
stress_model.DisplacementBC(name='BC-Fixed', createStepName='Initial',
                            region=region, u1=0.0, u2=0.0, u3=0.0)

# 对称约束
sym_faces_x = instance.faces.findAt(((plate_length/2, 0.0, plate_thickness/2),))
region = stress_assembly.Set(name='Sym-X', faces=sym_faces_x)
stress_model.DisplacementBC(name='BC-Sym-X', createStepName='Initial',
                            region=region, u2=0.0)

sym_faces_y = instance.faces.findAt(((0.0, plate_width/2, plate_thickness/2),))
region = stress_assembly.Set(name='Sym-Y', faces=sym_faces_y)
stress_model.DisplacementBC(name='BC-Sym-Y', createStepName='Initial',
                            region=region, u1=0.0)

# 从热传导结果导入温度场
all_cells = instance.cells
region = stress_assembly.Set(name='Temp-Region', cells=all_cells)
stress_model.Temperature(
    name='Temp-From-Thermal',
    createStepName='Thermal-Stress-Step',
    region=region,
    distributionType=FROM_FILE,
    fileName=f'{thermal_job_name}.odb',
    beginStep=0,
    beginIncrement=0,
    endStep=0,          # 最后一步
    endIncrement=0,     # 最后增量
    interpolate=ON
)

# 网格
all_cells = part.cells
part.setMeshControls(regions=all_cells, elemShape=HEX, technique=STRUCTURED)
part.seedPart(size=2.0)

# 应力单元
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交应力分析
stress_job_name = 'Thermal-Stress-Job'
if stress_job_name in mdb.jobs.keys():
    del mdb.jobs[stress_job_name]

stress_job = mdb.Job(name=stress_job_name, model=stress_model_name, numCpus=4)
stress_job.submit(consistencyChecking=OFF)
stress_job.waitForCompletion()

print("热应力分析完成!")

# ========== 结果输出 ==========
from odbAccess import openOdb

odb = openOdb(path=f'{stress_job_name}.odb')
last_frame = odb.steps['Thermal-Stress-Step'].frames[-1]

stress_field = last_frame.fieldOutputs['S']
max_mises = max([v.mises for v in stress_field.values])

u_field = last_frame.fieldOutputs['U']
max_disp = max([v.magnitude for v in u_field.values])

print("="*50)
print("热应力分析结果")
print("="*50)
print(f"最大Mises应力: {max_mises:.2f} MPa")
print(f"最大位移: {max_disp:.4f} mm")
print("="*50)

odb.close()
```

## 🔧 完全耦合热应力分析

```python
# 完全耦合分析（同时求解温度和位移）
model.CoupledTempDisplacementStep(
    name='Coupled-Step',
    previous='Initial',
    description='Fully coupled thermal-stress analysis',
    timePeriod=heating_time,
    initialInc=1.0,
    minInc=0.001,
    maxInc=10.0,
    maxNumInc=1000,
    deltmx=50.0,         # 最大温度增量
    cetol=0.001,         # 耦合场容差
    nlgeom=ON
)
```

## 📊 热应力计算原理

### 热应变公式

```
ε_thermal = α × ΔT

其中:
α = 热膨胀系数
ΔT = T - T_ref (温度变化)
```

### 总应变分解

```
ε_total = ε_elastic + ε_thermal
ε_elastic = ε_total - α × ΔT
```

### 热应力

```
σ = D × ε_elastic = D × (ε_total - α × ΔT)
```

## 💡 最佳实践

1. **单位一致性**：
   - 热传导系数：W/(m·K) → mW/(mm·K)
   - 比热容：J/(kg·K) → mJ/(tonne·K)
   - 热膨胀系数：/°C 或 /K

2. **边界条件**：
   - 应力分析需要足够的约束避免刚体位移
   - 对称面可以简化模型

3. **时间步长**：
   - 瞬态热分析需要小时间步
   - 使用自动时间步长控制

4. **结果验证**：
   - 检查温度分布合理性
   - 验证应力与温度梯度对应关系

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 温度单位错误 | 摄氏/开尔文混淆 | 使用 °C，Abaqus 内部处理 |
| 热膨胀方向错误 | 约束不足 | 添加适当约束 |
| 奇异矩阵 | 完全约束热膨胀 | 使用软弹簧或释放一个约束 |
| 温度不传递 | ODB 文件路径错误 | 检查文件路径和名称 |
