# Headless Execution — Detailed Reference

## Overview

Runs Abaqus without the GUI, submit jobs from the command line, and monitor progress by
parsing log files. This is how an **agent executes simulations end-to-end**:
`model script → noGUI run → job submit → monitor → parse logs → iterate`.

> 中文提示：agent 执行仿真的核心命令是 `abaqus cae noGUI=script.py`（建模）和
> `abaqus job=Job-1`（求解）。本文件给出完整命令、日志解读与退出码判断。

## Command Reference

### 1. Build the Model Headlessly (CAE kernel, no GUI)

```bash
# Run a CAE scripting file (builds model + submits job if the script does it)
abaqus cae noGUI=model_setup.py

# With a startup directory / environment overrides
abaqus cae noGUI=model_setup.py -script arg1 arg2     # pass args to the script (sys.argv)
```

Requirements inside `model_setup.py`:
- `from abaqus import *`, `from abaqusConstants import *`, `from caeModules import *`
- The script runs to completion; `mdb` is populated; if the script submits a job and
  calls `waitForCompletion()`, the run blocks until the solver finishes.

### 2. Submit a Solver Job (existing .inp or model)

```bash
# Submit from .inp directly (no CAE needed)
abaqus job=Job-1 interactive          # foreground: stream output to console
abaqus job=Job-1 background           # background: write to Job-1.log/.com, detach

# Common flags
abaqus job=Job-1 user=my_sub.f cpus=4 int      # with user subroutine, 4 cpus
abaqus job=Job-1 cpus=8 domain=8 standard_parallel=all
abaqus job=Job-1 double=both                   # double precision
abaqus job=Job-1 scratch=/tmp/abaqus           # scratch dir
abaqus job=Job-1 memory=90 memoryUnits=percent # memory limit
abaqus job=Job-1 restart, ...                  # see job.md restart template
```

> On macOS/Linux the environment is usually activated via `source /path/to/abaqusvars.sh`
> (Windows: `abaqusvars.bat`). The `abaqus` launcher must be on `PATH`.

### 3. Run Kernel Scripts Without CAE (post-processing etc.)

```bash
abaqus python post.py                 # odbAccess-only scripts (fast startup)
abaqus python -c "print('hello')"     # inline
abaqus viewer noGUI=render.py         # viewport/report generation without GUI
```

## Files Produced by a Job (the agent's ground truth)

| File | Content | Agent use |
|------|---------|-----------|
| `Job-1.sta` | Increment summary: time, increment size, iterations, cutbacks, warnings | Convergence status per increment; "***WARNING: THE PLASTICITY..." lines |
| `Job-1.msg` | Solver details: iteration residuals, contact, diagnostics | Convergence diagnostics, error causes |
| `Job-1.dat` | Input echo + `*PRINT` outputs + errors | Verify model was as intended; some errors only appear here |
| `Job-1.log` | Solver start/stop log | Job lifecycle (started/finished/aborted) |
| `Job-1.com` | The exact command line used | Reproducibility |
| `Job-1.lck` | Lock file — **exists while the job runs** | Poll: job still running |
| `Job-1.odb` | Results database | Post-processing |
| `Job-1.inp` | Input deck (written by `writeInput`) | Static checks with `scripts/inp_checker.py` |
| `Job-1.res/.stt` | Restart files | Restart analysis |

## Reading `.sta` — The Quick Convergence Summary

```
         STEP  INC ATT ITRS TOT TIME  STEP TIME  INC TIME  CUT    MONITOR RATIO   #FIX  #FL  #A  #IW  #IC  #LW  #LC  #PW  #PC
             1    1   1    1   1.000     1.000     1.000    0   -1.000E+00  0.000    0    0   0    0    0    0    0    0    0
```

Key columns:
- **ITRS**: iterations in this increment. 1–3 = healthy; 4–8 = acceptable; repeated >16
  or `CUT` > 0 → convergence trouble
- **CUT**: number of cutbacks in this increment. Repeated cutbacks → reduce `initialInc`
- **MONITOR RATIO**: normalized residual — should trend below 1.0

Script to parse quickly:

```bash
grep -E "^( *STEP|[0-9]+ +[0-9]+)" Job-1.sta | tail -20
```

## Reading `.msg` — Diagnostics

```bash
# Errors and warnings
grep -iE "error|warning" Job-1.msg | sort -u | head -30

# Negative eigenvalues (instability / snap-through)
grep -c "negative eigenvalue" Job-1.msg

# Non-convergence
grep -iE "did not converge|too many attempts|convergence problem" Job-1.msg
```

Typical solver abort messages and where to find the fix:
- `TOO MANY ATTEMPTS MADE FOR THIS INCREMENT` → `error_diagnosis.md` — increment control
- `ZERO PIVOT` / `NUMERICAL SINGULARITY` → check boundary conditions/constraints
- `NEGATIVE EIGENVALUE` → buckling/instability; check for rigid-body modes
- `ELEMENT DISTORTED EXCESSIVELY` → mesh/geometry issue

## Exit Status Determination (agent decision table)

| Signal | Meaning | Next action |
|--------|---------|-------------|
| `Job-1.lck` disappears AND `Job-1.log` shows `THE ANALYSIS HAS COMPLETED SUCCESSFULLY` | Success | Proceed to post-processing |
| `.sta` last line is a step/analysis summary with no error | Success (verify `.msg` warnings) | Proceed |
| `abaqus job=...` command exits non-zero | Failure before/during solve | Check `.log`, `.dat`, `.msg` |
| `Error: The executable "standard.exe" aborted with system error code` | Solver crash | Check `.msg` tail, disk space, memory |
| `***ERROR: TOO MANY INCREMENTS` in `.dat` | Increment limit | Increase `maxNumInc` or fix convergence |
| Lock file remains long after expected end | Hung job | Inspect `.msg`; kill via `abaqus terminate job=Job-1` |

## Monitoring Loop (bash)

```bash
#!/usr/bin/env bash
# scripts/job_monitor.sh — submit + monitor + capture logs
set -u
JOB="${1:-Job-1}"
abaqus job="$JOB" background
while [ -f "$JOB.lck" ]; do
  sleep 30
  echo "[$(date +%H:%M:%S)] still running — last sta line:"
  tail -1 "$JOB.sta" 2>/dev/null || echo "(no .sta yet)"
done
echo "=== Job finished ==="
tail -5 "$JOB.log"
grep -iE "^error" "$JOB.dat" | head -5
```

## Agent Execution Recipe (headless)

```bash
# 1. Generate the model (writes model + optionally .inp)
abaqus cae noGUI=model_setup.py

# 2. Optionally write the input deck for inspection
#    (in model_setup.py: mdb.jobs['Job-1'].writeInput(consistencyChecking=OFF))

# 3. Submit solver
abaqus job=Job-1 cpus=4 background

# 4. Poll until done (lock file gone) — parse .sta/.msg/.dat on the way

# 5. Extract results
abaqus python scripts/odb_extract.py Job-1.odb --field U --max
```

## Environment Variables & Config

```bash
export ABAQUS_SCRATCH=/fast/scratch        # scratch dir
export ABAQUS_BAT_OVERRIDE=1               # allow batch override
export ABAQUS_IMAGES=off                   # no image output
export ABQ_MPI_PRELOAD=0                   # MPI workarounds on some clusters
```

The site configuration lives in `site/abaqus_v6.env` inside the Abaqus installation
(`pre_memory`, `pre_standard`, `mp_mode`, `default_cores`...).

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `abaqus: command not found` | Environment not sourced | `source /.../abaqusvars.sh` |
| `noGUI` script crashes silently | Python exception in script | Wrap in `try/except` + `print`; run `abaqus cae noGUI=... -verbose` |
| Job "runs forever" | Lock file not released on crash | `abaqus terminate job=Job-1`; delete stale `.lck` |
| Results missing `S` | Field output not requested | Check FieldOutputRequest in model script |
| `.inp` differs from intention | CAE writes what it wants | Inspect `.inp` echo in `.dat`, or `writeInput` and diff |
| Background job dies at shell exit | `background` uses shell job control | Use `nohup abaqus job=... ` or screen/tmux |

## Related

- `postprocess_odb.md` — read results once the job completes
- `error_diagnosis.md` — symptom → fix decision tables
- `job.md` — mdb.Job API (cpus, memory, restart, submodel)
- `scripts/job_monitor.sh` — ready-made monitoring wrapper
