# 技能：网格划分 (Meshing)

## 📖 功能描述

定义网格控制参数、设置单元类型、生成有限元网格。

## 🔧 API 参考

### 核心类和方法

```python
# 设置种子（单元大小）
part.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)

# 边布种
part.seedEdgeBySize(edges=edges, size=5.0, deviationFactor=0.1)

# 设置网格控制
part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)

# 设置单元类型
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))

# 生成网格
part.generateMesh()
```

## 💻 代码模板

### 模板 1：自动网格划分

```python
# ========== 网格参数 ==========
element_size = 10.0       # 全局单元尺寸 (mm)
deviation_factor = 0.1    # 偏差因子
min_size_factor = 0.1     # 最小尺寸因子

# ========== 生成网格 ==========
part = model.parts['Part-1']

# 1. 设置种子
part.seedPart(
    size=element_size,
    deviationFactor=deviation_factor,
    minSizeFactor=min_size_factor,
    constraint=FINER
)

# 2. 生成网格
part.generateMesh()

print(f"网格生成完成，单元数: {len(part.elements)}")
print(f"节点数: {len(part.nodes)}")
```

### 模板 2：结构化网格（六面体）

```python
# ========== 结构化六面体网格 ==========
# 适用于可扫掠的几何

part = model.parts['Part-1']

# 设置网格控制（六面体）
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,           # 六面体单元
    technique=STRUCTURED,    # 结构化网格
    algorithm=MEDIAL_AXIS    # 或 ADVANCING_FRONT
)

# 设置种子
part.seedPart(size=5.0, deviationFactor=0.1)

# 设置单元类型
elem_type = mesh.ElemType(
    elemCode=C3D8R,          # 减缩积分六面体单元
    elemLibrary=STANDARD,
    kinematicSplit=AVERAGE_STRAIN,
    secondOrderAccuracy=OFF,
    hourglassControl=DEFAULT,
    distortionControl=DEFAULT
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

# 生成网格
part.generateMesh()
```

### 模板 3：扫掠网格

```python
# ========== 扫掠网格 ==========
# 适用于拉伸/旋转几何

part = model.parts['Part-1']

# 设置扫掠网格控制
cells = part.cells
part.setMeshControls(
    regions=cells,
    elemShape=HEX,
    technique=SWEEP,         # 扫掠技术
    algorithm=MEDIAL_AXIS
)

# 设置扫掠路径（可选）
# part.setSweepPath(region=cell, edge=edge, sense=FORWARD)

# 设置种子
part.seedPart(size=5.0)

# 设置单元类型
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))

part.generateMesh()
```

### 模板 4：自由网格（四面体）

```python
# ========== 自由四面体网格 ==========
# 适用于复杂几何

part = model.parts['Part-1']

# 设置网格控制（四面体）
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=TET,           # 四面体单元
    technique=FREE,          # 自由网格
    algorithm=ADVANCING_FRONT # 或 DELAUNAY
)

# 设置种子
part.seedPart(size=3.0, deviationFactor=0.1)

# 设置单元类型（二阶四面体）
elem_type = mesh.ElemType(
    elemCode=C3D10,          # 二阶四面体单元
    elemLibrary=STANDARD,
    secondOrderAccuracy=ON
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

part.generateMesh()
```

### 模板 5：壳体网格

```python
# ========== 壳体网格划分 ==========
part = model.parts['Shell-Part']

# 设置网格控制（四边形）
all_faces = part.faces
part.setMeshControls(
    regions=all_faces,
    elemShape=QUAD,          # 四边形单元
    technique=FREE,          # 或 STRUCTURED
    algorithm=MEDIAL_AXIS
)

# 边布种
edges = part.edges
part.seedEdgeBySize(edges=edges, size=5.0)

# 设置壳单元类型
elem_type = mesh.ElemType(
    elemCode=S4R,            # 减缩积分壳单元
    elemLibrary=STANDARD,
    hourglassControl=DEFAULT
)
part.setElementType(regions=(all_faces,), elemTypes=(elem_type,))

part.generateMesh()
```

### 模板 6：梁单元网格

```python
# ========== 梁单元网格 ==========
part = model.parts['Beam-Part']

# 边布种
all_edges = part.edges
part.seedEdgeByNumber(edges=all_edges, number=10)  # 每条边10个单元

# 设置梁单元类型
elem_type = mesh.ElemType(
    elemCode=B31,            # 线性梁单元 (或 B32 二阶)
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_edges,), elemTypes=(elem_type,))

part.generateMesh()
```

### 模板 7：局部加密

```python
# ========== 局部网格加密 ==========
part = model.parts['Part-1']

# 全局种子
part.seedPart(size=10.0)

# 局部加密 - 通过边布种
# 选择要加密的边
refine_edges = part.edges.findAt(
    ((50.0, 0.0, 10.0),),
    ((50.0, 50.0, 10.0),)
)

# 局部加密
part.seedEdgeBySize(
    edges=refine_edges,
    size=2.0,                # 局部单元尺寸
    deviationFactor=0.1,
    minSizeFactor=0.1,
    constraint=FINER
)

# 设置单元类型并生成网格
cells = part.cells
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))
part.generateMesh()
```

### 模板 8：分区后网格

```python
# ========== 分区后网格划分 ==========
# 先对几何分区，再划分结构化网格

part = model.parts['Part-1']

# 1. 创建分区平面
cells = part.cells
partition_face = part.faces[0]
partition_edge = part.edges[0]

# 通过草图分区
sketch = model.ConstrainedSketch(name='__partition__', sheetSize=200.0)
sketch.Line(point1=(0.0, 0.0), point2=(100.0, 0.0))

part.PartitionCellBySketch(
    sketch=sketch,
    cells=cells,
    sketchPlane=partition_face,
    sketchUpEdge=partition_edge
)

# 2. 对分区后的区域分别设置网格
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED
)

part.seedPart(size=5.0)
part.generateMesh()
```

## 🎯 单元类型速查表

### 实体单元 (3D)

| 单元代码 | 描述 | 适用场景 |
|---------|------|---------|
| C3D8R | 六面体，线性，减缩积分 | 通用，计算效率高 |
| C3D8 | 六面体，线性，完全积分 | 避免沙漏，弯曲问题 |
| C3D8I | 六面体，非协调模式 | 弯曲问题，粗网格 |
| C3D20R | 六面体，二阶，减缩积分 | 高精度，应力集中 |
| C3D20 | 六面体，二阶，完全积分 | 最高精度 |
| C3D4 | 四面体，线性 | 复杂几何，自由网格 |
| C3D10 | 四面体，二阶 | 复杂几何，高精度 |
| C3D6 | 三棱柱，线性 | 过渡网格 |
| C3D15 | 三棱柱，二阶 | 过渡网格，高精度 |

### 壳单元 (2D)

| 单元代码 | 描述 | 适用场景 |
|---------|------|---------|
| S4R | 四边形，线性，减缩积分 | 通用壳体分析 |
| S4 | 四边形，线性，完全积分 | 厚壳，避免沙漏 |
| S8R | 四边形，二阶，减缩积分 | 高精度壳体分析 |
| S3R | 三角形，线性 | 复杂几何过渡 |
| S3 | 三角形，线性，完全积分 | 小应变 |

### 梁单元 (1D)

| 单元代码 | 描述 | 适用场景 |
|---------|------|---------|
| B31 | 线性梁 | 通用梁分析 |
| B32 | 二阶梁 | 高精度，分布载荷 |
| B31H | 线性梁（杂交） | 不可弯曲变形 |
| B32H | 二阶梁（杂交） | 不可弯曲变形 |
| B33 | 三次梁 (Euler-Bernoulli) | 细长梁 |

## 🔧 高级网格控制

### 网格质量检查

```python
# 获取网格质量指标
mesh_stats = part.getMeshStats()

# 检查单元质量
elem_quality = part.quality

# 检查未划分网格的区域
unmeshed_regions = part.getUnmeshedRegions()
```

### 删除网格

```python
# 删除整个网格
part.deleteMesh()

# 删除特定区域的网格
part.deleteMesh(regions=cells)
```

### 网格过渡技术

```python
# 使用偏置种子实现网格过渡
edge = part.edges[0]

# 双偏置（两端密，中间疏）
part.seedEdgeByBias(
    biasMethod=SINGLE,
    end1Edges=(edge,),
    ratio=3.0,               # 两端单元尺寸比
    number=20                # 单元数
)

# 单偏置（一端密，一端疏）
part.seedEdgeByBias(
    biasMethod=DOUBLE,
    end1Edges=(edge,),
    end2Edges=(edge2,),
    minSize=1.0,
    maxSize=5.0,
    number=15
)
```

## 💡 最佳实践

1. **单元选择原则**：
   - 优先使用六面体单元（C3D8R）
   - 复杂几何使用二阶四面体（C3D10）
   - 避免使用线性四面体（C3D4）

2. **网格密度**：
   - 关注区域局部加密（应力集中、接触区）
   - 至少 3-4 层单元描述厚度方向
   - 避免单元长宽比过大

3. **沙漏控制**：
   - 减缩积分单元需要检查沙漏能
   - 沙漏能应小于内能的 5%

4. **收敛检查**：
   - 粗网格 → 细网格对比
   - 检查结果对网格的敏感性

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 网格生成失败 | 几何质量差 | 修复几何，使用虚拟拓扑 |
| 单元质量差 | 扭曲或畸形单元 | 调整种子，改进几何 |
| 沙漏模式 | 减缩积分单元变形模式 | 启用沙漏控制，细化网格 |
| 体积自锁 | 完全积分单元不可压材料 | 使用杂交单元或减缩积分 |
| 剪切自锁 | 线性单元弯曲问题 | 使用非协调单元或二阶单元 |
