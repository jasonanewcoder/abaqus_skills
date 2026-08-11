# ODB Post-Processing — Detailed Reference

## Overview

Reads results from the Abaqus output database (`.odb`) using the Python `odbAccess` module.
This is the **verification loop of agent-driven analysis**: extract stress/displacement/
reaction results, check convergence diagnostics (energy, status), and produce a report —
without opening CAE.

> 中文提示：后处理是 agent 闭环的关键——跑完 job 后必须读取 ODB 验证结果，
> 而不是让用户自己打开 CAE 看。以下模板可直接在 `abaqus python script.py` 中运行
> （脚本运行在 Abaqus 的 Python 环境里，`odbAccess` 已内置）。

## Two Ways to Run

```bash
# 1. Full CAE environment (mdb available, GUI disabled)
abaqus cae noGUI=post.py

# 2. Lightweight kernel-only (only odbAccess + abaqus modules, faster startup)
abaqus python post.py
```

For pure ODB work use **`abaqus python`** — it starts faster and does not need CAE.

## Core API

```python
from odbAccess import openOdb
import numpy as np  # available in Abaqus Python 3.x (2023+)

odb = openOdb(path='Job-1.odb', readOnly=True)   # readOnly: never modify results
# ... work ...
odb.close()
```

### Navigate the ODB Structure

```python
odb = openOdb(path='Job-1.odb', readOnly=True)

# Model tree
print(odb.rootAssembly.instances.keys())          # instance names
print(odb.parts.keys())                           # part names

# Steps and frames
for step_name, step in odb.steps.items():
    print(step_name, 'frames:', len(step.frames))
    for i, frame in enumerate(step.frames):
        print('  frame', i, 'time', frame.frameValue,
              'inc', frame.incrementNumber,
              'desc', frame.description)

# Field outputs available in the last frame
last_frame = odb.steps['Static-Step'].frames[-1]
print(last_frame.fieldOutputs.keys())             # 'S', 'E', 'U', 'RF', 'PEEQ'...
```

### Common Field Outputs

| Key | Meaning | Data type |
|-----|---------|-----------|
| `U` | Displacement | VECTOR (nodal) |
| `RF` | Reaction force | VECTOR (nodal) |
| `S` | Stress tensor | TENSOR_3D_FULL (integration points) |
| `E` | Total strain | TENSOR_3D_FULL |
| `PE`, `PEEQ` | Plastic strain, equivalent plastic strain | TENSOR / SCALAR |
| `NT`, `TEMP` | Temperature | SCALAR |
| `HFL` | Heat flux | VECTOR |
| `CSTRESS`, `CDISP` | Contact stress / displacement | TENSOR / VECTOR |
| `STATUS` | Element status (0=dead/removed, 1=active) | SCALAR |
| `PHILSM`, `STATUSXFEM` | XFEM level set / crack status | SCALAR |
| `SDV` | Solution-dependent state variables | SCALAR (per SDV index) |

> `MISES` is NOT stored in the ODB — the viewer computes it from `S`.
> In post-processing you compute it yourself (see below).

## Template 1: Extract Nodal Quantities (Displacement, Reaction Force)

```python
from odbAccess import openOdb

odb = openOdb(path='Job-1.odb', readOnly=True)
frame = odb.steps['Static-Step'].frames[-1]

# Nodal displacement — loop over all nodes
u_field = frame.fieldOutputs['U']
max_u = 0.0
for value in u_field.values:
    mag = (value.data[0]**2 + value.data[1]**2 + value.data[2]**2) ** 0.5
    max_u = max(max_u, mag)
print(f'Max displacement magnitude: {max_u:.6f} mm')

# Reaction force on a set
set_name = 'Fixed-End'
try:
    region = odb.rootAssembly.instances['Beam-1'].nodeSets[set_name]
    rf_field = frame.fieldOutputs['RF'].getSubset(region=region)
    rf_tot = [0.0, 0.0, 0.0]
    for value in rf_field.values:
        for i in range(3):
            rf_tot[i] += value.data[i]
    print(f'Total reaction force: {rf_tot} N')
except KeyError:
    print(f'Set {set_name} not found')
```

> **Important**: `getSubset(region=...)` for node sets — for a set created in the
> assembly, reference it via `rootAssembly.instances[name].nodeSets[name]` (instance-level)
> or `rootAssembly.nodeSets[name]` (assembly-level). Try both if the first fails.

## Template 2: Compute Mises Stress from the S Tensor

```python
from odbAccess import openOdb

odb = openOdb(path='Job-1.odb', readOnly=True)
frame = odb.steps['Static-Step'].frames[-1]
s_field = frame.fieldOutputs['S']

# S stored as (S11, S22, S33, S12, S13, S23) — Abaqus order
max_mises = 0.0
max_elem = None
for value in s_field.values:
    s11, s22, s33 = value.data[0], value.data[1], value.data[2]
    s12, s13, s23 = value.data[3], value.data[4], value.data[5]
    mises = ((s11 - s22)**2 + (s22 - s33)**2 + (s33 - s11)**2
             + 6.0 * (s12**2 + s13**2 + s23**2)) ** 0.5 / 2.0 ** 0.5
    if mises > max_mises:
        max_mises = mises
        max_elem = (value.elementLabel, value.integrationPoint)
print(f'Max Mises stress: {max_mises:.3f} MPa at {max_elem}')

# Get results at the MAXIMUM PRINCIPAL component too:
max_principal_field = s_field.getScalarField(componentLabel='Max. Principal')
```

## Template 3: Element Stress on a Specific Set (e.g. hot spot)

```python
region = odb.rootAssembly.instances['Plate-1'].elementSets['Hot-Spot']
s_field = frame.fieldOutputs['S'].getSubset(region=region)

# Average over integration points per element (element average)
from collections import defaultdict
elem_sum = defaultdict(lambda: [0.0]*6)
elem_count = defaultdict(int)
for value in s_field.values:
    elem_sum[value.elementLabel] = [a + b for a, b in
                                    zip(elem_sum[value.elementLabel], value.data)]
    elem_count[value.elementLabel] += 1
for label in elem_sum:
    avg = [v / elem_count[label] for v in elem_sum[label]]
    print(f'Element {label}: S = {avg}')
```

## Template 4: History Output — Load–Displacement Curve

```python
# History output is per history region (node / element / section point)
step = odb.steps['Static-Load']
for region_key, region in step.historyRegions.items():
    print(region_key)                    # e.g. 'Node BEAM-1.5'
    print(region.historyOutputs.keys())  # e.g. 'U2', 'RF2', 'SMISES'

# Extract a curve for XY plotting
region = step.historyRegions['Node BEAM-1.5']
u2 = region.historyOutputs['U2']
times = [d.frameValue for d in u2.data]
values = [d.value for d in u2.data]

# Write to CSV for reporting
with open('load_deflection.csv', 'w') as f:
    f.write('time,u2\n')
    for t, v in zip(times, values):
        f.write(f'{t},{v}\n')
```

## Template 5: Energy Diagnostics (Convergence & Stability)

```python
# Global history outputs: ALLKE, ALLIE, ALLVD, ALLAE, ALLWK, ETOTAL
region = odb.steps['Nonlinear-Step'].historyRegions['Assembly ASSEMBLY']
keys = region.historyOutputs.keys()

if 'ALLIE' in keys and 'ALLKE' in keys:
    last = lambda k: region.historyOutputs[k].data[-1].value
    print(f'Internal energy ALLIE: {last("ALLIE"):.6e}')
    print(f'Kinetic energy ALLKE:  {last("ALLKE"):.6e}')
    # Quasi-static check: ALLKE should be << ALLIE (<5% typically)

if 'ETOTAL' in keys:
    print(f'Total energy ETOTAL:   {last("ETOTAL"):.6e}')

if 'ALLAE' in keys:
    # Artificial (hourglass) energy — should be <5% of ALLIE
    ratio = last('ALLAE') / max(last('ALLIE'), 1e-30)
    print(f'Hourglass ratio ALLAE/ALLIE: {ratio:.2%}')
    if ratio > 0.05:
        print('WARNING: hourglass energy too high — refine mesh or change element type')

if 'ALLVD' in keys and 'ALLIE' in keys:
    # Viscous dissipation from stabilization
    ratio_vd = last('ALLVD') / max(last('ALLIE'), 1e-30)
    print(f'Stabilization ratio ALLVD/ALLIE: {ratio_vd:.2%}')
    if ratio_vd > 0.05:
        print('WARNING: stabilization energy too high — reduce stabilization magnitude')
```

## Template 6: Automated Verification Report

```python
def report_job(path='Job-1.odb'):
    """Minimal machine-readable verification summary (agent-friendly)."""
    from odbAccess import openOdb
    odb = openOdb(path=path, readOnly=True)
    lines = []
    for sname, step in odb.steps.items():
        frame = step.frames[-1]
        line = f'step={sname} nframes={len(step.frames)} '
        if 'U' in frame.fieldOutputs:
            u = frame.fieldOutputs['U']
            maxu = max((v.data[0]**2 + v.data[1]**2 + v.data[2]**2)**0.5
                       for v in u.values)
            line += f'max_U={maxu:.6g} '
        if 'S' in frame.fieldOutputs:
            s = frame.fieldOutputs['S']
            maxs = max(max(v.data) for v in s.values)
            line += f'max_S_component={maxs:.6g}'
        lines.append(line)
    odb.close()
    return '\n'.join(lines)

if __name__ == '__main__':
    print(report_job())
```

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `KeyError` on `fieldOutputs['S']` | Output not requested in step | Add `variables=('S', ...)` to FieldOutputRequest |
| Empty `values` | Region subset mismatch | Check set exists at instance vs assembly level |
| Wrong stress ordering | 3D vs plane-stress `data` length | 2D has 3 components (`S11,S22,S12`); always check `value.data` length |
| `frameValue` vs real time | Frame holds step-local time | Use `step.timePeriod` for total time |
| Job still running | `.lck` file present | Wait for `job.waitForCompletion()` or poll `.lck` |
| Opening ODB while job writes | Read conflict | Open `readOnly=True` and retry |

## Best Practices

1. **Always open `readOnly=True`** when only reading — safe with running jobs
2. Check `step.totalTime` and `frame.frameValue` before comparing increments
3. Verify element set names — CAE lowercases/trims names in ODB
4. For large ODBs, use `getSubset` to limit reads; avoid looping all values if possible
5. Write results to CSV/JSON so the agent can compare with analytical values
6. When the job aborted, the ODB may contain partial results — check the last frame's
   `incrementNumber` against the `.sta` file

## Related

- `headless_execution.md` — submit + monitor + capture `.sta/.msg/.dat`
- `verification.md` — analytical benchmarks to compare against
- `scripts/odb_extract.py` — ready-made CLI for common extractions
