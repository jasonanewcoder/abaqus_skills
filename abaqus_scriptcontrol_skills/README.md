# Abaqus Skills Corpus

## Project Introduction

This skills corpus is designed to provide AI programming assistants with structured Abaqus secondary development knowledge, helping users quickly generate high-quality, runnable Abaqus Python scripts through natural language descriptions.

## Core Objectives

- **Lower the Barrier**: Users don't need to memorize complex Abaqus APIs; scripts can be generated through natural language
- **Ensure Quality**: Provide verified code templates and best practices
- **Comprehensive Coverage**: From basic modeling to advanced analysis (static/fatigue/XFEM/thermal stress/composite materials)
- **Fast Iteration**: Support conversational requirement clarification, quickly converging to user's true needs

## Directory Structure

```
abaqus_scriptcontrol_skills/
├── README.md                 # This file
├── manual.md                 # User manual (English)
├── manual_zh.md              # 用户手册 (中文)
├── prompts/                  # AI prompt guides
│   └── ai_guide.md
├── general/                  # General skills (Claude Code Skill format)
│   ├── SKILL.md             # Skill main file
│   └── reference/           # Detailed reference documentation
│       ├── modeling.md      # Geometric modeling
│       ├── material.md      # Material definition
│       ├── step.md          # Step setup
│       ├── bc_load.md       # Boundary conditions and loads
│       ├── mesh.md          # Mesh generation
│       └── job.md           # Job submission
├── static/                   # Static analysis skills
│   ├── SKILL.md
│   └── reference/
│       ├── linear.md        # Linear static analysis
│       └── nonlinear.md     # Nonlinear static analysis
├── fatigue/                  # Fatigue analysis skills
│   ├── SKILL.md
│   └── reference/
│       └── high_cycle.md    # High-cycle fatigue
├── xfem/                     # Extended Finite Element XFEM
│   ├── SKILL.md
│   └── reference/
│       └── crack.md         # XFEM crack analysis
├── thermal/                  # Thermal stress analysis
│   ├── SKILL.md
│   └── reference/
│       └── stress.md        # Thermal stress analysis
├── composite/                # Composite material analysis
│   ├── SKILL.md
│   └── reference/
│       └── shell.md         # Composite laminate
└── examples/                 # Comprehensive examples
    └── example_pressure_vessel.md
```

## Skill Modules

### General Skills (general/)

Basic operations for all analysis types:
- Geometric modeling (sketch, extrusion, revolution, cutting)
- Material property definition (isotropic/anisotropic)
- Section properties (solid/shell/beam)
- Assembly and constraints
- Step setup
- Boundary conditions and loads
- Mesh generation techniques
- Job submission and monitoring
- Result extraction and visualization

### Static Analysis (static/)

- **Linear Static Analysis**: Small deformation, linear elastic materials
- **Nonlinear Static Analysis**: Large deformation, material nonlinearity, contact

### Fatigue Analysis (fatigue/)

- **High-cycle Fatigue**: Stress-based S-N curve method

### Extended Finite Element XFEM (xfem/)

- **Crack Analysis**: Extended Finite Element Method, damage evolution

### Thermal Stress Analysis (thermal/)

- **Steady-state Heat Transfer**: Temperature field calculation
- **Transient Heat Transfer**: Time-varying temperature field
- **Thermal-mechanical Coupling**: Thermal stress calculation

### Composite Materials (composite/)

- **Laminated Shell Elements**: Classical laminate theory implementation
- **Failure Analysis**: Hashin failure criteria

## Claude Code Skill Format

This skills corpus is organized according to Claude Code's Skill format:

- **SKILL.md**: Main skill file, containing skill overview, function list, code snippets, and quick reference
- **reference/**: Detailed reference documentation directory, containing complete API references and code templates

### Usage

1. **View SKILL.md**: Understand skill functionality and basic usage
2. **View reference/**: Get detailed code templates and API references
3. **Combine Skills**: Combine multiple skill modules to generate complete scripts based on requirements

## Quick Start

### User Workflow

1. **Describe Requirements**: Describe your analysis needs in natural language
2. **AI Clarification**: AI confirms key details through concise dialogue
3. **Generate Script**: AI generates complete script based on confirmed requirements
4. **Run and Verify**: Run script in Abaqus and view results

### AI Usage Guide

AI assistants should follow these principles before generating scripts:

1. **Understand First, Then Generate**: Confirm user intent through 2-3 key questions
2. **Modular Construction**: Use skill modules from this corpus to build complete scripts
3. **Provide Comments**: Include clear step descriptions in the code
4. **Include Verification**: Provide verification checklist after generating scripts

See [`prompts/ai_guide.md`](prompts/ai_guide.md) for details.

## Script Standards

All generated scripts should follow these standards:

```python
# -*- coding: utf-8 -*-
"""
Analysis Type: [Static/Fatigue/XFEM/Thermal Stress/Composite Materials]
Created: YYYY-MM-DD
Description: [Brief description of analysis purpose]

Input parameters to confirm:
- [List parameters that need user input]
"""

from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Parameter Definition ==========
# All user-modifiable parameters are concentrated here

# ========== 2. Model Creation ==========
# Geometric modeling

# ========== 3. Material and Section ==========
# Material property definition

# ========== 4. Assembly ==========
# Part assembly

# ========== 5. Step ==========
# Step setup

# ========== 6. Interactions ==========
# Contact, constraints, etc.

# ========== 7. Loads and Boundary Conditions ==========
# Boundary condition and load application

# ========== 8. Mesh ==========
# Mesh generation

# ========== 9. Job Submission ==========
# Create and submit job

# ========== 10. Post-processing ==========
# Result extraction (optional)
```

## Contributing Guide

Contributions of new skill modules or improvements to existing modules are welcome. Please ensure:

1. Code has been actually tested in Abaqus
2. Includes complete comment explanations
3. Provides corresponding example files
4. Updates this documentation

## License

MIT License - Free to use and modify
