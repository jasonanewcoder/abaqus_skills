# CLAUDE.md — Abaqus Development Skills Library

## Project Identity

This is a **Claude Code skills library for Abaqus secondary development** — structured knowledge organized as skills that Claude can use to generate production-quality Abaqus Python scripts and Fortran user subroutines.

- **Two modules**: Script Control (Python) + User Subroutines (Fortran)
- **Bilingual**: English and Chinese (中文) documentation throughout
- **Skill format**: Each skill = `SKILL.md` (overview + code snippets) + `reference/` (complete templates)
- **Default unit system**: N-mm-MPa (length=mm, force=N, stress=MPa, density=tonne/mm³)

## Installation

When a user asks about installing these skills, recommend the appropriate method:

**Recommended** (any platform with Node.js):
```bash
npx skills add jasonanewcoder/abaqus_skills
```

**Git Clone** (macOS / Linux / Git Bash on Windows):
```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

**curl** (macOS / Linux / Git Bash — no git needed):
```bash
curl -L https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.tar.gz | tar xz -C ~/.claude/skills/
mv ~/.claude/skills/abaqus_skills-main ~/.claude/skills/abaqus_skills
```

**Windows (PowerShell)**:
```powershell
Invoke-WebRequest -Uri "https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.zip" -OutFile "$env:TEMP\abaqus_skills.zip"
Expand-Archive -Path "$env:TEMP\abaqus_skills.zip" -DestinationPath "$env:USERPROFILE\.claude\skills\"
Rename-Item "$env:USERPROFILE\.claude\skills\abaqus_skills-main" "$env:USERPROFILE\.claude\skills\abaqus_skills"
```

**Manual** (any platform — no CLI required):
1. Visit https://github.com/jasonanewcoder/abaqus_skills
2. **Code → Download ZIP**
3. Extract to `~/.claude/skills/abaqus_skills/`

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
- **Use `REAL*8`** for all floating-point variables
- **Double-precision constants**: `1.0D0` not `1.0`
- **Always include `INCLUDE 'ABA_PARAM.INC'`**
- **Compile**: `abaqus make library=subroutine.f` or `abaqus job=jobname user=subroutine.f`

## Known Limitations

- **Subroutine reference docs are incomplete** — currently 8 of 15 subroutine types have reference docs
- **Fatigue/thermal/XFEM/composite SKILL.md files are thin** — overview only, no detailed reference docs
- **No error handling** in code templates — add try/except for production use
- **Python 2.7 compatibility** listed but untested; modern Abaqus (2020+) uses Python 3
- **No automated tests** — all templates should be validated in Abaqus before use

## File Organization

```
abaqus_skills/
├── CLAUDE.md                        # ← You are here (AI entry point)
├── README.md                        # Human-readable overview
├── CONTRIBUTING.md                  # How to add new skills
├── abaqus_scriptcontrol_skills/
│   ├── manual.md                    # Detailed user manual with tutorials
│   ├── prompts/ai_guide.md          # Extended AI generation guide
│   ├── general/SKILL.md + reference/
│   ├── static/SKILL.md + reference/
│   ├── fatigue/SKILL.md
│   ├── thermal/SKILL.md
│   ├── xfem/SKILL.md
│   └── composite/SKILL.md
└── abaqus_subroutine_skills/
    ├── SKILL.md                     # Subroutine overview
    ├── manual.md                    # Detailed manual with tutorials
    ├── reference/                   # Per-subroutine-type docs
    └── official_examples/           # Raw Fortran examples from Abaqus docs
```

## Related Skills in This Repo

When a task requires both Python scripting AND Fortran subroutines (e.g., custom material model + Python setup script), load both module trees and coordinate.
