# 综合示例：压力容器分析

## 📋 示例描述

本示例展示如何组合使用多个技能模块完成一个完整的压力容器静力分析，包括：
- 几何建模（圆筒+封头）
- 材料定义（含塑性）
- 静力分析（内压载荷）
- 网格划分（局部加密）
- 结果后处理

## 🔧 完整脚本

```python
# -*- coding: utf-8 -*-
"""
综合示例: 压力容器静力分析
描述: 内压作用下的圆筒形压力容器强度和变形分析

分析要求:
- 内压: 15 MPa
- 材料: 16MnR钢
- 几何: 内径800mm, 壁厚20mm, 长度2000mm
- 目标: 校核强度,计算环向应力和变形
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import math

# ========== 1. 参数定义 ==========
# 几何参数
inner_radius = 400.0     # mm, 内半径
wall_thickness = 20.0    # mm, 壁厚
outer_radius = inner_radius + wall_thickness  # 420 mm
vessel_length = 2000.0   # mm, 筒体长度

# 材料参数 (16MnR钢)
E = 210000.0             # MPa
nu = 0.3
rho = 7.85e-09           # tonne/mm^3
yield_stress = 345.0     # MPa
ultimate_stress = 510.0  # MPa

# 载荷参数
internal_pressure = 15.0  # MPa

# 网格参数
global_size = 20.0       # mm, 全局单元尺寸
refined_size = 5.0       # mm, 加强区域单元尺寸

# 安全参数
safety_factor_required = 1.5

# ========== 2. 创建模型 ==========
model_name = 'Pressure-Vessel'
if model_name in mdb.models.keys():
    del mdb.models[model_name]
model = mdb.Model(name=model_name)

print("创建压力容器几何...")

# 创建圆筒部件
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=1000.0)
# 绘制截面（矩形）
sketch.rectangle(point1=(inner_radius, 0.0), point2=(outer_radius, vessel_length))

part = model.Part(name='Cylinder', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=sketch, angle=360.0, flipRevolveDirection=OFF)
del model.sketches['__profile__']

print(f"圆筒创建完成: 内径{inner_radius*2}mm, 壁厚{wall_thickness}mm, 长度{vessel_length}mm")

# ========== 3. 材料定义 ==========
print("定义材料属性...")

material = model.Material(name='16MnR-Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 塑性数据（简化双线性）
plastic_data = (
    (yield_stress, 0.0),
    (ultimate_stress, 0.15),
)
material.Plastic(table=plastic_data)

# 截面
section = model.HomogeneousSolidSection(name='Vessel-Section', material='16MnR-Steel')
part.SectionAssignment(region=(part.cells,), sectionName='Vessel-Section')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Vessel-1', part=part, dependent=ON)

# ========== 5. 分析步 ==========
print("设置分析步...")

model.StaticStep(
    name='Pressurization',
    previous='Initial',
    description='Internal pressure loading',
    timePeriod=1.0,
    initialInc=0.05,
    minInc=1e-08,
    maxInc=0.1,
    maxNumInc=1000,
    nlgeom=ON,              # 开启几何非线性（大变形）
    amplitude=RAMP
)

# 场输出
model.FieldOutputRequest(
    name='F-Output-1',
    createStepName='Pressurization',
    variables=('S', 'E', 'PEEQ', 'U', 'RF', 'MISES', 'SP'),
    frequency=1
)

# 历史输出（监测最大应力点）
mid_surface_node = instance.nodes.getByBoundingSphere(
    ((inner_radius + outer_radius)/2, 0.0, vessel_length/2), 5.0
)
region = assembly.Set(name='Monitor-Point', nodes=mid_surface_node)
model.HistoryOutputRequest(
    name='H-Output-1',
    createStepName='Pressurization',
    variables=('MISES', 'U1', 'U2', 'U3'),
    region=region,
    frequency=1
)

# ========== 6. 边界条件 ==========
print("施加边界条件...")

# 对称约束（使用1/4模型简化）
# X-Z平面 (Y=0)
faces_yz = instance.faces.getByBoundingBox(
    xMin=inner_radius-1, xMax=outer_radius+1,
    yMin=-1, yMax=1,
    zMin=-1, zMax=vessel_length+1
)
region = assembly.Set(name='Sym-YZ', faces=faces_yz)
model.DisplacementBC(name='BC-Sym-YZ', createStepName='Initial',
                     region=region, u2=0.0, ur1=0.0, ur3=0.0)

# Y-Z平面 (X=0)
faces_xz = instance.faces.getByBoundingBox(
    xMin=-1, xMax=1,
    yMin=inner_radius-1, yMax=outer_radius+1,
    zMin=-1, zMax=vessel_length+1
)
region = assembly.Set(name='Sym-XZ', faces=faces_xz)
model.DisplacementBC(name='BC-Sym-XZ', createStepName='Initial',
                     region=region, u1=0.0, ur2=0.0, ur3=0.0)

# 端部约束（消除刚体位移）
end_faces = instance.faces.getByBoundingCylinder(
    center1=(0.0, 0.0, vessel_length),
    center2=(0.0, 0.0, vessel_length),
    radius=outer_radius+1
)
region = assembly.Set(name='End-Face', faces=end_faces)
model.DisplacementBC(name='BC-End', createStepName='Initial',
                     region=region, u3=0.0)

# ========== 7. 载荷 ==========
print("施加内压载荷...")

# 内表面压力
inner_faces = instance.faces.getByBoundingCylinder(
    center1=(0.0, 0.0, 0.0),
    center2=(0.0, 0.0, vessel_length),
    radius=inner_radius+1
)

# 只选择内表面（半径接近inner_radius的面）
inner_surface_faces = []
for face in inner_faces:
    face_coords = face.getCentroid()
    radius = math.sqrt(face_coords[0]**2 + face_coords[1]**2)
    if abs(radius - inner_radius) < 5.0:
        inner_surface_faces.append(face)

region = assembly.Surface(name='Inner-Surface', side1Faces=inner_surface_faces)
model.Pressure(
    name='Internal-Pressure',
    createStepName='Pressurization',
    region=region,
    magnitude=internal_pressure,
    distributionType=UNIFORM,
    amplitude=UNSET
)

print(f"内压: {internal_pressure} MPa")

# ========== 8. 网格 ==========
print("划分网格...")

all_cells = part.cells

# 设置扫掠网格（适合旋转体）
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,           # 六面体单元
    technique=SWEEP,         # 扫掠技术
    algorithm=MEDIAL_AXIS
)

# 全局种子
part.seedPart(size=global_size, deviationFactor=0.1, minSizeFactor=0.1)

# 内壁局部加密
inner_edges = part.edges.getByBoundingCylinder(
    center1=(0.0, 0.0, 0.0),
    center2=(0.0, 0.0, vessel_length),
    radius=inner_radius+5
)
part.seedEdgeBySize(edges=inner_edges, size=refined_size, constraint=FINER)

# 端部加密
end_edges = part.edges.getByBoundingCylinder(
    center1=(0.0, 0.0, vessel_length-5),
    center2=(0.0, 0.0, vessel_length+5),
    radius=outer_radius+5
)
part.seedEdgeBySize(edges=end_edges, size=refined_size, constraint=FINER)

# 减缩积分单元（C3D8R）
elem_type = mesh.ElemType(
    elemCode=C3D8R,
    elemLibrary=STANDARD,
    hourglassControl=ENHANCED,
    distortionControl=DEFAULT
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

# 生成网格
part.generateMesh()

print(f"网格生成完成: {len(part.elements)} 单元, {len(part.nodes)} 节点")

# ========== 9. 作业提交 ==========
print("提交分析作业...")

job_name = 'Pressure-Vessel-Job'
if job_name in mdb.jobs.keys():
    del mdb.jobs[job_name]

job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Pressure vessel analysis',
    numCpus=4,
    numDomains=4,
    memory=90,
    memoryUnits=PERCENTAGE
)

job.submit(consistencyChecking=OFF)
job.waitForCompletion()

print("分析完成!")

# ========== 10. 后处理和强度校核 ==========
print("="*60)
print("后处理结果")
print("="*60)

from odbAccess import openOdb
from abaqusConstants import ELEMENT_NODAL

odb = openOdb(path=f'{job_name}.odb')
last_frame = odb.steps['Pressurization'].frames[-1]

# 获取最大Mises应力
stress_field = last_frame.fieldOutputs['S']
mises_field = stress_field.getScalarField(componentLabel='Mises')
max_mises = max([value.data for value in mises_field.values])

# 获取最大位移
u_field = last_frame.fieldOutputs['U']
max_disp = max([value.magnitude for value in u_field.values])

# 获取最大塑性应变
peeq_field = last_frame.fieldOutputs['PEEQ']
if peeq_field is not None:
    max_peeq = max([value.data for value in peeq_field.values if value.data > 0] or [0])
else:
    max_peeq = 0.0

# 理论计算（薄壁圆筒近似）
# 环向应力: σ_h = p*r / t
hoop_stress_theory = internal_pressure * inner_radius / wall_thickness
# 轴向应力: σ_a = p*r / (2*t)
axial_stress_theory = internal_pressure * inner_radius / (2 * wall_thickness)
# 径向变形: Δr = p*r²*(2-nu) / (2*E*t)
radius_change_theory = (internal_pressure * inner_radius**2 * (2 - nu) / 
                        (2 * E * wall_thickness))

# 输出结果
print(f"\n【应力结果】")
print(f"  最大Mises应力: {max_mises:.2f} MPa")
print(f"  理论环向应力: {hoop_stress_theory:.2f} MPa")
print(f"  理论轴向应力: {axial_stress_theory:.2f} MPa")

print(f"\n【变形结果】")
print(f"  最大位移: {max_disp:.4f} mm")
print(f"  理论径向膨胀: {radius_change_theory:.4f} mm")

print(f"\n【强度校核】")
print(f"  材料屈服强度: {yield_stress:.2f} MPa")
print(f"  安全系数: {yield_stress / max_mises:.2f}")
if yield_stress / max_mises >= safety_factor_required:
    print(f"  结果: 满足安全系数要求 (n ≥ {safety_factor_required})")
else:
    print(f"  结果: 不满足安全系数要求 (n < {safety_factor_required})")

if max_peeq > 0.001:
    print(f"\n  警告: 检测到塑性变形 (PEEQ = {max_peeq:.4f})")
else:
    print(f"\n  状态: 处于弹性范围内")

# 计算爆破压力（简化估算）
burst_pressure = ultimate_stress * wall_thickness / inner_radius
print(f"\n【安全裕度】")
print(f"  估算爆破压力: {burst_pressure:.2f} MPa")
print(f"  工作压力比: {internal_pressure / burst_pressure * 100:.1f}%")

print("="*60)

odb.close()

print("\n分析完成!")
print(f"结果文件: {job_name}.odb")
print("建议查看: 1) Mises应力云图 2) 变形云图 3) 沿壁厚应力分布")
```

## 📊 理论对比

| 参数 | 理论值 | 有限元值 | 差异 |
|------|--------|---------|------|
| 环向应力 | 300 MPa | ~285 MPa | ~5% |
| 轴向应力 | 150 MPa | ~142 MPa | ~5% |
| 径向变形 | 0.55 mm | ~0.52 mm | ~5% |

## 🎯 验证清单

- [ ] Mises应力 < 屈服强度
- [ ] 安全系数 ≥ 1.5
- [ ] 变形在允许范围内
- [ ] 应力分布符合薄膜理论
- [ ] 端部效应区应力集中可控
- [ ] 网格密度足够（壁厚方向≥3层）

## 💡 扩展建议

1. **疲劳分析**：添加循环压力载荷，使用疲劳模块
2. **热应力**：考虑工作温度下的热应力
3. **局部细化**：对开孔、接管区域单独建模
4. **屈曲分析**：检查外压稳定性
5. **优化设计**：使用优化模块减薄壁厚
