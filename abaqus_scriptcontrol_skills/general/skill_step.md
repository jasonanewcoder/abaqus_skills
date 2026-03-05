# 技能：分析步设置 (Step Configuration)

## 📖 功能描述

定义分析步类型、输出请求、求解器控制等。

## 🔧 API 参考

### 核心类和方法

```python
# 创建静力分析步
model.StaticStep(name='Step-1', previous='Initial', 
                 initialInc=0.1, maxInc=0.5, nlgeom=ON)

# 创建动态分析步
model.DynamicImplicitStep(name='Dynamic-Step', previous='Initial',
                          timePeriod=1.0, initialInc=0.01)

# 场输出请求
model.FieldOutputRequest(name='F-Output-1', createStepName='Step-1',
                         variables=('S', 'E', 'U', 'RF'))

# 历史输出请求
model.HistoryOutputRequest(name='H-Output-1', createStepName='Step-1',
                           variables=('RF1', 'U1'))
```

## 💻 代码模板

### 模板 1：通用静力分析步

```python
# ========== 分析步参数 ==========
step_name = 'Static-Step'
initial_inc = 0.1    # 初始增量
max_inc = 0.5        # 最大增量
min_inc = 1e-05      # 最小增量
max_num_inc = 100    # 最大增量步数
nlgeom = ON          # 几何非线性

# ========== 创建静力分析步 ==========
model = mdb.models['Model-1']

model.StaticStep(
    name=step_name,
    previous='Initial',
    description='Static analysis step',
    timePeriod=1.0,
    initialInc=initial_inc,
    minInc=min_inc,
    maxInc=max_inc,
    maxNumInc=max_num_inc,
    nlgeom=nlgeom,
    amplitude=RAMP
)
```

### 模板 2：线性静力分析步

```python
# ========== 线性静力分析步 ==========
# 线性分析：关闭几何非线性，使用直接求解器

model.StaticStep(
    name='Linear-Static',
    previous='Initial',
    description='Linear static analysis',
    timePeriod=1.0,
    initialInc=1.0,    # 线性分析可以一步完成
    minInc=1.0,
    maxInc=1.0,
    maxNumInc=1,
    nlgeom=OFF,        # 关闭几何非线性
    amplitude=RAMP
)

# 设置求解器为直接求解器（适合线性分析）
model.steps['Linear-Static'].setValues(
    solutionTechnique=FULL_NEWTON,
    matrixStorage=UNSYMMETRIC
)
```

### 模板 3：非线性静力分析步（接触）

```python
# ========== 非线性静力分析步（接触问题） ==========
# 接触问题需要更严格的收敛控制

model.StaticStep(
    name='Contact-Step',
    previous='Initial',
    description='Static analysis with contact',
    timePeriod=1.0,
    initialInc=0.01,   # 小初始增量
    minInc=1e-08,      # 很小的最小增量
    maxInc=0.1,        # 限制最大增量
    maxNumInc=10000,   # 允许更多增量步
    nlgeom=ON,
    amplitude=STEP     # 接触载荷使用阶跃加载
)

# 设置收敛控制
model.steps['Contact-Step'].setValues(
    solutionTechnique=FULL_NEWTON,
    convertSDI=CONVERT_SDI_OFF,
    matrixSolver=DIRECT,
    matrixStorage=UNSYMMETRIC
)
```

### 模板 4：屈曲分析步（特征值）

```python
# ========== 线性屈曲分析 ==========
# 需要先完成一个静力分析步

# 1. 预加载步
model.StaticStep(
    name='Preload',
    previous='Initial',
    nlgeom=OFF
)

# 2. 屈曲分析步
model.BuckleStep(
    name='Buckle-Step',
    previous='Preload',
    numEigen=10,           # 提取前10阶特征值
    vectors=16,            # 向量数
    maxIterations=50       # 最大迭代次数
)
```

### 模板 5：模态分析步

```python
# ========== 模态分析参数 ==========
num_modes = 10     # 提取模态数
min_frequency = 0.0   # 最小频率
max_frequency = 10000.0  # 最大频率 (Hz)

# ========== 创建模态分析步 ==========
model.FrequencyStep(
    name='Modal-Step',
    previous='Initial',
    description='Natural frequency extraction',
    eigenSolver=LANCZOS,    # 或 SUBSPACE
    numEigen=num_modes,
    minEigen=min_frequency,
    maxEigen=max_frequency,
    vectors=20,
    maxIterations=100
)
```

### 模板 6：瞬态动力学分析

```python
# ========== 瞬态动力学参数 ==========
time_period = 1.0     # 分析时长 (s)
initial_inc = 0.001   # 初始时间增量
min_inc = 1e-08       # 最小时间增量
max_inc = 0.01        # 最大时间增量

# ========== 创建瞬态分析步 ==========
model.DynamicImplicitStep(
    name='Transient-Step',
    previous='Initial',
    description='Transient dynamic analysis',
    timePeriod=time_period,
    initialInc=initial_inc,
    minInc=min_inc,
    maxInc=max_inc,
    maxNumInc=100000,
    nlgeom=ON,
    application=MODERATE_DISSIPATION,  # 或 TRANSIENT_FIDELITY
    amplitude=RAMP
)

# 设置时间积分参数
model.steps['Transient-Step'].setValues(
    alpha=DEFAULT,      # HHT 积分参数
    initialConditions=ON
)
```

### 模板 7：热传导分析步

```python
# ========== 稳态热传导 ==========
model.HeatTransferStep(
    name='Steady-Thermal',
    previous='Initial',
    description='Steady state heat transfer',
    response=STEADY_STATE,
    maxNumInc=1000,
    initialInc=1.0,
    minInc=1e-05,
    maxInc=1.0,
    deltmx=100.0        # 最大允许温度增量
)

# ========== 瞬态热传导 ==========
model.HeatTransferStep(
    name='Transient-Thermal',
    previous='Initial',
    description='Transient heat transfer',
    response=TRANSIENT,
    timePeriod=3600.0,   # 1小时
    maxNumInc=10000,
    initialInc=60.0,     # 1分钟
    minInc=0.01,
    maxInc=300.0,        # 5分钟
    deltmx=50.0          # 最大温度增量
)
```

### 模板 8：耦合热应力分析步

```python
# ========== 热-力耦合分析 ==========
model.CoupledTempDisplacementStep(
    name='Thermal-Stress',
    previous='Initial',
    description='Coupled thermal-stress analysis',
    timePeriod=1.0,
    maxNumInc=10000,
    initialInc=0.1,
    minInc=1e-08,
    maxInc=0.5,
    deltmx=10.0,         # 最大温度增量
    cetol=0.001,         # 温度-位移耦合容差
    nlgeom=ON
)
```

## 📊 场输出请求 (Field Output)

### 常用输出变量

```python
# 完整输出（大文件）
full_variables = ('S', 'E', 'PE', 'PEEQ', 'PEEQT',        # 应力应变
                  'LE', 'U', 'V', 'A',                    # 位移速度加速度
                  'RF', 'CF', 'P', 'CSTRESS', 'CDISP',    # 接触相关
                  'NT', 'TEMP', 'HFL',                    # 温度热流
                  'ENER', 'ELEN', 'EVOL', 'EMASS')        # 能量和体积

# 标准输出（推荐）
standard_variables = ('S', 'E', 'U', 'RF', 'PEEQ')

# 最小输出（小文件）
minimal_variables = ('S', 'U')
```

### 设置场输出

```python
# 创建场输出请求
model.FieldOutputRequest(
    name='Field-Output',
    createStepName='Step-1',
    variables=('S', 'E', 'U', 'RF', 'PEEQ'),
    frequency=LAST_INCREMENT,    # 输出频率
    region=MODEL,                # 或指定区域
    sectionPoints=DEFAULT,
    rebar=EXCLUDE
)

# 每N个增量输出一次
model.FieldOutputRequest(
    name='Field-Output-Freq',
    createStepName='Step-1',
    variables=('S', 'U'),
    frequency=10                 # 每10个增量输出
)

# 在指定时间输出
model.FieldOutputRequest(
    name='Field-Output-Time',
    createStepName='Step-1',
    variables=('S', 'U'),
    timeInterval=0.1             # 每0.1时间单位输出
)
```

## 📈 历史输出请求 (History Output)

```python
# 设置历史输出（特定节点/单元）

# 1. 创建集合（在部件或装配级别）
assembly = model.rootAssembly
region = assembly.Set(name='Monitor-Node', nodes=((instance.nodes[0],)))

# 2. 创建历史输出
model.HistoryOutputRequest(
    name='History-Output',
    createStepName='Step-1',
    variables=('U1', 'U2', 'U3', 'RF1', 'RF2', 'RF3'),
    region=region,
    frequency=1                   # 每个增量都输出
)

# 输出特定单元的应力
region = assembly.Set(name='Monitor-Element', elements=((instance.elements[0],)))
model.HistoryOutputRequest(
    name='History-Stress',
    createStepName='Step-1',
    variables=('S11', 'S22', 'S33', 'MISES'),
    region=region,
    sectionPoints=DEFAULT,
    frequency=1
)

# 接触输出
region = assembly.Surface(name='Contact-Surf', side1Faces=instance.faces[0:1])
model.HistoryOutputRequest(
    name='Contact-Output',
    createStepName='Step-1',
    variables=('CFN', 'CFS', 'CAREA', 'CMN'),
    region=region,
    frequency=1
)
```

## 🎛️ 求解器控制

### 静力分析求解器设置

```python
# 设置求解器控制
import step

# 获取分析步
step_obj = model.steps['Step-1']

# 设置求解技术
step_obj.setValues(
    solutionTechnique=FULL_NEWTON,      # 或 QUASI_NEWTON, SECANT
    convertSDI=CONVERT_SDI_OFF,
    matrixSolver=DIRECT,                # 或 ITERATIVE
    matrixStorage=SYMMETRIC,            # 或 UNSYMMETRIC
    matrixStorageFreq=1
)

# 设置收敛控制
step_obj.setValues(
    initialInc=0.1,
    minInc=1e-08,
    maxInc=0.5,
    maxNumInc=1000,
    maxLineSearchIterations=20,
    extrapolation=LINEAR                # 或 PARABOLIC, NONE
)
```

### 自动稳定化

```python
# 对于高度非线性问题，启用自动稳定化
model.StaticStep(
    name='Stabilized-Step',
    previous='Initial',
    stabilizationMagnitude=0.0002,       # 阻尼系数
    stabilizationMethod=DAMPING_FACTOR,
    continueDampingFactors=False,
    adaptiveDampingRatio=None
)
```

## ⚙️ 分析步间传递

```python
# 多步分析，从上一分析步继承状态

# 第一步
model.StaticStep(name='Step-1', previous='Initial')

# 第二步（继承第一步结果）
model.StaticStep(name='Step-2', previous='Step-1')

# 第三步（移除载荷）
model.StaticStep(name='Step-3', previous='Step-2')
```

## 💡 最佳实践

1. **初始增量选择**：
   - 线性分析：initialInc = 1.0
   - 简单非线性：initialInc = 0.1
   - 复杂接触：initialInc = 0.01

2. **非线性诊断**：
   - 收敛困难时减小 initialInc
   - 使用自动稳定化（stabilization）
   - 考虑分步加载

3. **输出控制**：
   - 大模型：减少输出变量，增加输出间隔
   - 调试阶段：增加输出频率
   - 最终运行：优化输出以减小文件大小

4. **单位检查**：
   - timePeriod 和增量步的单位与时间相关载荷一致

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 收敛失败 | 增量太大或载荷过大 | 减小 initialInc，启用稳定化 |
| 奇异矩阵 | 约束不足 | 检查边界条件 |
| 结果不保存 | 未设置输出请求 | 创建 FieldOutputRequest |
| 时间步太小 | minInc 设置太小 | 调整 minInc 或使用自动时间步 |
