# Job Submission Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus job submission.

## Core API

```python
# Create job
job = mdb.Job(name='Job-1', model='Model-1')

# Submit job
job.submit()

# Wait for completion
job.waitForCompletion()

# Write input file
mdb.jobs['Job-1'].writeInput(consistencyChecking=OFF)
```

## Code Templates

### Template 1: Basic Job Submission

```python
job_name = 'Static-Analysis'
model_name = 'Model-1'
num_cpus = 4

# Create job
job = mdb.Job(
    name=job_name,
    model=model_name,
    description='Static analysis job',
    type=ANALYSIS,
    memory=90,
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
    numDomains=num_cpus,
    numGpus=0
)

# Submit job
job.submit(consistencyChecking=OFF)

# Wait for completion
job.waitForCompletion()

print(f"Job {job_name} completed!")
```

### Template 2: Parallel Computing Setup

```python
num_cpus = 8
num_gpus = 0

job = mdb.Job(
    name='Parallel-Job',
    model='Model-1',
    description='Parallel analysis',
    numCpus=num_cpus,
    numDomains=num_cpus,
    multiprocessingMode=DOMAIN,
    numGpus=num_gpus
)

job.submit()
job.waitForCompletion()
```

### Template 3: Memory Optimization

```python
job = mdb.Job(
    name='Large-Model-Job',
    model='Model-1',
    description='Large model analysis',
    memory=90,
    memoryUnits=PERCENTAGE,
    getMemoryFromAnalysis=True,
    # Or specify fixed memory
    # memory=32000,
    # memoryUnits=MEGA_BYTES,
    explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE
)

job.submit()
```

### Template 4: Restart Analysis

```python
# 1. Enable restart
model.steps['Step-1'].Restart(
    frequency=10,
    numberIntervals=0,
    overlay=OFF,
    timeMarks=OFF
)

# 2. Create initial job and run
job = mdb.Job(name='Job-Initial', model='Model-1')
job.submit()
job.waitForCompletion()

# 3. Restart from specific increment
restart_job = mdb.Job(
    name='Job-Restart',
    model='Model-1',
    description='Restart analysis',
    restartJob='Job-Initial',
    restartStep='Step-1',
    restartIncrement=50
)

restart_job.submit()
```

### Template 5: Submodel Analysis

```python
# Global model job
global_job = mdb.Job(name='Global-Job', model='Global-Model')
global_job.submit()
global_job.waitForCompletion()

# Submodel job
submodel_job = mdb.Job(
    name='Submodel-Job',
    model='Submodel-Model',
    description='Submodel analysis',
    submodel=True,
    submodelJob='Global-Job'
)

submodel_job.submit()
```

### Template 6: Generate Input File Only

```python
job = mdb.Job(name='Input-Only', model='Model-1')

# Write input file only, don't submit for calculation
job.writeInput(consistencyChecking=OFF)

print("Input file generated: Input-Only.inp")
```

### Template 7: Batch Submit Multiple Jobs

```python
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

# Submit sequentially
for job in jobs:
    job.submit()
    job.waitForCompletion()
    print(f"Job {job.name} completed")
```

## Job Monitoring and Diagnostics

### Monitoring Job Status

```python
job = mdb.jobs['Job-1']
status = job.status

# Status values: NONE, SUBMITTED, RUNNING, ABORTED, TERMINATED, COMPLETED

print(f"Job status: {status}")

# Wait for completion and check results
job.waitForCompletion()

if job.status == COMPLETED:
    print("Analysis completed successfully!")
else:
    print(f"Analysis not completed, status: {job.status}")
```

### Viewing Message File

```python
import os

msg_file = f'{job_name}.msg'

if os.path.exists(msg_file):
    with open(msg_file, 'r') as f:
        content = f.read()
        if 'ERROR' in content:
            print("Errors found!")
        if 'WARNING' in content:
            print("Warnings found!")
```

### Job Callbacks

```python
import time

def on_job_complete(job_name):
    print(f"Job {job_name} completed!")
    # Auto post-processing

job.submit()
while job.status == SUBMITTED or job.status == RUNNING:
    time.sleep(5)
    
if job.status == COMPLETED:
    on_job_complete(job.name)
```

## Advanced Settings

### User Subroutines

```python
job = mdb.Job(
    name='User-Subroutine-Job',
    model='Model-1',
    userSubroutine='my_umat.for',
    numCpus=4
)

job.submit()
```

### Environment Variable Settings

```python
import os

# Set Abaqus environment variables
os.environ['ABAQUS_NO_PARALLEL'] = '1'
os.environ['ABA_BATCH_OVERRIDE'] = '1'

job = mdb.Job(name='Env-Job', model='Model-1')
job.submit()
```

### Temporary Directory Settings

```python
job = mdb.Job(
    name='Scratch-Job',
    model='Model-1',
    scratch='D:/Temp/Abaqus'
)

job.submit()
```

## Best Practices

1. **Naming Conventions**:
   - Use concise and clear job names
   - Avoid special characters and spaces

2. **Parallel Computing**:
   - Large models: numCpus = 4-16
   - Small models: numCpus = 1-2

3. **Memory Management**:
   - Use getMemoryFromAnalysis=True
   - Set memory=90 for large models

4. **Error Handling**:
   - Check .msg and .dat files
   - Review .sta file for increment history
