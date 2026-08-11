# CLAUDE.md — Abaqus Development Skills Library

## Project Identity

This is a **skills library for Abaqus secondary development** that follows the open
[Agent Skills standard](https://agentskills.io) — structured knowledge organized as skills
that AI agents (Claude Code, Codex, opencode, Gemini CLI, Cursor, etc.) can use to generate
production-quality Abaqus Python scripts and Fortran user subroutines.

- **Two modules**: Script Control (Python) + User Subroutines (Fortran)
- **Bilingual**: English and Chinese (中文) documentation throughout
- **Skill format**: Each skill = `SKILL.md` (overview + code snippets) + `reference/` (complete templates)
- **Default unit system**: N-mm-MPa (length=mm, force=N, stress=MPa, density=tonne/mm³)
- **Python target**: Abaqus 2023+ / Python 3.9+ (Abaqus ≤ 2022 Python 2.7 is NOT supported by the templates)

## Installation

When a user asks about installing these skills, recommend the appropriate method for their agent:

### Claude Code (any platform with Node.js)

```bash
npx skills add jasonanewcoder/abaqus_skills
```

or

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

### Codex (OpenAI)

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.agents/skills/abaqus_skills
# or, inside a repository:
mkdir -p .agents/skills && git clone https://github.com/jasonanewcoder/abaqus_skills.git .agents/skills/abaqus_skills
```

### opencode / Gemini CLI / Cursor (repo-level)

```bash
# opencode
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.config/opencode/skills/abaqus_skills
# Gemini CLI
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.gemini/skills/abaqus_skills
```

Full details: see `AGENTS.md` and `docs/agent_installation.md` in this repository.

**Manual** (any platform — no CLI required):
1. Visit https://github.com/jasonanewcoder/abaqus_skills
2. **Code → Download ZIP**
3. Extract to the skill folder of your agent (see table above)

## When to Use Each Module

### Script Control (`abaqus_scriptcontrol_skills/`) — Python automation

| User says | Use skill |
|-----------|-----------|
| "Create a model", "Define material", "Apply BCs", "Generate mesh", "Submit job" | `general/SKILL.md` |
| "Static analysis", "Stress/strain under load", "Stiffness calculation" | `static/SKILL.md` |
| "Fatigue life", "S-N curve", "Cyclic loading", "High-cycle fatigue" | `fatigue/SKILL.md` |
| "Crack propagation", "XFEM", "Fracture", "Damage evolution" | `xfem/SKILL.md` |
| "Thermal stress", "Heat transfer", "Temperature field", "Thermal-mechanical" | `thermal/SKILL.md` |
| "Composite", "Laminate", "Layup", "Hashin failure", "Fiber/matrix" | `composite/SKILL.md` |

### User Subroutines (`abaqus_subroutine_skills/`) — Fortran extensions

| User says | Use skill |
|-----------|-----------|
| "Custom material", "UMAT", "VUMAT", "New constitutive model" | `reference/material/` |
| "Moving load", "DLOAD", "Non-uniform pressure" | `reference/load/` |
| "Custom boundary", "DISP", "Prescribed displacement" | `reference/boundary/` |
| "Field variable", "USDFLD", "Spatial property variation" | `reference/field/` |
| "Initial stress", "SIGINI", "Residual stress", "Geostress" | `reference/initial/` |
| "Friction model", "FRIC", "Tribology" | `reference/friction/` |
| "Heat generation", "HETVAL", "Curing", "Hydration" | `reference/thermal/` |
| "Custom element", "UEL", "VUEL", "Special connection" | `reference/element/` |

## How Skills Work — Resolution Pattern

1. **Read `SKILL.md` first** — understand the skill's overview, functions, and quick reference
2. **Then dive into `reference/*.md`** — each contains complete, copy-paste-ready code templates
3. **Combine modules** — most analyses use `general/` + one specialized module
4. **Cross-reference the manual** — `manual.md` has example tutorials showing full workflows

## Script Generation Standard (Mandatory)

Every generated Python script MUST follow this structure:

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: [Static/Fatigue/XFEM/Thermal/Composite]
Description: [Brief description of what this script does]

User Input Parameters:
- param: value (unit) — description

Assumptions:
- [list any assumptions]
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# All user-modifiable parameters centralized here with unit comments

# ========== 2. Model Creation ==========

# ========== 3. Material & Section ==========

# ========== 4. Assembly ==========

# ========== 5. Step ==========

# ========== 6. Interactions ==========

# ========== 7. Loads & Boundary Conditions ==========

# ========== 8. Mesh ==========

# ========== 9. Job Submission ==========

# ========== 10. Post-Processing (optional) ==========
```

## AI Workflow When Generating Scripts

### Phase 1: Clarify (always do this first)
- Ask **at most 3-4** focused questions before writing code
- Confirm: material type, key dimensions, load magnitude, analysis type
- Provide sensible defaults to reduce user burden

### Phase 2: Select Modules
- Foundation (always needed): `general/SKILL.md` → `reference/modeling.md`, `material.md`, `step.md`, `bc_load.md`, `mesh.md`, `job.md`
- Specialized (pick based on analysis type): `static/`, `fatigue/`, `thermal/`, `xfem/`, `composite/`

### Phase 3: Generate
- Copy code from reference templates, adapt parameters
- Every line with a dimension MUST have a unit comment: `length = 100.0  # mm`
- Include verification checklist at the end

### Phase 4: Provide Run Instructions
- How to run in Abaqus CAE
- Verification checklist (geometry, materials, BCs, mesh)
- Common failure modes and debugging tips

## Unit System (N-mm-MPa — Always Used)

| Physical Quantity | Unit | Notes |
|------------------|------|-------|
| Length | mm | |
| Force | N | |
| Stress / Pressure / Elastic Modulus | MPa (N/mm²) | |
| Density | tonne/mm³ | kg/m³ × 10⁻¹² |
| Gravity | 9800 mm/s² | = 9.8 m/s² |
| Thermal conductivity | mW/(mm·K) | = W/(m·K), value unchanged |
| Specific heat | N·mm/(tonne·K) | J/(kg·K) × 10⁶ |
| Convection coefficient | mW/(mm²·K) | W/(m²·K) × 10⁻³ |
| Heat flux | mW/mm² | W/m² × 10⁻³ |
| Heat generation | mW/mm³ | W/m³ × 10⁻³ |
| Velocity | mm/s | = m/s × 10³ |

## Material Library Quick Lookup

| Material | E (MPa) | ν | Density (tonne/mm³) | Yield (MPa) |
|----------|---------|---|---------------------|-------------|
| Q235 Steel | 210000 | 0.3 | 7.85e-09 | 235 |
| Q345 Steel | 210000 | 0.3 | 7.85e-09 | 345 |
| Aluminum 6061 | 69000 | 0.33 | 2.70e-09 | 276 |
| Aluminum 7075 | 72000 | 0.33 | 2.81e-09 | 503 |
| Ti-6Al-4V | 113800 | 0.342 | 4.43e-09 | 880 |
| Concrete C30 | 30000 | 0.2 | 2.50e-09 | 30 (compressive) |

Full library with Python helper function: `abaqus_scriptcontrol_skills/general/reference/material.md`

## Common Element Types

| Element | When to Use |
|---------|-------------|
| C3D8R | General solid (default choice) |
| C3D8I | Bending-dominated problems |
| C3D10 | Complex geometry (free mesh) |
| S4R | General shell structures |
| B31 | Beam structures |

## Subroutine Rules

- **Fortran fixed format**: cols 1-5 (labels), col 6 (continuation), cols 7-72 (code)
- **Use `REAL*8`** for all floating-point variables; declare every variable explicitly —
  `ABA_PARAM.INC` implicitly types I–N as INTEGER, so e.g. an undeclared `N_HARD = 0.3` truncates to 0
- **Double-precision constants**: `1.0D0` not `1.0`
- **Always include `INCLUDE 'ABA_PARAM.INC'`** (Standard) or `include 'vaba_param.inc'` (Explicit subroutines)
- **Compile**: `abaqus make library=subroutine.f` or `abaqus job=jobname user=subroutine.f`

## Known Limitations

- **VRIC is the only supported subroutine type without a reference doc** (14 of 15 covered)
- **No automated tests** — all templates should be validated in Abaqus before use
- **No error handling** in most code templates — add try/except for production use
- **Python 3.9+ only** (Abaqus 2023+); Python 2.7 (Abaqus ≤ 2022) is not supported
- Unverified API items are tracked in `docs/ERRATA.md` (section 2) — check it before using those features

## File Organization

```
abaqus_skills/
├── CLAUDE.md                        # ← You are here (AI entry point)
├── AGENTS.md                        # Multi-agent entry point (Codex/opencode etc.)
├── abaqus_agent_playbook.md         # End-to-end agent workflow for Abaqus simulation tasks
├── README.md                        # Human-readable overview
├── CONTRIBUTING.md                  # How to add new skills
├── docs/
│   ├── ERRATA.md                    # Fixed bugs + unverified API items
│   └── agent_installation.md        # Install skills in every agent tool
├── scripts/                         # Standalone Python 3 helper tools
│   ├── unit_converter.py            # Unit-system conversion & validation
│   ├── inp_checker.py               # Static check of .inp files
│   ├── odb_extract.py               # CLI result extraction from .odb
│   └── job_monitor.sh               # Submit + monitor + log capture
├── abaqus_scriptcontrol_skills/
│   ├── manual.md                    # Detailed user manual with tutorials
│   ├── prompts/ai_guide.md          # Extended AI generation guide
│   ├── general/SKILL.md + reference/
│   ├── static/SKILL.md + reference/
│   ├── fatigue/SKILL.md + reference/
│   ├── thermal/SKILL.md + reference/
│   ├── xfem/SKILL.md + reference/
│   └── composite/SKILL.md + reference/
├── abaqus_subroutine_skills/
│   ├── SKILL.md                     # Subroutine overview
│   ├── manual.md                    # Detailed manual with tutorials
│   ├── reference/                   # Per-subroutine-type docs
│   └── official_examples/           # Raw Fortran examples from Abaqus docs
└── cross_module_examples/           # End-to-end Python+Fortran+post tasks
```

## Related Skills in This Repo

When a task requires both Python scripting AND Fortran subroutines (e.g., custom material model + Python setup script), load both module trees and coordinate.

## Agent Execution Loop (Mandatory for Full Tasks)

For any task that says "run the analysis" (not just "write the script"):

1. **Clarify** — ask ≤4 questions (material, dimensions, load, analysis type); propose defaults
2. **Generate** — per Script Generation Standard above; reference the appropriate SKILL.md tree
3. **Run headless** — `abaqus cae noGUI=script.py` then `abaqus job=Job-1` (see `general/reference/headless_execution.md`)
4. **Diagnose** — parse `.sta`/`.msg`/`.dat`; if errors → `error_diagnosis.md` decision table → fix → rerun
5. **Verify** — extract results from `.odb` (`postprocess_odb.md`); compare against analytical/expected values (`verification.md`)
6. **Report** — summary table: model summary, key results, verification status, warnings

Tools `scripts/unit_converter.py`, `scripts/inp_checker.py`, `scripts/odb_extract.py`,
`scripts/job_monitor.sh` exist for steps 3–5.
