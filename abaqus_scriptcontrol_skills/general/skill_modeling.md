# 技能：几何建模 (Geometry Modeling)

## 📖 功能描述

创建 Abaqus 模型中的几何部件(Part)，包括基于草图的拉伸、旋转、扫掠等建模方法。

## 🔧 API 参考

### 核心类和方法

```python
# 创建部件
mdb.Model(name='Model-1')
model = mdb.models['Model-1']

# 基于草图创建三维实体
part = model.Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# ... 绘制草图 ...
part.BaseSolidExtrude(sketch=sketch, depth=100.0)

# 创建壳体
part.BaseShellExtrude(sketch=sketch, depth=100.0)

# 旋转创建
part.BaseSolidRevolve(sketch=sketch, angle=360.0, flipRevolveDirection=OFF)
```

## 💻 代码模板

### 模板 1：长方体

```python
# ========== 1. 长方体参数 ==========
length = 100.0   # mm, X方向长度
width = 50.0     # mm, Y方向宽度
height = 20.0    # mm, Z方向高度

# ========== 2. 创建长方体 ==========
model = mdb.models['Model-1']
part = model.Part(name='Block', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# 创建草图
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))

# 拉伸
part.BaseSolidExtrude(sketch=sketch, depth=height)

# 删除草图（可选）
del model.sketches['__profile__']
```

### 模板 2：圆柱体

```python
# ========== 圆柱体参数 ==========
radius = 25.0    # mm, 圆柱半径
height = 100.0   # mm, 圆柱高度

# ========== 创建圆柱体 ==========
model = mdb.models['Model-1']
part = model.Part(name='Cylinder', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# 创建圆形草图
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(radius, 0.0))

# 拉伸
part.BaseSolidExtrude(sketch=sketch, depth=height)

del model.sketches['__profile__']
```

### 模板 3：空心圆筒

```python
# ========== 圆筒参数 ==========
outer_radius = 50.0   # mm, 外半径
inner_radius = 45.0   # mm, 内半径
height = 200.0        # mm, 高度

# ========== 创建空心圆筒 ==========
model = mdb.models['Model-1']
part = model.Part(name='Pipe', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# 外圆
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outer_radius, 0.0))
# 内圆（孔）
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(inner_radius, 0.0))

part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']
```

### 模板 4：L 形支架

```python
# ========== L 形支架参数 ==========
leg1_length = 100.0   # mm
leg1_width = 50.0     # mm
leg1_thickness = 10.0 # mm
leg2_length = 80.0    # mm
leg2_width = 50.0     # mm
leg2_thickness = 10.0 # mm

# ========== 创建 L 形支架 ==========
model = mdb.models['Model-1']
part = model.Part(name='L-Bracket', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# 绘制 L 形轮廓
sketch.Line(point1=(0.0, 0.0), point2=(leg1_length, 0.0))
sketch.Line(point1=(leg1_length, 0.0), point2=(leg1_length, leg1_width))
sketch.Line(point1=(leg1_length, leg1_width), point2=(leg2_thickness, leg1_width))
sketch.Line(point1=(leg2_thickness, leg1_width), point2=(leg2_thickness, leg1_width + leg2_length))
sketch.Line(point1=(leg2_thickness, leg1_width + leg2_length), point2=(0.0, leg1_width + leg2_length))
sketch.Line(point1=(0.0, leg1_width + leg2_length), point2=(0.0, 0.0))

part.BaseSolidExtrude(sketch=sketch, depth=leg1_thickness)
del model.sketches['__profile__']
```

### 模板 5：球体

```python
# ========== 球体参数 ==========
radius = 50.0   # mm

# ========== 创建球体 ==========
# 方法：半圆旋转
model = mdb.models['Model-1']
part = model.Part(name='Sphere', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# 绘制半圆（使用圆弧）
sketch.ArcByCenterEnds(center=(0.0, 0.0), point1=(-radius, 0.0), point2=(radius, 0.0), direction=CLOCKWISE)
# 封闭轮廓
sketch.Line(point1=(-radius, 0.0), point2=(radius, 0.0))

part.BaseSolidRevolve(sketch=sketch, angle=360.0, flipRevolveDirection=OFF)
del model.sketches['__profile__']
```

## 📝 草图绘制方法

### 基本几何图形

```python
sketch = model.ConstrainedSketch(name='sketch', sheetSize=200.0)

# 点
sketch.Point(point=(x, y))

# 直线
sketch.Line(point1=(x1, y1), point2=(x2, y2))

# 矩形
sketch.rectangle(point1=(x1, y1), point2=(x2, y2))

# 圆（圆心+圆上一点）
sketch.CircleByCenterPerimeter(center=(cx, cy), point1=(px, py))

# 圆（圆心+半径）
sketch.circle(centerPoint=(cx, cy), point1=(cx + r, cy))

# 圆弧（圆心+端点）
sketch.ArcByCenterEnds(center=(cx, cy), point1=(x1, y1), point2=(x2, y2), direction=CLOCKWISE)

# 椭圆
sketch.EllipseByCenterPerimeter(center=(cx, cy), axisPoint1=(ax1, ay1), axisPoint2=(ax2, ay2))

# 多边形（外接圆）
sketch.regularPolygonByCircumscribeCircle(
    centerPoint=(cx, cy),
    pointOnCircle=(px, py),
    numberOfSides=6
)
```

### 约束和尺寸

```python
# 固定约束
sketch.FixedConstraint(entity=vertex)

# 重合约束
sketch.CoincidentConstraint(entity1=vertex1, entity2=vertex2)

# 水平约束
sketch.HorizontalConstraint(entity=line)

# 垂直约束
sketch.VerticalConstraint(entity=line)

# 平行约束
sketch.ParallelConstraint(entity1=line1, entity2=line2)

# 垂直约束（几何）
sketch.PerpendicularConstraint(entity1=line1, entity2=line2)

# 等长约束
sketch.EqualLengthConstraint(entity1=line1, entity2=line2)

# 尺寸标注
sketch.Dimension(entity=line, textPoint=(x, y), value=length)
sketch.RadialDimension(curve=circle, textPoint=(x, y), radius=radius)
```

## 🔍 选择几何对象

```python
# 选择所有单元
cells = part.cells

# 根据索引选择
cell = part.cells[0]

# 根据坐标选择（选择包含某点的单元）
selected_cells = part.cells.findAt(((x, y, z),))

# 选择面
faces = part.faces
face = part.faces.findAt(((x, y, z),))

# 选择边
edges = part.edges
edge = part.edges.findAt(((x, y, z),))

# 选择顶点
vertices = part.vertices
vertex = part.vertices.findAt(((x, y, z),))

# 选择特征线（用于分割）
edges_by_angle = part.edges.getSequenceFromMask(mask=('[#1 ]',),)
```

## 🎨 特征操作

### 切割（Cut）

```python
# 拉伸切割
part.CutExtrude(sketchPlane=face, sketchUpEdge=edge, 
                sketchPlaneSide=SIDE1, sketchOrientation=RIGHT,
                sketch=sketch, depth=cut_depth, flipExtrudeDirection=OFF)

# 旋转切割
part.CutRevolve(sketchPlane=face, sketchUpEdge=edge,
                sketchPlaneSide=SIDE1, sketchOrientation=RIGHT,
                sketch=sketch, angle=90.0)

# 扫掠切割
part.CutSweep(pathEdge=path_edge, sketch=sketch)
```

### 圆角和倒角

```python
# 圆角
edges_for_fillet = part.edges.findAt(((x1, y1, z1),), ((x2, y2, z2),))
part.Round(radius=5.0, edgeList=edges_for_fillet)

# 倒角
edges_for_chamfer = part.edges.findAt(((x, y, z),))
part.Chamfer(length=2.0, length2=2.0, edgeList=edges_for_chamfer)
```

### 抽壳

```python
# 抽壳（移除面）
face_to_remove = part.faces.findAt(((x, y, z),))
part.Shell(thickness=2.0, faceList=(face_to_remove,))

# 抽壳所有面
part.SolidExtrude(...)  # 先创建实体
part.Shell(thickness=2.0, faceList=part.faces)
```

### 镜像

```python
# 镜像特征
mirror_plane = part.datums[datum_plane_id]
part.Mirror(mirrorPlane=mirror_plane, featureList=(feature1, feature2))
```

### 阵列

```python
# 线性阵列
edge_for_direction = part.edges[0]
part.LinearPattern(featureList=(feature,), direction1=edge_for_direction,
                   number1=3, spacing1=50.0)

# 圆周阵列
axis_for_rotation = part.datums[datum_axis_id]
part.CircularPattern(featureList=(feature,), axis=axis_for_rotation,
                     number=6, totalAngle=360.0)
```

## 💡 最佳实践

1. **命名规范**：使用有意义的部件名称，如 `'Beam_100x50'`
2. **单位一致性**：所有尺寸使用统一单位（推荐 mm）
3. **草图清理**：创建完成后删除临时草图 `del model.sketches['__profile__']`
4. **参数化**：将尺寸定义为变量，便于修改
5. **验证几何**：复杂模型创建后检查是否有自由边、短边等问题

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 草图未封闭 | 轮廓线未闭合 | 检查所有线段端点是否重合 |
| 自相交 | 草图线交叉 | 修改草图避免交叉 |
| 零厚度 | 拉伸深度为0 | 检查深度参数 |
| 无效选择 | findAt 坐标不在目标上 | 调整坐标或使用索引选择 |
