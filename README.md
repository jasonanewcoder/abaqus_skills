# Abaqus Development Skills Library

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Abaqus](https://img.shields.io/badge/Abaqus-2016%2B-blue.svg)](https://www.3ds.com/products-services/simulia/products/abaqus/)
[![Python](https://img.shields.io/badge/Python-2.7%2F3.x-green.svg)](https://www.python.org/)
[![Fortran](https://img.shields.io/badge/Fortran-90%2B-purple.svg)](https://fortran-lang.org/)

[English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>

## Project Overview

This is a comprehensive **Abaqus Development Skills Library** designed to help engineers, researchers, and students quickly master Abaqus scripting control and user subroutine development technologies. Through structured knowledge organization and rich example code, it significantly reduces the learning curve for Abaqus customization.

---

## Core Modules

This skills library consists of two main modules:

### 1. Abaqus Script Control Skills (`abaqus_scriptcontrol_skills/`)

Uses Python language for automated modeling, analysis, and post-processing in Abaqus.

**Coverage Areas:**

| Category | Description |
|----------|-------------|
| **General** | Modeling, materials, boundary conditions, meshing, step settings, job submission |
| **Static Analysis** | Linear elastic analysis, nonlinear static analysis |
| **Fatigue Analysis** | High-cycle fatigue, low-cycle fatigue |
| **Thermal Analysis** | Heat transfer, thermal-stress coupling |
| **Composite Materials** | Laminate modeling, failure analysis |
| **XFEM** | Crack propagation simulation |

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
│       └── job.md
├── static/                        # Static analysis
│   ├── SKILL.md
│   └── reference/
│       ├── linear.md
│       └── nonlinear.md
├── fatigue/                       # Fatigue analysis
│   └── SKILL.md
├── thermal/                       # Thermal analysis
│   └── SKILL.md
├── composite/                     # Composite materials
│   └── SKILL.md
└── xfem/                          # XFEM crack analysis
    └── SKILL.md
```

### 2. Abaqus Subroutine Skills (`abaqus_subroutine_skills/`)

Uses Fortran language to develop custom user subroutines, extending Abaqus functionality.

**Subroutine Types:**

| Subroutine | Function Description | Applicable Solver |
|------------|---------------------|-------------------|
| UMAT | Custom material constitutive model | Standard |
| VUMAT | Custom material constitutive model | Explicit |
| DLOAD | Distributed load definition | Standard |
| VDLOAD | Distributed load definition | Explicit |
| DISP | Custom displacement boundary | Standard |
| VDISP | Custom displacement boundary | Explicit |
| USDFLD | User-defined field variables | General |
| SIGINI | Initial stress definition | General |
| SDVINI | Initial state variables | General |
| FRIC | Custom friction model | Standard |
| VRIC | Custom friction model | Explicit |
| HETVAL | Heat generation | Thermal |
| UEL | User-defined element | Standard |
| VUEL | User-defined element | Explicit |

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
│   ├── vric/
│   ├── hetval/
│   ├── uel/
│   ├── vuEL/
│   ├── film/
│   └── ...
└── reference/                     # Reference documents
    ├── material/
    │   ├── umat_elastic.md
    │   ├── umat_plasticity.md
    │   └── vumat_elastic.md
    ├── load/
    │   └── dload_moving.md
    ├── boundary/
    │   └── disp_control.md
    ├── initial/
    │   └── sigini_stress.md
    ├── field/
    │   └── usdfld_spatial.md
    ├── friction/
    │   └── fric_contact.md
    ├── thermal/
    │   └── hetval_heat.md
    └── element/
        └── uel_spring.md
```

---

## Quick Start

### Requirements

- **Abaqus**: 2016 or later
- **Python**: 2.7 or 3.x (depends on Abaqus version)
- **Fortran Compiler**: Intel Fortran or GNU Fortran (for subroutines)

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

- [Script Control Manual](abaqus_scriptcontrol_skills/manual.md)
- [Subroutine Manual](abaqus_subroutine_skills/manual.md)
- [Script Control Chinese Manual](abaqus_scriptcontrol_skills/manual_zh.md)
- [Subroutine Chinese Manual](abaqus_subroutine_skills/manual_zh.md)

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
- Abaqus 2016 或更高版本
- Python 2.7 或 3.x（取决于 Abaqus 版本）
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

### 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

---

<div align="center">

**如果对您有帮助，请给我们一个 ⭐！**

由 Abaqus 开发者为 Abaqus 社区贡献

</div>
