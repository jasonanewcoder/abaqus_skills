# 案例三：AI辅助Abaqus仿真高级 - 压力容器热应力耦合分析

## 引言：真正的多物理场挑战

恭喜你，已经跟着我完成了两个案例！

从简单的悬臂梁，到进阶的应力集中，我们的仿真能力在不断提升。但今天我们要面对的，是一个真正具有挑战性的问题：**热应力耦合分析**。

为什么说它“高级”？

因为它涉及两个物理场的相互作用：
1. **温度场**：热量在物体内部传导
2. **应力场**：温度变化导致材料膨胀/收缩

这种耦合在工程中极其常见：
- 发动机缸体：燃烧产生高温，机体膨胀
- 电子设备：芯片发热，热应力导致开裂
- 管道系统：内流高温介质，内外温差导致热应力
- 焊接过程：局部加热冷却，产生残余应力

今天的案例是一个典型的工业问题：**压力容器在内外温差作用下的热应力分析**。

---

## 一、案例参数：内压容器的热应力

### 1.1 问题描述

![图片：压力容器截面示意图]
```
    ┌───────────────────────────────────┐
    │  内壁: T=200°C    outer_r=420mm  │
    │  ────────────────────────────────  │
    │              │                     │
    │              │   壁厚 t=20mm       │
    │              │                     │
    │  外壁: T=80°C                     │
    │  对流散热 h=100W/(m²·K)           │
    └───────────────────────────────────┘
            长度 L=1000mm
```

一个圆柱形压力容器，内有高温介质，外与环境对流散热。容器同时承受：
- **内压**：10 MPa
- **热载荷**：内壁200°C，外壁80°C（对流边界）

### 1.2 关键参数

| 参数 | 数值 | 单位 |
|------|------|------|
| 内径rᵢ | 400 | mm |
| 外径rₒ | 420 | mm |
| 壁厚t | 20 | mm |
| 长度L | 1000 | mm |
| 材料 | 16MnR钢 | - |
| 弹性模量E | 210000 | MPa |
| 泊松比ν | 0.3 | - |
| 热膨胀系数α | 1.2×10⁻⁵ | /°C |
| 导热系数k | 45 | W/(m·K) |
| 内壁温度Tᵢ | 200 | °C |
| 外壁温度Tₒ | 80 | °C |
| 对流系数h | 100 | W/(m²·K) |
| 环境温度T∞ | 30 | °C |
| 内压P | 10 | MPa |

### 1.3 理论背景：热应力

当温度变化时，材料会热膨胀（或收缩）。如果这种膨胀受到约束，就会产生**热应力**。

**热应力基本公式**：
$$\sigma = E \cdot \alpha \cdot \Delta T$$

其中：
- E 是弹性模量
- α 是热膨胀系数
- ΔT 是温度变化

在我们的案例中，内壁温度高，膨胀多；外壁温度低，膨胀少。内外膨胀不一致，互相约束，就产生了热应力。

---

## 二、分析策略：顺序耦合

### 2.1 什么是顺序耦合？

对于热-结构耦合问题，有两种分析方法：

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| **直接耦合** | 同时求解温度和应力 | 强耦合（温度影响显著） |
| **顺序耦合** | 先求温度场，再求应力场 | 弱耦合（单向影响） |

我们的案例属于**顺序耦合**：
1. **第一步**：做热传导分析，得到温度分布
2. **第二步**：将温度场作为载荷，做结构分析

### 2.2 为什么用顺序耦合？

- 计算效率高：两个简单分析 < 一个复杂分析
- 物理概念清晰：先有温度，再有应力
- 便于调试：分别验证温度场和应力场

---

## 三、让AI生成脚本

### 3.1 给AI的指令

```
请帮我生成一个Abaqus Python脚本，进行压力容器的顺序耦合热应力分析。

要求：
1. 第一步：稳态热传导分析
   - 内壁施加温度边界条件 T=200°C
   - 外壁施加对流边界条件 h=100 W/(m²·K)，环境温度30°C
   - 导热系数 k=45 W/(m·K)

2. 第二步：热应力分析
   - 导入第一步的温度场结果
   - 材料属性：E=210000 MPa, ν=0.3, α=1.2e-5 /°C
   - 内压 P=10 MPa

3. 使用八分之一模型（利用对称性）

请参考技能库中的热分析技能生成代码。
```

### 3.2 AI生成的代码

```python
# -*- coding: utf-8 -*-
"""
压力容器热应力耦合分析
分析类型: 顺序耦合热-结构分析
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *
import math

# ========== 1. 参数定义 ==========
# 几何参数（单位：mm）
inner_radius = 400.0    # 内半径
outer_radius = 420.0    # 外半径
length = 1000.0         # 长度

# 材料参数
E = 210000.0           # 弹性模量 (MPa)
nu = 0.3               # 泊松比
alpha = 1.2e-05        # 热膨胀系数 (/°C)
conductivity = 45.0     # 导热系数 (W/(m·K))
density = 7.85e-09     # 密度 (tonne/mm³)

# 温度参数（单位：°C）
inner_temp = 200.0      # 内壁温度
outer_temp = 80.0       # 外壁初始温度
sink_temp = 30.0        # 环境温度
film_coeff = 100.0      # 对流系数 (W/(m²·K))

# 压力参数（单位：MPa）
inner_pressure = 10.0   # 内压

# 网格参数
mesh_size = 15.0        # 全局网格大小

# ========== 2. 第一步：热传导分析 ==========
print("=" * 60)
print("第一步：热传导分析")
print("=" * 60)

thermal_model = mdb.Model(name='Thermal-Analysis')

# 创建八分之一圆柱壳
sketch = thermal_model.ConstrainedSketch(name='__profile__', sheetSize=1000.0)
sketch.rectangle(point1=(inner_radius, 0.0), point2=(outer_radius, length/2))

part = thermal_model.Part(name='Vessel- Thermal', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=sketch, angle=45.0)  # 45° = 1/8圆周
del thermal_model.sketches['__profile__']

# 定义热材料
mat = thermal_model.Material(name='Steel-Thermal')
mat.Conductivity(table=((conductivity/1000.0,),))  # 转换为 mm·W/(K·mm)·K = W/(mm·K)
mat.Density(table=((density),))

section = thermal_model.HomogeneousSolidSection(name='Thermal-Section', 
                                                material='Steel-Thermal')
part.SectionAssignment(region=(part.cells,), sectionName='Thermal-Section')

# 装配
assembly = thermal_model.rootAssembly
instance = assembly.Instance(name='Thermal-1', part=part, dependent=ON)

# 热分析步
thermal_model.HeatTransferStep(
    name='Steady-State', 
    previous='Initial', 
    response=STEADY_STATE
)

# 内壁温度边界条件
inner_faces = instance.faces.getByBoundingCylinder(
    center1=(0, 0, 0), 
    center2=(0, length, 0), 
    radius=inner_radius + 1
)
inner_faces = [f for f in inner_faces 
               if abs(math.sqrt(f.getCentroid()[0]**2 + f.getCentroid()[1]**2) - inner_radius) < 5]
inner_region = assembly.Set(name='Inner-Wall', faces=inner_faces)

thermal_model.TemperatureBC(
    name='Inner-Temp', 
    createStepName='Steady-State',
    region=inner_region, 
    magnitude=inner_temp
)

# 外壁对流边界条件
outer_faces = instance.faces.getByBoundingCylinder(
    center1=(0, 0, 0), 
    center2=(0, length, 0), 
    radius=outer_radius - 1
)
outer_faces = [f for f in outer_faces 
               if abs(math.sqrt(f.getCentroid()[0]**2 + f.getCentroid()[1]**2) - outer_radius) < 5]
outer_region = assembly.Surface(name='Outer-Surf', side1Faces=outer_faces)

thermal_model.FilmCondition(
    name='Convection', 
    createStepName='Steady-State',
    surface=outer_region, 
    filmCoeff=film_coeff/1000.0,  # 转换为 mm 单位
    sinkTemperature=sink_temp
)

# 对称边界条件
# X=0 对称
sym_x_faces = instance.faces.getByBoundingBox(xMin=-0.1, xMax=0.1)
sym_x_region = assembly.Set(name='Sym-X', faces=sym_x_faces)
thermal_model.TemperatureBC(
    name='BC-Sym-X', 
    createStepName='Steady-State',
    region=sym_x_region, 
    magnitude=0.0  # 对称面热通量为0
)

# Y=0 对称
sym_y_faces = instance.faces.getByBoundingBox(yMin=-0.1, yMax=0.1)
sym_y_region = assembly.Set(name='Sym-Y', faces=sym_y_faces)
thermal_model.TemperatureBC(
    name='BC-Sym-Y', 
    createStepName='Steady-State',
    region=sym_y_region, 
    magnitude=0.0
)

# Z=0 端面对称（长度方向）
sym_z_faces = instance.faces.getByBoundingBox(zMin=-0.1, zMax=0.1)
sym_z_region = assembly.Set(name='Sym-Z', faces=sym_z_faces)
thermal_model.TemperatureBC(
    name='BC-Sym-Z', 
    createStepName='Steady-State',
    region=sym_z_region, 
    magnitude=0.0
)

# 划分网格
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=SWEEP)
part.seedPart(size=mesh_size)
elem_type = mesh.ElemType(elemCode=DC3D8)  # 热传导单元
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交热分析作业
thermal_job = mdb.Job(name='Thermal-Job', model='Thermal-Analysis')
thermal_job.submit()
thermal_job.waitForCompletion()

print("热传导分析完成！")
print("=" * 60)

# ========== 3. 第二步：热应力分析 ==========
print("=" * 60)
print("第二步：热应力分析")
print("=" * 60)

stress_model = mdb.Model(name='Thermal-Stress')

# 创建相同的几何
sketch = stress_model.ConstrainedSketch(name='__profile__', sheetSize=1000.0)
sketch.rectangle(point1=(inner_radius, 0.0), point2=(outer_radius, length/2))

part = stress_model.Part(name='Vessel-Stress', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidRevolve(sketch=sketch, angle=45.0)
del stress_model.sketches['__profile__']

# 定义材料（包含热膨胀）
mat = stress_model.Material(name='Steel-Structural')
mat.Elastic(table=((E, nu),))
mat.Expansion(table=((alpha,),))  # 热膨胀系数
mat.Density(table=((density),))

section = stress_model.HomogeneousSolidSection(name='Stress-Section', 
                                               material='Steel-Structural')
part.SectionAssignment(region=(part.cells,), sectionName='Stress-Section')

# 装配
assembly = stress_model.rootAssembly
instance = assembly.Instance(name='Stress-1', part=part, dependent=ON)

# 结构分析步
stress_model.StaticStep(
    name='Thermal-Load', 
    previous='Initial',
    timePeriod=1.0,
    initialInc=0.1
)

# 导入温度场（预定义场）
from odbAccess import openOdb
import os

if os.path.exists('Thermal-Job.odb'):
    temp_odb = openOdb('Thermal-Job.odb')
    temp_step = temp_odb.steps['Steady-State']
    temp_frame = temp_step.frames[-1]
    temp_field = temp_frame.fieldOutputs['NT11']
    
    # 创建预定义场
    predef_field = stress_model.PredefinedField(
        name='Temperature-Import',
        createStepName='Initial',
        region=assembly.allInstances['Stress-1'].sets,
        distributionType=FROM_FILE,
        fileName='Thermal-Job.odb',
        stepName='Steady-State',
        endStep=None,
        beginStep=None,
        beginFrame=None,
        endFrame=None,
        interpolate=ON,
        absoluteExteriorTolerance=0.0,
        exteriorTolerance=0.0
    )
    
    temp_odb.close()

# 对称边界条件
sym_x_faces = instance.faces.getByBoundingBox(xMin=-0.1, xMax=0.1)
sym_x_region = assembly.Set(name='Sym-X', faces=sym_x_faces)
stress_model.DisplacementBC(
    name='BC-Sym-X', 
    createStepName='Initial',
    region=sym_x_region,
    u1=0.0, u2=SET, u3=SET,
    ur1=SET, ur2=0.0, ur3=SET
)

sym_y_faces = instance.faces.getByBoundingBox(yMin=-0.1, yMax=0.1)
sym_y_region = assembly.Set(name='Sym-Y', faces=sym_y_faces)
stress_model.DisplacementBC(
    name='BC-Sym-Y', 
    createStepName='Initial',
    region=sym_y_region,
    u1=SET, u2=0.0, u3=SET,
    ur1=0.0, ur2=SET, ur3=SET
)

sym_z_faces = instance.faces.getByBoundingBox(zMin=-0.1, zMax=0.1)
sym_z_region = assembly.Set(name='Sym-Z', faces=sym_z_faces)
stress_model.DisplacementBC(
    name='BC-Sym-Z', 
    createStepName='Initial',
    region=sym_z_region,
    u1=SET, u2=SET, u3=0.0,
    ur1=SET, ur2=SET, ur3=0.0
)

# 内压载荷
inner_faces = instance.faces.getByBoundingCylinder(
    center1=(0, 0, 0), 
    center2=(0, length, 0), 
    radius=inner_radius + 1
)
inner_faces = [f for f in inner_faces 
               if abs(math.sqrt(f.getCentroid()[0]**2 + f.getCentroid()[1]**2) - inner_radius) < 5]
inner_region = assembly.Surface(name='Inner-Surface', side1Faces=inner_faces)

stress_model.Pressure(
    name='Internal-Pressure', 
    createStepName='Thermal-Load',
    region=inner_region,
    magnitude=inner_pressure
)

# 划分网格
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=SWEEP)
part.seedPart(size=mesh_size)
elem_type = mesh.ElemType(elemCode=C3D8R)  # 结构单元
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.generateMesh()

# 提交结构分析作业
stress_job = mdb.Job(name='Stress-Job', model='Thermal-Stress')
stress_job.submit()
stress_job.waitForCompletion()

# ========== 4. 后处理 ==========
print("=" * 60)
print("后处理：提取结果")
print("=" * 60)

odb = openOdb(path='Stress-Job.odb')
last_frame = odb.steps['Thermal-Load'].frames[-1]

# 提取应力
stress_field = last_frame.fieldOutputs['S']
max_stress = max([v.mises for v in stress_field.values])

# 提取位移
disp_field = last_frame.fieldOutputs['U']
max_disp = max([v.magnitude for v in disp_field.values])

# 提取温度（从热分析结果）
temp_odb = openOdb(path='Thermal-Job.odb')
temp_frame = temp_odb.steps['Steady-State'].frames[-1]
temp_field = temp_frame.fieldOutputs['NT11']
max_temp = max([v.data[0] for v in temp_field.values])
min_temp = min([v.data[0] for v in temp_field.values])

print(f"最大温度: {max_temp:.2f} °C")
print(f"最小温度: {min_temp:.2f} °C")
print(f"最大位移: {max_disp:.4f} mm")
print(f"最大Mises应力: {max_stress:.2f} MPa")
print("=" * 60)

# 理论估算（简化）
# 热应力 ≈ E * alpha * delta_T / (1-nu)
delta_T = max_temp - min_temp
theoretical_thermal_stress = E * alpha * delta_T / (1 - nu)
print(f"理论热应力估算: {theoretical_thermal_stress:.2f} MPa")

odb.close()
temp_odb.close()
```

---

## 四、运行与验证

### 4.1 运行脚本

保存为 `thermal_stress.py`，然后在Abaqus CAE中运行。

**注意**：这个脚本会运行两个分析（热传导 + 结构），可能需要几分钟时间。

### 4.2 预期结果

| 结果 | 预期值 | 说明 |
|------|--------|------|
| 最大温度 | ~200°C | 内壁附近 |
| 最小温度 | ~80-100°C | 外壁附近 |
| 温度梯度 | 从内到外递减 | 稳态热传导 |
| 最大位移 | ~0.5-1mm | 热膨胀+内压 |
| 最大应力 | ~150-250 MPa | 热应力+内压 |

### 4.3 结果解读

1. **温度分布**：内壁温度高，外壁温度低，呈现非线性分布（因为对流边界）

2. **应力分布**：
   - 环向应力最大（圆筒的周向）
   - 热应力与内压应力叠加

3. **位移分布**：整体向外膨胀，内壁膨胀更多

---

## 五、关键技术点：顺序耦合分析

### 5.1 温度场导入

顺序耦合的核心是**如何把温度场传给结构分析**。

在Abaqus中，使用**预定义场（PredefinedField）**：

```python
# 从热分析ODB文件导入温度场
predef_field = stress_model.PredefinedField(
    name='Temperature-Import',
    createStepName='Initial',
    region=assembly.allInstances['Part-1'],
    distributionType=FROM_FILE,
    fileName='Thermal-Job.odb',  # 热分析结果文件
    stepName='Steady-State',       # 热分析步
    interpolate=ON                 # 插值
)
```

### 5.2 热膨胀材料

在结构分析中，材料需要开启热膨胀选项：

```python
mat.Elastic(table=((E, nu),))
mat.Expansion(table=((alpha,),))  # 关键：热膨胀系数
```

这样Abaqus会自动计算热应力：
$$\sigma = E \cdot \alpha \cdot (T - T_{ref})$$

其中 $T_{ref}$ 是参考温度，默认为0°C。

---

## 六、常见问题与解决

### 问题一：温度场导入失败

**原因**：热分析结果文件不存在或路径错误

**解决**：
1. 确认热分析作业成功完成（状态为Completed）
2. 检查ODB文件是否在正确目录
3. 确认stepName与热分析步名称一致

### 问题二：热应力为0

**原因**：材料未定义热膨胀系数

**解决**：
1. 确认代码中有 `mat.Expansion(table=((alpha,),))`
2. 确认温度场正确导入

### 问题三：应力值异常大

**原因**：单位不一致

**解决**：
1. 确认所有单位统一（N-mm-MPa-°C制）
2. 导热系数要转换单位（W/(m·K) → W/(mm·K)）
3. 对流系数要转换单位

---

## 结尾：系列的终点，实践的起点

恭喜你！完成了Abaqus Skills系列的全部五个案例！

让我们回顾一下这五篇文章：

1. **第一篇**：讨论了AI与CAE的现状与未来
2. **第二篇**：手把手教你配置AI助手
3. **第三篇**：入门案例——悬臂梁
4. **第四篇**：进阶案例——带孔板应力集中
5. **第五篇**：高级案例——热应力耦合

从简单到复杂，从理论到实践，你应该已经对AI辅助CAE仿真有了比较完整的认识。

**这只是起点，不是终点。**

Abaqus Skills项目还在持续更新中，未来会加入更多：
- 疲劳分析
- 动力学分析
- 复合材料
- 裂纹扩展（XFEM）
- 用户子程序（UMAT等）

如果你对这些高级话题感兴趣，欢迎持续关注这个项目。

---

## 最后的呼吁

如果这个系列对你有帮助，请：

1. **点赞、收藏** —— 这是对我最大的鼓励
2. **评论分享** —— 说出你的使用心得或问题
3. **Star一下** —— 给项目加点星星
   - GitHub: https://github.com/jasonanewcoder/abaqus_skills
   - Gitee: https://gitee.com/jasonfun1995/abaqus_skills

让我们一起，推动CAE行业进入AI时代！

---

**作者：JasonAn**
**欢迎关注我的专栏**
**我们江湖再见！**

---

*系列文章完结*
