# 案例二：AI辅助Abaqus仿真进阶 - 带孔板应力集中分析

## 引言：从简单到复杂的跨越

在上一篇文章中，我们完成了第一个入门案例：悬臂梁静力分析。那个案例虽然简单，但涵盖了CAE仿真最核心的流程：建模→材料→边界→载荷→网格→计算→验证。

但 реальной 工程中，问题往往没那么简单。

今天我们要面对的，是一个更贴近实际工业场景的问题：**应力集中**。

想象一下：你有一块钢板，上面有个圆孔。当你施加拉力时，你会发现孔边附近的应力远大于远离孔的地方。这种“应力放大”的现象，就叫做**应力集中**。

它有多重要？

> 几乎所有机械零件的失效，都发生在应力集中区域。螺栓孔、键槽、齿轮齿根、焊缝边缘……这些地方都是应力集中的“重灾区”。统计数据显示，80%以上的疲劳断裂起源于应力集中点。

让我们开始吧。

---

## 一、案例参数：带孔板在拉伸

### 1.1 问题描述

![图片：带孔板单向拉伸示意图]
```
        →σ=100MPa
    ┌─────────────────────┐
    │                     │
    │    ○  孔           │
    │                     │
    └─────────────────────┘
        (板厚 t=5mm)
```

一块矩形平板，中心有圆形通孔，在板的两端施加均匀拉应力。

### 1.2 关键参数

| 参数 | 数值 | 单位 |
|------|------|------|
| 板长L | 200 | mm |
| 板宽W | 100 | mm |
| 板厚t | 5 | mm |
| 孔径d | 20 | mm |
| 材料 | 铝合金6061 | - |
| 弹性模量E | 69000 | MPa |
| 泊松比ν | 0.33 | - |
| 远场应力σ | 100 | MPa |

### 1.3 理论背景：应力集中系数

对于无限大平板中的圆孔，弹性力学给出了精确解：

$$\sigma_{max} = \sigma_{\infty} \times (2 + \frac{d}{W})$$

其中：
- $\sigma_{max}$ 是孔边最大应力
- $\sigma_{\infty}$ 是远场应力
- $d$ 是孔径
- $W$ 是板宽

当 $d/W$ 很小时（薄板小孔），应力集中系数Kt ≈ 3.0。

也就是说，即使远场应力只有100MPa，孔边的最大应力可能达到300MPa！

**这就是应力集中最可怕的地方：它会让局部应力远超过材料的许用应力。**

---

## 二、利用对称性：四分之一模型

### 2.1 为什么要用对称模型？

这个案例如果我们用完整模型，网格数量会很多，计算时间长。但这块板有两个对称面：

1. **水平对称面**：板上下对称
2. **竖直对称面**：板左右对称（孔在正中间）

所以我们只需要建立 **四分之一模型**，可以节省75%的计算量！

### 2.2 对称边界条件

在对称面上，需要设置对称边界条件：

| 对称面 | 约束条件 |
|--------|----------|
| X=0（竖直对称面） | u1=0, ur2=0, ur3=0 |
| Y=0（水平对称面） | u2=0, ur1=0, ur3=0 |

其中：
- u1, u2, u3 是三个方向的位移
- ur1, ur2, ur3 是三个方向的转动

---

## 三、让AI生成脚本

### 3.1 给AI的指令

```
请帮我生成一个Abaqus Python脚本，进行带孔板的四分之一模型应力集中分析。

模型参数：
- 板尺寸：200mm × 100mm × 5mm（长×宽×厚）
- 孔径：20mm
- 材料：铝合金6061（E=69000 MPa，ν=0.33）
- 远场应力：100 MPa

要求：
1. 使用四分之一模型，利用对称性
2. 在X=0面设置对称边界条件（u1=0）
3. 在Y=0面设置对称边界条件（u2=0）
4. 在X=L面施加拉应力（用压力载荷）
5. 孔边进行局部网格加密
6. 计算并输出应力集中系数

请参考技能库中的模板生成代码。
```

### 3.2 AI生成的代码

```python
# -*- coding: utf-8 -*-
"""
带孔板应力集中分析（四分之一模型）
分析类型: 线弹性静力分析
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数（单位：mm）
plate_length = 200.0   # 板长（X方向）
plate_width = 100.0    # 板宽（Y方向）
plate_thickness = 5.0  # 板厚（Z方向）
hole_radius = 10.0     # 孔半径

# 材料参数（单位：MPa）
E = 69000.0           # 弹性模量（铝合金6061）
nu = 0.33             # 泊松比

# 载荷参数（单位：MPa）
applied_stress = 100.0  # 远场拉应力

# 网格参数
global_mesh_size = 8.0   # 全局网格大小
local_mesh_size = 1.0    # 孔边加密网格大小

# ========== 2. 创建模型 ==========
model = mdb.Model(name='Plate-with-Hole')

# 创建部件
part = model.Part(name='Quarter-Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# 创建草图
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)

# 绘制四分之一矩形（X≥0, Y≥0）
sketch.rectangle(point1=(0.0, 0.0), point2=(plate_length/2, plate_width/2))

# 绘制圆孔（圆心在原点）
sketch.CircleByCenterPerimeter(
    center=(0.0, 0.0),
    point1=(hole_radius, 0.0)
)

# 拉伸创建板
part.BaseSolidExtrude(sketch=sketch, depth=plate_thickness)

# 删除临时草图
del model.sketches['__profile__']

# ========== 3. 材料和截面 ==========
# 创建材料
material = model.Material(name='Aluminum-6061')
material.Elastic(table=((E, nu),))

# 创建截面
section = model.HomogeneousSolidSection(name='Plate-Section', 
                                         material='Aluminum-6061')

# 分配截面
part.SectionAssignment(region=(part.cells,), sectionName='Plate-Section')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)

# ========== 5. 分析步 ==========
model.StaticStep(name='Tension', previous='Initial', 
                timePeriod=1.0, initialInc=0.1, nlgeom=OFF)

# ========== 6. 边界条件（对称约束）==========
# X=0 面对称约束（竖直对称面）
# 约束U1（X方向位移）、UR2（Y轴转动）、UR3（Z轴转动）
sym_x_region = assembly.Set(
    name='Sym-X', 
    faces=instance.faces.getByBoundingBox(xMin=-0.1, xMax=0.1)
)
model.DisplacementBC(
    name='BC-Sym-X', 
    createStepName='Initial',
    region=sym_x_region,
    u1=0.0, u2=SET, u3=SET,
    ur1=SET, ur2=0.0, ur3=0.0
)

# Y=0 面对称约束（水平对称面）
# 约束U2（Y方向位移）、UR1（X轴转动）、UR3（Z轴转动）
sym_y_region = assembly.Set(
    name='Sym-Y', 
    faces=instance.faces.getByBoundingBox(yMin=-0.1, yMax=0.1)
)
model.DisplacementBC(
    name='BC-Sym-Y', 
    createStepName='Initial',
    region=sym_y_region,
    u1=SET, u2=0.0, u3=SET,
    ur1=0.0, ur2=SET, ur3=0.0
)

# ========== 7. 载荷（端面拉应力）==========
# 在X=L/2的面施加压力载荷
# 注意：实际是拉伸，用负号表示拉
load_region = assembly.Set(
    name='Load-Face',
    faces=instance.faces.getByBoundingBox(
        xMin=plate_length/2-0.1, xMax=plate_length/2+0.1
    )
)

# 计算载荷大小
# 1/4模型，载荷为总载荷的1/4
# 总载荷 = 应力 × 截面积 = 100 MPa × (100mm × 5mm) = 50000 N
# 1/4模型承受的载荷 = 50000 / 4 = 12500 N
total_force = applied_stress * plate_width * plate_thickness
quarter_force = total_force / 4

# 转换为面载荷
pressure = applied_stress  # MPa

model.Pressure(
    name='Tensile-Load', 
    createStepName='Tension',
    region=load_region,
    magnitude=pressure
)

# ========== 8. 网格划分（局部加密）==========
# 设置网格控制
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=FREE)

# 全局网格
part.seedPart(size=global_mesh_size)

# 孔边局部加密
# 选择孔边附近的边
hole_edges = part.edges.getByBoundingCylinder(
    center1=(0, 0, 0),
    center2=(0, 0, plate_thickness),
    radius=hole_radius * 2.0
)
part.seedEdgeBySize(edges=hole_edges, size=local_mesh_size, constraint=FINER)

# 设置单元类型（二阶六面体单元，提高精度）
elem_type = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))

# 划分网格
part.generateMesh()

# ========== 9. 提交作业 ==========
job = mdb.Job(name='Plate-Hole-Job', model='Plate-with-Hole')
job.submit()
job.waitForCompletion()

# ========== 10. 后处理 ==========
from odbAccess import openOdb
import numpy as np

odb = openOdb(path='Plate-Hole-Job.odb')
last_frame = odb.steps['Tension'].frames[-1]

# 提取应力结果
stress_field = last_frame.fieldOutputs['S']
max_stress = max([v.mises for v in stress_field.values])

# 计算应力集中系数
Kt = max_stress / applied_stress

print("=" * 60)
print("带孔板应力集中分析结果")
print("=" * 60)
print(f"远场应力: {applied_stress:.2f} MPa")
print(f"最大Mises应力: {max_stress:.2f} MPa")
print(f"应力集中系数 Kt: {Kt:.3f}")
print(f"理论值 Kt: 3.0 (无限大板)")
print(f"误差: {abs(Kt - 3.0)/3.0*100:.1f}%")
print("=" * 60)

odb.close()
```

---

## 四、运行与验证

### 4.1 运行脚本

保存为 `plate_with_hole.py`，然后在Abaqus CAE中运行：

```
File → Run Script → plate_with_hole.py
```

等待作业完成。

### 4.2 查看结果

运行脚本后，你应该能看到：

| 结果 | 数值 | 说明 |
|------|------|------|
| 远场应力 | 100 MPa | 施加的载荷 |
| 最大Mises应力 | ~280-300 MPa | 孔边应力 |
| 应力集中系数 Kt | 2.8-3.0 | 与理论值3.0接近 |

### 4.3 结果分析

1. **应力云图**：你应该能看到孔边呈现“红火”区域（高应力），远离孔的区域应力较低（蓝绿色）

2. **应力分布**：从孔边到远场，应力逐渐衰减

3. **应力集中系数**：计算值应该在2.8-3.0之间，与理论值3.0吻合

**为什么不是精确的3.0？**

因为我们的板不是“无限大板”。有限大的板边界会影响应力分布，使得实际应力集中系数略小于理论值。

---

## 五、关键技巧：局部网格加密

### 5.1 为什么需要局部加密？

看下面这个对比：

| 网格方案 | 网格数量 | 计算精度 |
|----------|----------|----------|
| 全局均匀网格（8mm） | ~2000 | 较差，孔边应力不准 |
| 局部加密（孔边1mm） | ~5000 | 精确 |

局部加密的核心思想是：**在应力梯度大的区域使用细网格，在应力平缓的区域使用粗网格**。

这样既保证计算精度，又节省计算时间。

### 5.2 如何选择加密区域？

在Abaqus中，常用的方法有：

1. **基于距离选择**：
```python
# 选择孔边一定范围内的边
hole_edges = part.edges.getByBoundingCylinder(
    center1=(0, 0, 0),
    center2=(0, 0, thickness),
    radius=hole_radius * 2.0  # 2倍孔半径范围内
)
```

2. **基于坐标选择**：
```python
# 选择X在0-20mm范围内的边
local_edges = part.edges.getByBoundingBox(xMin=0, xMax=20)
```

3. **手动选择**（在GUI中更直观）

---

## 六、常见问题与解决

### 问题一：网格划分失败

**原因**：几何有重叠或交叉

**解决**：
1. 检查草图是否正确绘制
2. 尝试调整网格控制参数
3. 尝试改变单元类型（从HEX改为TET）

### 问题二：应力集中系数偏低（<2.5）

**原因**：
1. 网格太粗，无法捕捉应力梯度
2. 孔边单元阶次太低

**解决**：
1. 减小孔边网格尺寸（local_mesh_size改为0.5或更小）
2. 使用二阶单元（C3D10而非C3D8R）

### 问题三：结果与理论值误差大（>10%）

**原因**：板不够大，边界效应明显

**解决**：
1. 增加板尺寸
2. 或使用更大比例的模型（如1/2模型而非1/4模型）

---

## 结尾：应力集中有多可怕？

回到文章开头的那个问题：应力集中有多可怕？

一块远场应力只有100MPa的板，因为一个20mm的孔，孔边应力达到了300MPa。如果这是Q235钢（屈服强度235MPa），板就已经屈服了；如果这是脆性材料，可能直接就断了。

**这就是为什么结构设计规范中，对应力集中区域有额外的加强要求：加大圆角、使用加强筋、采用多孔分布……**

**思考题**：如果你想把圆孔改成椭圆孔（长轴水平），应力集中系数会变大还是变小？

答案会在下期揭晓。

**下期预告**

案例三我们将进入高级领域：**热应力耦合分析**。这将是一个真正的多物理场问题，你需要同时考虑：

- 热传导（温度场分布）
- 热-结构耦合（温度导致膨胀）
- 边界条件（对流散热）

这也将是我们这个系列的最后一个案例。敬请期待！

---

**作者：JasonAn，欢迎关注我的专栏**

**如果有任何问题，欢迎在评论区留言。觉得有帮助的话，点个赞再走~**

**项目地址：https://github.com/jasonanewcoder/abaqus_skills**
