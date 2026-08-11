# Abaqus Development Skills Library

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Abaqus](https://img.shields.io/badge/Abaqus-2023%2B-blue.svg)](https://www.3ds.com/products-services/simulia/products/abaqus/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![Fortran](https://img.shields.io/badge/Fortran-90%2B-purple.svg)](https://fortran-lang.org/)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard-orange)](https://agentskills.io)

[English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>

## Project Overview

This is a comprehensive **Abaqus Development Skills Library** designed to help engineers, researchers, and students quickly master Abaqus scripting control and user subroutine development technologies — and to let **AI agents** (Claude Code, OpenAI Codex, opencode, Gemini CLI, Cursor...) execute Abaqus simulation tasks end-to-end using the open [Agent Skills](https://agentskills.io) standard.

**Key features:**
- **Skills for agents**: progressive-disclosure `SKILL.md` + `reference/` templates
- **End-to-end agent loop**: headless run → log diagnosis → ODB post-processing → verification (see `abaqus_agent_playbook.md`)
- **Executable helpers**: `scripts/` (unit converter, .inp checker, ODB extractor, job monitor)
- **21 subroutine reference docs** incl. DFLUX/UMATHT/CREEP/UAMP/URDFIL/UEXTERNALDB/ORIENT
- **Corrected & unit-consistent** (N-mm-MPa only); see `docs/ERRATA.md`

---

## Installation

### Method 1: Claude Code Skills CLI (Recommended)

```bash
npx skills add jasonanewcoder/abaqus_skills
```

This registers all skills in the library with Claude Code. After installation, Claude will automatically load the relevant skill when you describe an Abaqus task.

> **Requirements**: [Node.js](https://nodejs.org/) ≥ 18 (for `npx`). Ships with Claude Code.

### Other Agents (Codex / opencode / Gemini CLI)

```bash
# Codex (user-level)
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.agents/skills/abaqus_skills
# opencode
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.config/opencode/skills/abaqus_skills
# Gemini CLI
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.gemini/skills/abaqus_skills
# repo-level (works for several tools)
mkdir -p .agents/skills && git clone https://github.com/jasonanewcoder/abaqus_skills.git .agents/skills/abaqus_skills
```

Full instructions: `docs/agent_installation.md`

### Method 2: Git Clone

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

Then add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "skills": {
    "abaqus_scriptcontrol_skills": "~/.claude/skills/abaqus_skills/abaqus_scriptcontrol_skills",
    "abaqus_subroutine_skills": "~/.claude/skills/abaqus_skills/abaqus_subroutine_skills"
  }
}
```

### Method 3: Windows — Git Bash / WSL

```bash
# In Git Bash or WSL terminal:
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

Or use `npx` in PowerShell / Command Prompt:

```cmd
npx skills add jasonanewcoder/abaqus_skills
```

### Method 4: Windows — Manual Download (No CLI Tools)

1. Visit [github.com/jasonanewcoder/abaqus_skills](https://github.com/jasonanewcoder/abaqus_skills)
2. Click **Code → Download ZIP**
3. Extract to `%USERPROFILE%\.claude\skills\abaqus_skills\`
4. Register in `%USERPROFILE%\.claude\settings.json` (see Method 2)

### Method 5: curl (macOS / Linux / Git Bash on Windows)

```bash
# Download a single skill reference directly
curl -O https://raw.githubusercontent.com/jasonanewcoder/abaqus_skills/main/abaqus_scriptcontrol_skills/general/SKILL.md

# Or download the entire repo as a tar archive (no git needed)
curl -L https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.tar.gz | tar xz -C ~/.claude/skills/
mv ~/.claude/skills/abaqus_skills-main ~/.claude/skills/abaqus_skills
```

### Method 6: PowerShell (Windows)

```powershell
# Download entire repo as ZIP
Invoke-WebRequest -Uri "https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.zip" -OutFile "$env:TEMP\abaqus_skills.zip"

# Extract
Expand-Archive -Path "$env:TEMP\abaqus_skills.zip" -DestinationPath "$env:USERPROFILE\.claude\skills\"

# Rename
Rename-Item "$env:USERPROFILE\.claude\skills\abaqus_skills-main" "$env:USERPROFILE\.claude\skills\abaqus_skills"
```

### Verify Installation

After installing with any method, verify Claude Code sees the skills:

```bash
# List installed skills
ls ~/.claude/skills/abaqus_skills/

# Or ask Claude in a conversation:
# "What Abaqus skills are available?"
```

---

## Core Modules

This skills library consists of two main modules:

### 1. Abaqus Script Control Skills (`abaqus_scriptcontrol_skills/`)

Uses Python language for automated modeling, analysis, and post-processing in Abaqus.

**Coverage Areas:**

| Category | Description |
|----------|-------------|
| **General** | Modeling, materials, BCs, meshing, steps, jobs **+ agent loop: headless execution, error diagnosis, ODB post-processing, interaction/contact, verification** |
| **Static Analysis** | Linear elastic analysis, nonlinear static analysis |
| **Fatigue Analysis** | High-cycle fatigue (S-N), low-cycle fatigue (Coffin-Manson, fe-safe) |
| **Thermal Analysis** | Heat transfer, thermal-stress coupling, welding |
| **Composite Materials** | Laminate modeling, Hashin/Tsai-Wu failure, continuum shells |
| **XFEM** | Crack propagation (XFEM) + VCCT crack growth |

**Directory Structure:**

```
abaqus_scriptcontrol_skills/
├── manual.md                      # User manual
├── manual_zh.md                   # Chinese manual
├── README.md                      # Module documentation
├── README_zh.md                   # Chinese documentation
├── general/                       # General skills
│   ├── SKILL.md                   # Overview
│   └── reference/                 # Reference documents
│       ├── modeling.md
│       ├── material.md
│       ├── bc_load.md
│       ├── mesh.md
│       ├── step.md
│       ├── job.md
│       ├── interaction_contact.md
│       ├── headless_execution.md
│       ├── error_diagnosis.md
│       ├── postprocess_odb.md
│       └── verification.md
├── static/                        # Static analysis
│   ├── SKILL.md
│   └── reference/
│       ├── linear.md
│       └── nonlinear.md
├── fatigue/                       # Fatigue analysis
│   ├── SKILL.md
│   └── reference/
│       ├── high_cycle.md
│       └── low_cycle.md
├── thermal/                       # Thermal analysis
│   ├── SKILL.md
│   └── reference/
│       ├── steady_state.md
│       └── transient.md
├── composite/                     # Composite materials
│   ├── SKILL.md
│   └── reference/
│       ├── layup_definition.md
│       ├── failure_analysis.md
│       └── tsaiwu_continuum_shell.md
└── xfem/                          # XFEM crack analysis
    ├── SKILL.md
    └── reference/
        ├── crack_initiation.md
        └── vcct_fracture.md
```

### 2. Abaqus Subroutine Skills (`abaqus_subroutine_skills/`)

Uses Fortran language to develop custom user subroutines, extending Abaqus functionality.

**Subroutine Types:**

| Subroutine | Function Description | Applicable Solver |
|------------|---------------------|-------------------|
| UMAT | Custom material constitutive model | Standard |
| VUMAT | Custom material constitutive model | Explicit |
| CREEP | Creep / viscoplastic material | Standard |
| UMATHT | Custom thermal constitutive model | Standard (Thermal) |
| DLOAD | Distributed load definition | Standard |
| VDLOAD | Distributed load definition | Explicit |
| DFLUX | Moving heat source / heat flux | Thermal |
| DISP | Custom displacement boundary | Standard |
| VDISP | Custom displacement boundary | Explicit |
| USDFLD | User-defined field variables | General |
| ORIENT | Material orientation | General |
| SIGINI | Initial stress definition | General |
| SDVINI | Initial state variables | General |
| FRIC | Custom friction model | Standard |
| HETVAL | Heat generation | Thermal |
| FILM | Custom convection | Thermal |
| UEL | User-defined element | Standard |
| VUEL | User-defined element | Explicit |
| UAMP | Custom amplitude / control | General |
| UEXTERNALDB | Job I/O management | General |
| URDFIL | Results file filtering | General |

**Directory Structure:**

```
abaqus_subroutine_skills/
├── manual.md                      # User manual
├── manual_zh.md                   # Chinese manual
├── README.md                       # Module documentation
├── README_zh.md                    # Chinese documentation
├── SKILL.md                        # Skills overview
├── official_examples/              # Official example codes
│   ├── umat/
│   │   ├── umat_elastic_official.f
│   │   └── umat_mises_plasticity_official.f
│   ├── vumat/
│   ├── dload/
│   ├── vdload/
│   ├── disp/
│   ├── vdisp/
│   ├── usdfld/
│   ├── sigini/
│   ├── sdvini/
│   ├── fric/
│   ├── hetval/
│   ├── uel/
│   ├── film/
│   └── ...
└── reference/                     # Reference documents
    ├── material/
    │   ├── umat_elastic.md
    │   ├── umat_plasticity.md
    │   ├── vumat_elastic.md
    │   └── creep_material.md
    ├── load/
    │   ├── dload_moving.md
    │   ├── vdload_moving.md
    │   └── uamp_amplitude.md
    ├── boundary/
    │   ├── disp_control.md
    │   └── vdisp_control.md
    ├── initial/
    │   ├── sigini_stress.md
    │   └── sdvini_state_variables.md
    ├── field/
    │   ├── usdfld_spatial.md
    │   └── orient_direction.md
    ├── friction/
    │   └── fric_contact.md
    ├── thermal/
    │   ├── hetval_heat.md
    │   ├── film_convection.md
    │   ├── dflux_welding.md
    │   └── umatht_thermal.md
    ├── element/
    │   └── uel_spring.md
    ├── output/
    │   └── urdfil_results.md
    └── utility/
        └── uexternaldb_mgmt.md
```

---

## Quick Start

### Requirements

- **Abaqus**: 2023 or later (Python 3.9+/3.10)
- **Python**: 3.9+ for `scripts/` tools (run with system python3)
- **Fortran Compiler**: Intel Fortran or GNU Fortran (for subroutines)

### Run a Simulation with an AI Agent

```
1. Read abaqus_agent_playbook.md (the agent loop)
2. Build:   abaqus cae noGUI=model_setup.py
3. Check:   python3 scripts/inp_checker.py Job-1.inp
4. Run:     scripts/job_monitor.sh Job-1 cpus=4
5. Results: abaqus python scripts/odb_extract.py Job-1.odb --field U --max
```

### Using Script Control Skills

1. **Browse skill documentation**
   ```bash
   cd abaqus_scriptcontrol_skills
   # Read manual.md for usage instructions
   ```

2. **Use skill modules**
   
   Each `.md` file contains ready-to-use code templates. For example, find modeling-related snippets in `general/reference/modeling.md`.

3. **Combine to create complete scripts**
   
   Based on your analysis needs, combine code snippets from different modules to build complete analysis scripts.

### Using Subroutine Skills

1. **Select subroutine type**
   
   Choose the appropriate subroutine type based on your needs (e.g., UMAT, DLOAD).

2. **Review skill documentation**
   
   Read the `.md` files in the `reference/` directories to understand interface definitions and usage.

3. **Copy official examples**
   
   The `official_examples/` directory contains official example code ready to compile and run.

4. **Compile and run**
   ```bash
   # Example: Compile UMAT subroutine
   abaqus make library=umat_elastic_official.f
   ```

---

## Documentation

- [Agent Playbook](abaqus_agent_playbook.md) — end-to-end execution loop for AI agents
- [Script Control Manual](abaqus_scriptcontrol_skills/manual.md)
- [Subroutine Manual](abaqus_subroutine_skills/manual.md)
- [Script Control Chinese Manual](abaqus_scriptcontrol_skills/manual_zh.md)
- [Subroutine Chinese Manual](abaqus_subroutine_skills/manual_zh.md)
- [Errata & Known Issues](docs/ERRATA.md)
- [Agent Installation](docs/agent_installation.md)

---

## Contributing

Issues and Pull Requests are welcome! When contributing, please ensure:

1. Code is tested and runs properly in Abaqus
2. Clear comments and documentation are provided
3. Existing file organization and naming conventions are followed

---

## License

This project is open-sourced under the [MIT License](LICENSE).

---

<div align="center">

**Star ⭐ this repo if it helps you!**

Made with ❤️ by Abaqus developers for the Abaqus community

</div>

---

<a name="中文"></a>

## 中文介绍

本项目是一个全面的 **Abaqus 二次开发技能库**，旨在帮助工程师、研究人员和学生快速掌握 Abaqus 的脚本控制和用户子程序开发技术。通过结构化的知识组织和丰富的示例代码，大幅降低 Abaqus 二次开发的学习门槛。

### 安装方法

#### 方法一：Claude Code Skills CLI（推荐）

```bash
npx skills add jasonanewcoder/abaqus_skills
```

安装后，Claude 会在您描述 Abaqus 任务时自动加载相应技能。

> **环境要求**：[Node.js](https://nodejs.org/) ≥ 18（`npx` 随 Claude Code 附带）。

#### 方法二：Git Clone

```bash
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

#### 方法三：Windows — Git Bash / WSL

```bash
# 在 Git Bash 或 WSL 终端中：
git clone https://github.com/jasonanewcoder/abaqus_skills.git ~/.claude/skills/abaqus_skills
```

或在 PowerShell / 命令提示符中：

```cmd
npx skills add jasonanewcoder/abaqus_skills
```

#### 方法四：Windows — 手动下载（无需命令行工具）

1. 访问 [github.com/jasonanewcoder/abaqus_skills](https://github.com/jasonanewcoder/abaqus_skills)
2. 点击 **Code → Download ZIP**
3. 解压到 `%USERPROFILE%\.claude\skills\abaqus_skills\`

#### 方法五：curl（macOS / Linux / Windows Git Bash）

```bash
curl -L https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.tar.gz | tar xz -C ~/.claude/skills/
mv ~/.claude/skills/abaqus_skills-main ~/.claude/skills/abaqus_skills
```

#### 方法六：PowerShell（Windows）

```powershell
Invoke-WebRequest -Uri "https://github.com/jasonanewcoder/abaqus_skills/archive/refs/heads/main.zip" -OutFile "$env:TEMP\abaqus_skills.zip"
Expand-Archive -Path "$env:TEMP\abaqus_skills.zip" -DestinationPath "$env:USERPROFILE\.claude\skills\"
Rename-Item "$env:USERPROFILE\.claude\skills\abaqus_skills-main" "$env:USERPROFILE\.claude\skills\abaqus_skills"
```

#### 验证安装

```bash
ls ~/.claude/skills/abaqus_skills/
```

### 核心模块

本技能库包含两大核心模块：

#### 1. Abaqus 脚本控制技能 (`abaqus_scriptcontrol_skills/`)

使用 Python 语言进行 Abaqus 的自动化建模、分析和后处理。

**涵盖领域：**
- **通用技能** - 建模、材料、边界条件、网格、步骤设置、作业提交
- **静力分析** - 线弹性分析、非线性静力分析
- **疲劳分析** - 高周疲劳、低周疲劳
- **热分析** - 热传导、热应力耦合
- **复合材料** - 层合板建模、失效分析
- **XFEM** - 裂纹扩展模拟

#### 2. Abaqus 子程序技能 (`abaqus_subroutine_skills/`)

使用 Fortran 语言开发自定义用户子程序，扩展 Abaqus 功能。

**子程序类型：**
- UMAT - 自定义材料本构（Standard求解器）
- VUMAT - 自定义材料本构（Explicit求解器）
- DLOAD/VDLOAD - 分布载荷定义
- DISP/VDISP - 自定义位移边界
- USDFLD - 自定义场变量
- SIGINI/SDVINI - 初始应力/状态变量
- FRIC/VRIC - 自定义摩擦模型
- HETVAL - 热生成
- UEL/VUEL - 自定义单元

### 快速开始

**环境要求：**
- Abaqus 2023 或更高版本（Python 3.9+）
- Python 3.9+（运行 `scripts/` 辅助工具）
- Fortran 编译器：Intel Fortran 或 GNU Fortran

**使用方法：**

脚本控制技能：
1. 阅读 `manual.md` 了解使用方法
2. 参考各模块的 `.md` 文件获取代码模板
3. 组合不同模块的代码片段构建完整脚本

子程序技能：
1. 选择对应的子程序类型
2. 阅读 `reference/` 目录下的文档
3. 参考 `official_examples/` 中的官方示例
4. 使用 `abaqus make` 命令编译子程序

**AI Agent 端到端执行（Codex / Claude Code / opencode 等）：**
1. 阅读 `abaqus_agent_playbook.md`（执行闭环：澄清→生成→无头运行→诊断→迭代→验证→报告）
2. 建模：`abaqus cae noGUI=model_setup.py`
3. 检查：`python3 scripts/inp_checker.py Job-1.inp`
4. 提交监控：`scripts/job_monitor.sh Job-1 cpus=4`
5. 结果提取：`abaqus python scripts/odb_extract.py Job-1.odb --field U --max`

### 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

---

<div align="center">

**如果对您有帮助，请给我们一个 ⭐！**

由 Abaqus 开发者为 Abaqus 社区贡献

</div>
