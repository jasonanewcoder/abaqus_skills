# 技能：边界条件与载荷 (Boundary Conditions & Loads)

## 📖 功能描述

定义模型的边界条件（位移约束）和外部载荷（力、压力、温度等）。

## 🔧 API 参考

### 核心类和方法

```python
# 创建边界条件
model.DisplacementBC(name='BC-Fixed', createStepName='Initial', 
                     region=region, u1=0.0, u2=0.0, u3=0.0)

# 创建集中力
model.ConcentratedForce(name='Load-Force', createStepName='Step-1',
                        region=region, cf2=-1000.0)

# 创建压力
model.Pressure(name='Load-Pressure', createStepName='Step-1',
               region=region, magnitude=10.0)

# 创建体力
model.BodyForce(name='Load-Gravity', createStepName='Step-1',
                region=region, comp3=-9800.0)
```

## 💻 代码模板

### 模板 1：固定约束（全约束）

```python
# ========== 选择约束区域 ==========
assembly = model.rootAssembly
instance = assembly.instances['Part-1-1']

# 方法1：通过坐标选择面
fixed_faces = instance.faces.findAt(((0.0, 25.0, 10.0),))
region = assembly.Set(name='Fixed-End', faces=fixed_faces)

# 方法2：通过索引选择
# region = assembly.Set(name='Fixed-End', faces=instance.faces[0:1])

# ========== 创建固定约束 ==========
model.DisplacementBC(
    name='BC-Fixed',
    createStepName='Initial',    # 边界条件在Initial步创建
    region=region,
    u1=0.0,                      # X方向位移 = 0
    u2=0.0,                      # Y方向位移 = 0
    u3=0.0,                      # Z方向位移 = 0
    ur1=UNSET,                   # 转动不约束
    ur2=UNSET,
    ur3=UNSET,
    amplitude=UNSET,
    fixed=OFF,
    distributionType=UNIFORM,
    fieldName='',
    localCsys=None
)
```

### 模板 2：对称约束

```python
# ========== X-Y平面对称（Z=0平面） ==========
# 约束Z方向位移和绕X、Y轴转动
sym_faces = instance.faces.findAt(((50.0, 25.0, 0.0),))
region = assembly.Set(name='Symmetry-XY', faces=sym_faces)

model.DisplacementBC(
    name='BC-Symmetry-XY',
    createStepName='Initial',
    region=region,
    u1=UNSET,
    u2=UNSET,
    u3=0.0,          # Z方向固定
    ur1=0.0,         # 绕X轴转动固定
    ur2=0.0,         # 绕Y轴转动固定
    ur3=UNSET
)

# ========== X-Z平面对称（Y=0平面） ==========
region = assembly.Set(name='Symmetry-XZ', faces=instance.faces.findAt(((50.0, 0.0, 10.0),)))
model.DisplacementBC(
    name='BC-Symmetry-XZ',
    createStepName='Initial',
    region=region,
    u1=UNSET,
    u2=0.0,          # Y方向固定
    u3=UNSET,
    ur1=0.0,         # 绕X轴转动固定
    ur2=UNSET,
    ur3=0.0          # 绕Z轴转动固定
)

# ========== Y-Z平面对称（X=0平面） ==========
region = assembly.Set(name='Symmetry-YZ', faces=instance.faces.findAt(((0.0, 25.0, 10.0),)))
model.DisplacementBC(
    name='BC-Symmetry-YZ',
    createStepName='Initial',
    region=region,
    u1=0.0,          # X方向固定
    u2=UNSET,
    u3=UNSET,
    ur1=UNSET,
    ur2=0.0,         # 绕Y轴转动固定
    ur3=0.0          # 绕Z轴转动固定
)
```

### 模板 3：指定位移

```python
# ========== 施加强制位移 ==========
# 在特定分析步施加强制位移
loaded_faces = instance.faces.findAt(((100.0, 25.0, 10.0),))
region = assembly.Set(name='Loaded-End', faces=loaded_faces)

model.DisplacementBC(
    name='BC-Displacement',
    createStepName='Step-1',     # 在分析步1施加
    region=region,
    u1=0.0,
    u2=10.0,                     # Y方向位移 10mm
    u3=0.0,
    ur1=UNSET,
    ur2=UNSET,
    ur3=UNSET,
    amplitude=UNSET,
    fixed=OFF,
    distributionType=UNIFORM
)
```

### 模板 4：集中力

```python
# ========== 集中力载荷 ==========
# 在节点上施加集中力
load_node = instance.nodes[10]  # 通过索引选择节点
region = assembly.Set(name='Load-Node', nodes=(load_node,))

model.ConcentratedForce(
    name='Load-Force',
    createStepName='Step-1',
    region=region,
    cf1=0.0,           # X方向力
    cf2=-1000.0,       # Y方向力 (负值为向下)
    cf3=0.0,           # Z方向力
    amplitude=UNSET,
    follower=OFF,
    distributionType=UNIFORM,
    localCsys=None
)

# 多个节点的集中力
load_nodes = (instance.nodes[10], instance.nodes[11], instance.nodes[12])
region = assembly.Set(name='Load-Nodes', nodes=load_nodes)
model.ConcentratedForce(
    name='Load-Forces',
    createStepName='Step-1',
    region=region,
    cf2=-500.0
)
```

### 模板 5：压力载荷

```python
# ========== 均布压力 ==========
pressure_faces = instance.faces.findAt(((50.0, 50.0, 10.0),))
region = assembly.Surface(name='Pressure-Surf', side1Faces=pressure_faces)

model.Pressure(
    name='Load-Pressure',
    createStepName='Step-1',
    region=region,
    distributionType=UNIFORM,
    field='',
    magnitude=10.0,          # 压力值 (MPa = N/mm²)
    amplitude=UNSET
)

# ========== 随位置变化的压力 ==========
# 使用解析场定义分布压力
model.AnalyticalField(
    name='Varying-Pressure',
    description='Linearly varying pressure',
    expression='10.0 + 0.1 * X'    # 随X坐标线性变化
)

model.Pressure(
    name='Load-Varying-Pressure',
    createStepName='Step-1',
    region=region,
    distributionType=FIELD,
    field='Varying-Pressure',
    magnitude=1.0,
    amplitude=UNSET
)
```

### 模板 6：重力/加速度

```python
# ========== 重力载荷 ==========
# 在整个模型上施加重力
all_cells = instance.cells
region = assembly.Set(name='Whole-Body', cells=all_cells)

# 方法1：使用体力
gravity = 9800.0  # mm/s² (注意单位：9.8 m/s² = 9800 mm/s²)
model.BodyForce(
    name='Load-Gravity',
    createStepName='Step-1',
    region=region,
    comp1=0.0,           # X方向
    comp2=-gravity,      # Y方向 (负Y为重力方向)
    comp3=0.0,           # Z方向
    distributionType=UNIFORM
)

# 方法2：使用重力载荷（更常用）
model.Gravity(
    name='Load-Gravity',
    createStepName='Step-1',
    comp1=0.0,
    comp2=-1.0,          # 方向向量 (Y方向)
    comp3=0.0,
    amplitude=UNSET,
    distributionType=UNIFORM,
    field=''
)
```

### 模板 7：离心力

```python
# ========== 旋转离心力 ==========
# 定义旋转轴和转速
# 绕Z轴旋转，转速 1000 RPM
omega = 1000.0 * 2.0 * 3.14159 / 60.0  # 转换为 rad/s

model.RotationalBodyForce(
    name='Load-Centrifugal',
    createStepName='Step-1',
    region=region,
    magnitude=omega**2,    # 角速度平方
    centrifugal=ON,
    rotaryAcceleration=OFF,
    point1=(0.0, 0.0, 0.0),    # 旋转轴起点
    point2=(0.0, 0.0, 100.0),  # 旋转轴终点 (Z轴)
    amplitude=UNSET
)
```

### 模板 8：温度载荷

```python
# ========== 预定义温度场 ==========
# 创建温度场
model.Temperature(
    name='Predefined-Field',
    createStepName='Initial',
    region=region,
    distributionType=UNIFORM,
    crossSectionDistribution=CONSTANT_THROUGH_THICKNESS,
    magnitudes=(20.0,)     # 初始温度 20°C
)

# ========== 温度变化 ==========
# 在分析步中改变温度
model.Temperature(
    name='Temp-Change',
    createStepName='Step-1',
    region=region,
    distributionType=UNIFORM,
    magnitudes=(100.0,),    # 升高到 100°C
    amplitude=UNSET
)

# ========== 从结果文件导入温度场 ==========
# 使用已完成的传热分析结果
model.Temperature(
    name='Temp-From-ODB',
    createStepName='Step-1',
    region=region,
    distributionType=FROM_FILE,
    fileName='thermal_results.odb',
    beginStep=0,
    beginIncrement=0,
    endStep=LAST_STEP,
    endIncrement=LAST_INCREMENT,
    interpolate=ON
)
```

### 模板 9：螺栓预紧力

```python
# ========== 螺栓预紧力 ==========
# 1. 创建螺栓加载面（通常在螺栓杆中间）
bolt_faces = instance.faces.findAt(((50.0, 0.0, 10.0),))
region = assembly.Surface(name='Bolt-Surf', side1Faces=bolt_faces)

# 2. 创建预紧力载荷（第一步）
model.BoltLoad(
    name='Bolt-Pretension',
    createStepName='Step-1',
    region=region,
    magnitude=10000.0,       # 预紧力大小 (N)
    boltMethod=APPLY_FORCE,
    amplitude=UNSET,
    preloadType=DEPENDENT
)

# 3. 在后续分析步中固定螺栓长度
model.BoltLoad(
    name='Bolt-Fix',
    createStepName='Step-2',    # 后续分析步
    region=region,
    boltMethod=FIX_LENGTH
)
```

### 模板 10：随时间变化的载荷

```python
# ========== 使用幅值曲线 ==========
# 1. 定义幅值曲线
model.TabularAmplitude(
    name='Ramp-Amplitude',
    timeSpan=STEP,
    smooth=SOLVER_DEFAULT,
    data=((0.0, 0.0),      # 时间点, 幅值
          (0.5, 0.5),
          (1.0, 1.0))
)

# 2. 使用幅值曲线施加载荷
model.Pressure(
    name='Load-With-Amplitude',
    createStepName='Step-1',
    region=region,
    magnitude=10.0,
    amplitude='Ramp-Amplitude'    # 应用幅值曲线
)

# ========== 其他幅值类型 ==========
# 周期幅值
model.PeriodicAmplitude(
    name='Periodic-Amp',
    timeSpan=STEP,
    frequency=10.0,           # 频率 (Hz)
    start=0.0,
    a_0=0.0,
    data=((1.0, 0.0),)        # 余弦系数, 正弦系数
)

# 平滑步幅值
model.SmoothStepAmplitude(
    name='Smooth-Amp',
    timeSpan=STEP,
    data=((0.0, 0.0),
          (1.0, 1.0))
)
```

## 🎯 边界条件管理

### 抑制/激活边界条件

```python
# 在特定分析步抑制边界条件
model.boundaryConditions['BC-Fixed'].deactivate('Step-2')

# 重新激活
model.boundaryConditions['BC-Fixed'].activate('Step-3')

# 修改边界条件
model.boundaryConditions['BC-Displacement'].setValuesInStep(
    stepName='Step-2',
    u2=20.0     # 在Step-2将位移改为20mm
)
```

### 边界条件传播

```python
# 复制边界条件到新分析步
model.boundaryConditions['BC-1'].resume()

# 删除边界条件
del model.boundaryConditions['BC-1']
```

## 💡 最佳实践

1. **约束检查**：
   - 确保约束足够，避免刚体位移
   - 使用对称约束简化模型
   - 检查约束是否合理（不过约束）

2. **载荷施加**：
   - 集中力尽量施放在节点上
   - 压力载荷检查方向（箭头指向面）
   - 大变形分析注意载荷跟随性（follower）

3. **单位一致性**：
   - 力：N
   - 压力：MPa (N/mm²)
   - 加速度：mm/s² (9800 mm/s² = 1g)

4. **增量控制**：
   - 突变载荷使用 STEP 幅值
   - 渐进载荷使用 RAMP 幅值

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 过约束 | 约束多于必要自由度 | 检查约束是否重复 |
| 欠约束 | 缺少必要约束 | 检查刚体位移模式 |
| 载荷方向错误 | 压力方向不对 | 检查面法向方向 |
| 单位错误 | 重力加速度单位错误 | 使用 9800 mm/s² |
| 奇异 | 约束冲突 | 检查相邻区域约束 |
