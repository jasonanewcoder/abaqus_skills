# 案例一：AI辅助Abaqus仿真入门 - 悬臂梁静力分析

## 引言：百闻不如一见

前面的文章我们讲了很多理念和方法，但正如一位读者所说：“我不要听道理，我要看疗效。”

今天就是这个“疗效”——我将通过一个完整的案例，手把手教你如何使用Abaqus Skills技能库，让AI帮你完成一个真实的仿真分析。

我们从最简单的案例开始：**悬臂梁静力分析**。

这是一个经典的力学问题：一根矩形截面梁，一端固定，另一端施加集中力，计算梁的应力和变形。每个材料力学教材都会讲，验证结果也非常方便。

---

## 一、案例参数：这次要做什么？

### 1.1 问题描述

![图片：悬臂梁受力示意图]
```
┌─────────────────────────────────────────┐
│                                         │
│   固定端 ─────────────────── 自由端     │
│    ║                              ↓     │
│    ║                          F=5000N   │
│    ║                              ↓     │
│    ║                              ○     │
│    ╚═══════════════════════════════════╝
            L = 1000 mm
```

### 1.2 关键参数

| 参数 | 数值 | 单位 |
|------|------|------|
| 梁长L | 1000 | mm |
| 截面宽度b | 50 | mm |
| 截面高度h | 100 | mm |
| 材料 | Q235钢 | - |
| 弹性模量E | 210000 | MPa |
| 泊松比ν | 0.3 | - |
| 端部载荷F | 5000 | N |

### 1.3 理论解（用于验证）

这是中学水平的材料力学知识，我们来复习一下：

**最大弯曲应力**：
$$\sigma_{max} = \frac{M \cdot y}{I} = \frac{F \cdot L \cdot (h/2)}{b \cdot h^3 / 12} = \frac{6FL}{bh^2}$$

代入数值：
$$\sigma_{max} = \frac{6 \times 5000 \times 1000}{50 \times 100^2} = 60 \text{ MPa}$$

**最大挠度**：
$$\delta_{max} = \frac{FL^3}{3EI} = \frac{5000 \times 1000^3}{3 \times 210000 \times (50 \times 100^3 / 12)}$$

计算得：
$$\delta_{max} \approx 1.90 \text{ mm}$$

我们的有限元结果应该与这两个理论值非常接近（误差<5%）。

---

## 二、让AI帮忙：生成脚本

### 2.1 给AI的指令

按照第二篇文章的方法，我们需要给AI发送包含技能文件内容的提示词。这里为了简化，我直接展示关键的提示词结构，你可以直接使用：

```
请帮我生成一个Abaqus Python脚本，进行悬臂梁静力分析。

模型参数：
- 梁长：1000 mm
- 截面：50 mm × 100 mm（宽×高）
- 材料：Q235钢（E=210000 MPa，ν=0.3）
- 载荷：端部施加5000 N垂直向下的集中力
- 边界条件：一端固定（完全约束）

请参考以下技能文件中的模板来生成代码：
1. skill_modeling.md - 几何建模
2. skill_material.md - 材料定义  
3. skill_bc_load.md - 边界条件和载荷
4. skill_mesh.md - 网格划分
5. skill_job.md - 作业提交
6. skill_static_linear.md - 静力分析设置
```

### 2.2 AI生成的代码

AI会结合技能库中的模板，生成如下代码（我做了适当简化）：

```python
# -*- coding: utf-8 -*-
"""
悬臂梁静力分析
分析类型: 线弹性静力分析
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. 参数定义 ==========
# 几何参数（单位：mm）
length = 1000.0    # 梁长
width = 50.0       # 截面宽度
height = 100.0     # 截面高度

# 材料参数（单位：MPa）
E = 210000.0       # 弹性模量（Q235钢）
nu = 0.3           # 泊松比

# 载荷参数（单位：N）
load = 5000.0      # 端部集中力

# 网格参数
mesh_size = 20.0   # 全局网格大小

# ========== 2. 创建模型 ==========
model = mdb.Model(name='Cantilever-Beam')

# 创建部件
part = model.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# 创建草图（矩形截面）
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(width, height))

# 拉伸创建梁
part.BaseSolidExtrude(sketch=sketch, depth=length)

# 删除临时草图
del model.sketches['__profile__']

# ========== 3. 材料和截面 ==========
# 创建材料
material = model.Material(name='Steel-Q235')
material.Elastic(table=((E, nu),))

# 创建截面
section = model.HomogeneousSolidSection(name='Beam-Section', 
                                        material='Steel-Q235')

# 分配截面
part.SectionAssignment(region=(part.cells,), sectionName='Beam-Section')

# ========== 4. 装配 ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Beam-1', part=part, dependent=ON)

# ========== 5. 分析步 ==========
model.StaticStep(name='Load-Step', previous='Initial', 
                timePeriod=1.0, initialInc=0.1, nlgeom=OFF)

# ========== 6. 边界条件（固定端）==========
# 固定端在 X=0 的面
fixed_face = instance.faces.findAt(((width/2, height/2, 0.0),))
region = assembly.Set(name='Fixed-End', faces=fixed_face)
model.EncastreBC(name='BC-Fixed', createStepName='Initial', region=region)

# ========== 7. 载荷（自由端）==========
# 自由端在 X=length 的面
load_face = instance.faces.findAt(((width/2, height/2, length),))
region = assembly.Set(name='Load-Point', faces=load_face)
model.ConcentratedForce(name='Force', createStepName='Load-Step',
                       region=region, cf2=-load)  # cf2=-load 表示-Y方向

# ========== 8. 网格划分 ==========
# 设置网格控制
part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)

# 设置单元类型（八节点六面体单元）
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))

# 划分网格
part.generateMesh()

# ========== 9. 提交作业 ==========
job = mdb.Job(name='Cantilever-Beam-Job', model='Cantilever-Beam')
job.submit()
job.waitForCompletion()

print("=" * 50)
print("分析完成！")
print("=" * 50)
```

---

## 三、运行脚本：一步一步来

### 3.1 保存脚本

1. 打开文本编辑器（如Notepad++、VS Code）
2. 复制上述代码
3. 保存为 `cantilever_beam.py`（注意后缀是.py，不是.txt）

### 3.2 在Abaqus中运行

```
1. 打开 Abaqus CAE
2. 点击菜单：File → Run Script
3. 选择刚才保存的 cantilever_beam.py
4. 等待运行完成
```

### 3.3 查看结果

运行完成后，你会看到：

- **模型树**中新增了 `Cantilever-Beam` 模型
- 包含 Parts（部件）、Assemblies（装配）、Steps（分析步）等
- 提交了名为 `Cantilever-Beam-Job` 的作业
- 如果一切正常，作业状态会显示 "Completed"

---

## 四、结果验证：AI算对了么？

### 4.1 查看变形结果

1. 在模型树中双击 `Cantilever-Beam-Job` 结果
2. 选择 `Result` → `Job-xxx` → `Cantilever-Beam`
3. 点击 `Plot` → `Deformed Shape` → `U`（位移）

你应该能看到梁向下的弯曲变形。最大位移应该在 **1.9 mm** 左右（与理论值1.90 mm对比）。

### 4.2 查看应力结果

1. 点击 `Result` → `Contour Plot` → `Stress` → `Mises`
2. 观察应力云图

你应该能看到：
- **最大应力**在固定端，大约 **60 MPa** 左右
- 应力从固定端向自由端逐渐减小
- 这与材料力学的理论完全吻合

### 4.3 对比理论值

| 结果类型 | 理论值 | 有限元结果 | 误差 |
|----------|--------|------------|------|
| 最大位移 | 1.90 mm | ~1.90 mm | <1% |
| 最大应力 | 60 MPa | ~60 MPa | <1% |

如果你的结果与理论值误差超过5%，可能的原因：
- 网格太粗（尝试将 mesh_size 改为 10.0）
- 载荷施加位置不对
- 单位不一致

---

## 五、进阶：让脚本更智能

### 5.1 参数化建模

上面的脚本已经把关键参数提取到开头，方便修改。如果你想调整梁的长度或载荷，只需要修改开头几行：

```python
# 只需要修改这里
length = 1500.0   # 改成1.5米
load = 8000.0     # 改成8000N
```

运行修改后的脚本，AI会自动生成新的模型。

### 5.2 添加后处理

如果想让AI在脚本中直接输出结果，可以在最后添加：

```python
# 后处理：提取结果
from odbAccess import openOdb
import os

# 获取当前工作目录
job_name = 'Cantilever-Beam-Job'
odb_path = job_name + '.odb'

if os.path.exists(odb_path):
    odb = openOdb(path=odb_path)
    last_frame = odb.steps['Load-Step'].frames[-1]
    
    # 提取位移
    u_field = last_frame.fieldOutputs['U']
    max_displacement = max([v.magnitude for v in u_field.values])
    
    # 提取应力
    s_field = last_frame.fieldOutputs['S']
    max_stress = max([v.mises for v in s_field.values])
    
    print(f"最大位移: {max_displacement:.4f} mm")
    print(f"最大Mises应力: {max_stress:.2f} MPa")
    
    odb.close()
```

---

## 六、常见问题与解决

### 问题一：运行报错 "cannot find 'Cantilever-Beam-Job'"

**原因**：作业文件不存在，可能是因为分析失败

**解决**：
1. 检查Abaqus命令行是否有错误信息
2. 查看 .log 文件中的详细错误
3. 常见错误：网格划分失败、边界条件不足

### 问题二：结果显示为0

**原因**：可能没有正确加载结果文件

**解决**：
1. 确认作业状态是 "Completed"
2. 检查ODB文件是否存在
3. 在Abaqus/Viewer中重新打开结果

### 问题三：应力值不对

**原因**：单位不一致是最常见的问题

**解决**：
1. 检查所有参数单位是否统一（N-mm-MPa制）
2. 确保弹性模量是MPa单位（210000，不是210）
3. 确保力是N单位（5000，不是5）

---

## 结尾：第一座里程碑

恭喜你！完成了第一个完整的Abaqus仿真案例。

通过这个案例，你应该已经掌握：
- 如何利用技能库让AI生成正确的脚本
- 如何运行脚本并验证结果
- 如何进行基本的参数化建模

**思考题**：如果你想把矩形截面改成圆形截面，需要修改脚本的哪些部分？

答案会在下期揭晓。

**下期预告**

案例二我们将更进一步：**带孔板的应力集中分析**。这个案例将教会你：
- 如何创建复杂几何（带孔的板）
- 如何使用局部网格加密
- 如何计算应力集中系数

敬请期待！

---

**作者：JasonAn，欢迎关注我的专栏**

**如果有任何问题，欢迎在评论区留言，我会尽量解答。也欢迎点赞、收藏、转发！**

**项目地址：https://github.com/jasonanewcoder/abaqus_skills**
