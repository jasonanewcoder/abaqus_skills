# 技能：作业提交 (Job Submission)

## 📖 功能描述

创建分析作业、设置求解参数、提交计算、监控任务状态。

## 🔧 API 参考

### 核心类和方法

```python
# 创建作业
job = mdb.Job(name='Job-1', model='Model-1', description='Analysis job')

# 提交作业
job.submit()

# 等待完成
job.waitForCompletion()

# 写入输入文件
mdb.jobs['Job-1'].writeInput(consistencyChecking=OFF)
```

## 💻 代码模板

### 模板 1：基本作业提交

```python
# ========== 作业参数 ==========
job_name = 'Static-Analysis'
model_name = 'Model-1'
num_cpus = 4          # CPU核心数

# ========== 创建作业 ==========
# 创建作业
job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Static analysis job',
    type=ANALYSIS,
    atTime=None,
    waitMinutes=0,
    waitHours=0,
    queue=None,
    memory=90,                 # 内存百分比
    memoryUnits=PERCENTAGE,
    getMemoryFromAnalysis=True,
    explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE,
    echoPrint=OFF,
    modelPrint=OFF,
    contactPrint=OFF,
    historyPrint=OFF,
    userSubroutine='',
    scratch='',
    resultsFormat=ODB,
    multiprocessingMode=DEFAULT,
    numCpus=num_cpus,
    numDomains=num_cpus,       # 域数 = CPU数
    numGpus=0
)

# 写入输入文件（可选）
# job.writeInput(consistencyChecking=OFF)

# 提交作业
job.submit(consistencyChecking=OFF)

# 等待完成（可选）
job.waitForCompletion()

print(f"作业 {job_name} 完成!")
```

### 模板 2：并行计算设置

```python
# ========== 并行计算参数 ==========
num_cpus = 8          # 使用8核
num_gpus = 0          # GPU加速（如可用）

# ========== 创建并行作业 ==========
job = mdb.Job(
    name='Parallel-Job',
    model='Model-1',
    description='Parallel analysis',
    numCpus=num_cpus,
    numDomains=num_cpus,       # 域分解数
    multiprocessingMode=DOMAIN,  # 或 THREADS
    numGpus=num_gpus
)

# 提交
job.submit()
job.waitForCompletion()
```

### 模板 3：内存优化

```python
# ========== 大模型内存设置 ==========
job = mdb.Job(
    name='Large-Model-Job',
    model='Model-1',
    description='Large model analysis',
    memory=90,                 # 使用90%可用内存
    memoryUnits=PERCENTAGE,
    getMemoryFromAnalysis=True,  # 自动估计所需内存
    # 或指定固定内存
    # memory=32000,            # MB
    # memoryUnits=MEGA_BYTES,
    explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE
)

job.submit()
```

### 模板 4：增量输出控制

```python
# ========== 控制结果输出频率 ==========
job = mdb.Job(
    name='Controlled-Output',
    model='Model-1',
    description='Analysis with controlled output',
    resultsFormat=ODB,
    # 设置输出控制
    # 这些通常在模型级别设置，但可以在作业级别覆盖
)

# 设置增量输出（在模型中）
model.fieldOutputRequests['F-Output-1'].setValues(
    frequency=10              # 每10个增量输出一次
)

job.submit()
```

### 模板 5：重启动分析

```python
# ========== 设置重启动 ==========
# 1. 在模型中启用重启动
model.steps['Step-1'].Restart(
    frequency=10,             # 每10个增量写入重启动数据
    numberIntervals=0,
    overlay=OFF,
    timeMarks=OFF
)

# 2. 创建初始作业并运行
job = mdb.Job(name='Job-Initial', model='Model-1')
job.submit()
job.waitForCompletion()

# 3. 从特定增量重启动
# 创建重启动作业
restart_job = mdb.Job(
    name='Job-Restart',
    model='Model-1',
    description='Restart analysis',
    restartJob='Job-Initial',      # 原作业名
    restartStep='Step-1',          # 重启动的分析步
    restartIncrement=50            # 重启动的增量号
)

restart_job.submit()
```

### 模板 6：子模型分析

```python
# ========== 子模型分析 ==========
# 全局模型作业
global_job = mdb.Job(name='Global-Job', model='Global-Model')
global_job.submit()
global_job.waitForCompletion()

# 子模型作业
submodel_job = mdb.Job(
    name='Submodel-Job',
    model='Submodel-Model',
    description='Submodel analysis',
    submodel=True,
    submodelJob='Global-Job',      # 全局模型作业
    submodelJobDescription='Global model results'
)

submodel_job.submit()
```

### 模板 7：仅生成输入文件

```python
# ========== 仅写入INP文件 ==========
job = mdb.Job(name='Input-Only', model='Model-1')

# 仅写入输入文件，不提交计算
job.writeInput(consistencyChecking=OFF)

print("输入文件已生成: Input-Only.inp")

# 可以在命令行运行:
# abaqus job=Input-Only cpus=4
```

### 模板 8：批处理作业

```python
# ========== 批量提交多个作业 ==========
model_names = ['Model-1', 'Model-2', 'Model-3']
jobs = []

for i, model_name in enumerate(model_names):
    job_name = f'Job-{i+1}'
    job = mdb.Job(
        name=job_name,
        model=model_name,
        numCpus=4
    )
    jobs.append(job)

# 顺序提交
for job in jobs:
    job.submit()
    job.waitForCompletion()
    print(f"作业 {job.name} 完成")

# 或并行提交（需要足够许可证）
# for job in jobs:
#     job.submit()
# 
# for job in jobs:
#     job.waitForCompletion()
```

## 📊 作业监控和诊断

### 监控作业状态

```python
# 获取作业状态
job = mdb.jobs['Job-1']
status = job.status

# 状态值：
# NONE, SUBMITTED, RUNNING, ABORTED, TERMINATED, COMPLETED

print(f"作业状态: {status}")

# 等待完成并检查结果
job.waitForCompletion()

if job.status == COMPLETED:
    print("分析成功完成!")
else:
    print(f"分析未完成，状态: {job.status}")
```

### 查看消息文件

```python
import os

# 消息文件路径
msg_file = f'{job_name}.msg'

if os.path.exists(msg_file):
    with open(msg_file, 'r') as f:
        content = f.read()
        # 检查错误
        if 'ERROR' in content:
            print("发现错误!")
        # 检查警告
        if 'WARNING' in content:
            print("发现警告!")
```

### 作业回调（高级）

```python
# 定义回调函数
def on_job_complete(job_name):
    print(f"作业 {job_name} 完成!")
    # 自动进行后处理
    # openOdb(...)
    # ...

# 提交并设置回调（通过等待循环模拟）
job.submit()
while job.status == SUBMITTED or job.status == RUNNING:
    time.sleep(5)
    
if job.status == COMPLETED:
    on_job_complete(job.name)
```

## 🔧 高级设置

### 用户子程序

```python
# 使用用户子程序（UMAT, VUMAT, DLOAD等）
job = mdb.Job(
    name='User-Subroutine-Job',
    model='Model-1',
    userSubroutine='my_umat.for',    # Fortran源文件
    # 或编译后的文件
    # userSubroutine='my_umat.obj',
    numCpus=4
)

job.submit()
```

### 环境变量设置

```python
import os

# 设置Abaqus环境变量
os.environ['ABAQUS_NO_PARALLEL'] = '1'  # 禁用并行
os.environ['ABA_BATCH_OVERRIDE'] = '1'  # 批处理模式

# 创建和提交作业
job = mdb.Job(name='Env-Job', model='Model-1')
job.submit()
```

### 临时目录设置

```python
# 指定临时文件目录
job = mdb.Job(
    name='Scratch-Job',
    model='Model-1',
    scratch='D:/Temp/Abaqus'     # 临时文件目录
)

job.submit()
```

## 💡 最佳实践

1. **命名规范**：
   - 作业名称简洁明了
   - 避免特殊字符和空格
   - 使用有意义的命名如 `'Beam_Bending_Job'`

2. **并行计算**：
   - 根据模型大小选择CPU核心数
   - 大模型：numCpus = 4-16
   - 小模型：numCpus = 1-2（避免通信开销）

3. **内存管理**：
   - 使用 `getMemoryFromAnalysis=True`
   - 大模型设置 `memory=90, memoryUnits=PERCENTAGE`
   - 监控系统内存使用情况

4. **错误处理**：
   - 检查 `.msg` 和 `.dat` 文件
   - 查看 `.sta` 文件了解增量历史
   - 使用 `consistencyChecking=ON` 检查模型

5. **磁盘空间**：
   - 大模型确保足够的磁盘空间
   - 使用 `scratch` 指定大容量临时目录

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 许可证不足 | 并行数超过许可证限制 | 减少 numCpus |
| 内存不足 | 模型太大 | 增加内存设置，使用分域并行 |
| 输入错误 | 模型定义有误 | 检查 `.dat` 文件错误信息 |
| 收敛失败 | 非线性问题不收敛 | 调整增量步，启用稳定化 |
| 磁盘空间不足 | 临时文件太多 | 清理临时目录，增加磁盘空间 |
