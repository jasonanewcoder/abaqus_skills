# CONTRIBUTING.md — Abaqus Development Skills Library

## Welcome!

Thank you for contributing to the Abaqus Development Skills Library. This document explains how to add new skills, improve existing ones, and maintain quality standards.

## Quick Reference

| Want to... | File to edit/create |
|------------|-------------------|
| Add a new script control skill | `abaqus_scriptcontrol_skills/<category>/SKILL.md` + `reference/` |
| Add a new subroutine skill | `abaqus_subroutine_skills/reference/<category>/<name>.md` |
| Add an official example | `abaqus_subroutine_skills/official_examples/<subroutine>/` |
| Fix a code template bug | Find the template in `reference/` and edit |
| Improve AI guidance | `prompts/ai_guide.md` (per module) |
| Update project docs | `CLAUDE.md`, `README.md`, `CONTRIBUTING.md` |

## Skill File Format

### Script Control Skills (`SKILL.md`)

Every `SKILL.md` file MUST have:

1. **YAML frontmatter** — metadata block at the top:

```yaml
---
name: abaqus-script-control-<category>
description: One-line summary of what this skill does
version: "1.0"
capabilities:
  - capability_one
  - capability_two
triggers:
  - "keyword that activates this skill"
  - "Chinese equivalent"
constraints:
  - "Known limitation"
---
```

2. **Overview section** — what the skill covers and when to use it
3. **Skills list** — each sub-skill with:
   - Name and identifier (e.g., `skill_modeling`)
   - Applicable scenarios
   - Code snippet (~10-20 lines)
   - Link to detailed reference doc
4. **Quick reference** — unit system, common parameters, element types
5. **Related skills** — cross-references to other SKILL.md files

### Reference Documentation (`reference/*.md`)

Each reference file MUST have:

1. **Overview** — what this reference covers
2. **Applicable scenarios** — when to use this template
3. **Core API** — the key Abaqus Python API calls
4. **Code templates** — at least 3 complete, copy-paste-ready templates:
   - Simple/basic template
   - Intermediate/variation template
   - Advanced/complex template
5. **Best practices** — tips for getting correct results
6. **Common errors** — error/cause/solution table
7. **Verification checklist** — checklist items in `- [ ]` format

### Subroutine Reference Files

Same as script reference, plus:

1. **Theoretical formulas** — mathematical equations (LaTeX-style blocks)
2. **Interface definition** — full subroutine signature with parameter table
3. **Input file examples** — Abaqus keyword syntax

## Code Template Standards

### Python (Script Control)

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: [category]
Description: [one-line purpose]

User Input Parameters:
- param: value (unit) — description
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# All user-modifiable parameters centralized here

# ... 10-step structure ...
```

- Always use **N-mm-MPa** unit system
- Every dimension MUST have a unit comment: `length = 100.0  # mm`
- Use meaningful names: `'Cantilever-Beam'` not `'Model-1'`
- Check for existing model/job names before creating: `if name in mdb.models.keys(): del mdb.models[name]`
- Templates must be runnable as-is (fill in placeholder values with realistic defaults)

### Fortran (Subroutines)

```fortran
      SUBROUTINE NAME(ARGS)
C
C     Brief description
C     Compatible: Abaqus/Standard or Abaqus/Explicit
C
      INCLUDE 'ABA_PARAM.INC'    ! Standard
C     include 'vaba_param.inc'   ! Explicit
C
      DIMENSION ...
      REAL*8 ...                 ! Always REAL*8
      INTEGER ...
C
C     Parameter definitions
      PARAMETER (...)
C
C     Main computation
      ...
C
      RETURN
      END
```

- Fixed-format Fortran: cols 1-5 (labels), col 6 (continuation `C` or non-zero), cols 7-72 (code)
- Always use `REAL*8` for floating point
- Double-precision constants: `1.0D0` not `1.0`
- Include `INCLUDE 'ABA_PARAM.INC'` (Standard) or `include 'vaba_param.inc'` (Explicit)
- Comment blocks describe each logical section

## Testing Requirements

Before submitting, verify:

1. **Python templates**: Test in Abaqus CAE (File → Run Script) with the parameter values as written
2. **Fortran templates**: Compile with `abaqus make library=subroutine.f` — at minimum, the code must compile without errors
3. **Reference docs**: All embedded code blocks should be syntactically valid
4. **No hardcoded paths**: Templates must not reference absolute file paths
5. **Unit consistency**: All values use N-mm-MPa (unless template explicitly uses a different system)

## Adding a New Skill Category (Script Control)

```
abaqus_scriptcontrol_skills/
└── <new_category>/
    ├── SKILL.md           # Frontmatter + overview + code snippets + quick reference
    └── reference/
        ├── <topic1>.md    # Detailed reference with templates
        └── <topic2>.md
```

1. Create the directory: `mkdir -p abaqus_scriptcontrol_skills/<new_category>/reference`
2. Write `SKILL.md` following the frontmatter + sections format
3. Write at least 2 reference docs with ≥ 3 templates each
4. Update `CLAUDE.md` to include the new skill in the "When to Use" table
5. Update `abaqus_scriptcontrol_skills/manual.md` to list the new module

## Adding a New Subroutine Reference

```
abaqus_subroutine_skills/reference/<category>/<subroutine_name>.md
```

1. Create the file in the appropriate `reference/<category>/` directory
2. Follow the subroutine reference format (theory + interface + code + verification)
3. Update `abaqus_subroutine_skills/SKILL.md` to reference the new file
4. Update `abaqus_subroutine_skills/manual.md` file-lookup tables

## Style Conventions

### Markdown
- Headings: `#` for document title, `##` for sections, `###` for subsections
- Code blocks: use fenced blocks with language identifier: ````python`, ````fortran`, ````abaqus`, ````bash
- Tables: use standard markdown pipe tables
- Links: use relative paths for internal references: `[text](../other/SKILL.md)`
- Checkboxes: `- [ ]` for unchecked, `- [x]` for checked

### Naming
- Files: `snake_case.md` (reference docs), `SKILL.md` (skill main files, uppercase)
- Directories: `snake_case/`
- Variables in templates: `snake_case` (Python), `UPPER_CASE` (Fortran)
- Job/model names: `Pascal-Case-With-Dashes`

## Pull Request Checklist

- [ ] Any new `SKILL.md` has YAML frontmatter
- [ ] All code templates have been tested in Abaqus
- [ ] Unit comments on every dimension value
- [ ] No hardcoded absolute paths
- [ ] Error/cause/solution tables for common issues
- [ ] Cross-reference links to related skills
- [ ] Bilingual parity: if you add EN content, add equivalent ZH content (or note "ZH pending")
- [ ] `CLAUDE.md` updated if adding new skill category
- [ ] `CONTRIBUTING.md` updated if changing contribution workflow

## Questions?

Open an issue on GitHub with the label `question` or `help-wanted`. For Abaqus-specific questions, refer to the [SIMULIA Knowledge Base](https://www.3ds.com/support/knowledge-base/).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers this project.
