# Abaqus 二次开发技能库 (Abaqus Development Skills Library)

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Abaqus](https://img.shields.io/badge/Abaqus-2016%2B-blue.svg)](https://www.3ds.com/products-services/simulia/products/abaqus/)
[![Python](https://img.shields.io/badge/Python-2.7%2F3.x-green.svg)](https://www.python.org/)
[![Fortran](https://img.shields.io/badge/Fortran-90%2B-purple.svg)](https://fortran-lang.org/)

[中文](#中文) | [English](#english)

</div>

---

<a name="中文"></a>
## 📚 中文介绍

### 项目简介

本项目是一个全面的 Abaqus 二次开发技能库，旨在帮助工程师、研究人员和学生快速掌握 Abaqus 的脚本控制和用户子程序开发技术。通过结构化的知识组织和丰富的示例代码，大幅降低 Abaqus 二次开发的学习门槛。

### 🎯 核心内容

本技能库包含两大核心模块：

#### 1. Abaqus 脚本控制技能 (`abaqus_scriptcontrol_skills/`)

使用 Python 语言进行 Abaqus 的自动化建模、分析和后处理。

**涵盖领域：**
- **通用技能** - 建模、材料、边界条件、网格、作业提交等基础操作
- **静力分析** - 线弹性分析、非线性静力分析
- **疲劳分析** - 高周疲劳、低周疲劳分析
- **热分析** - 热传导、热应力耦合分析
- **复合材料** - 层合板建模、失效分析
- **XFEM** - 裂纹扩展模拟

#### 2. Abaqus 子程序技能 (`abaqus_subroutine_skills/`)

使用 Fortran 语言开发自定义用户子程序，扩展 Abaqus 功能。

**子程序类型：**
| 子程序 | 功能描述 | 适用求解器 |
|--------|----------|------------|
| UMAT | 自定义材料本构 | Standard |
| VUMAT | 自定义材料本构 | Explicit |
| DLOAD/VDLOAD | 分布载荷定义 | Standard/Explicit |
| DISP/VDISP | 自定义位移边界 | Standard/Explicit |
| USDFLD | 自定义场变量 | 通用 |
| SIGINI/SDVINI | 初始应力/状态变量 | 通用 |
| FRIC/VRIC | 自定义摩擦 | Standard/Explicit |
| HETVAL | 热生成 | 热分析 |
| UEL/VUEL | 自定义单元 | Standard/Explicit |

### 📁 项目结构

```
abaqus-skills/
├── README.md                          # 本文件
├── LICENSE                            # MIT 许可证
├── .gitignore                         # Git 忽略文件
│
├── abaqus_scriptcontrol_skills/       # 脚本控制技能库
│   ├── manual.md                      # 使用手册
│   ├── README.md                      # 模块说明
│   ├── prompts/                       # AI 提示词指南
│   ├── general/                       # 通用技能
│   │   ├── skill_modeling.md
│   │   ├── skill_material.md
│   │   ├── skill_bc_load.md
│   │   ├── skill_mesh.md
│   │   └── ...
│   ├── static/                        # 静力分析
│   ├── fatigue/                       # 疲劳分析
│   ├── thermal/                       # 热分析
│   ├── composite/                     # 复合材料
│   ├── xfem/                          # XFEM 裂纹分析
│   └── examples/                      # 综合示例
│
└── abaqus_subroutine_skills/          # 子程序技能库
    ├── manual.md                      # 使用手册
    ├── material/                      # 材料子程序
    │   ├── skill_umat_elastic.md
    │   └── skill_umat_plasticity.md
    ├── load/                          # 载荷子程序
    ├── boundary/                      # 边界条件子程序
    ├── initial/                       # 初始条件子程序
    ├── field/                         # 场变量子程序
    ├── friction/                      # 摩擦子程序
    ├── thermal/                       # 热分析子程序
    ├── element/                       # 自定义单元
    ├── examples/                      # 完整示例
    └── official_examples/             # 官方示例代码
        ├── umat/
        ├── vumat/
        ├── dload/
        └── ...
```

### 🚀 快速开始

#### 环境要求

- **Abaqus**: 2016 或更高版本
- **Python**: 2.7 或 3.x (取决于 Abaqus 版本)
- **Fortran 编译器**: Intel Fortran 或 GNU Fortran (用于子程序)

#### 使用脚本控制技能

1. **浏览技能文档**
   ```bash
   cd abaqus_scriptcontrol_skills
   # 查看 manual.md 了解使用方法
   ```

2. **使用技能模块**
   
   每个 `.md` 文件包含可直接使用的代码模板。例如，在 `general/skill_modeling.md` 中找到建模相关的代码片段。

3. **组合生成完整脚本**
   
   根据分析需求，组合不同模块的代码片段，构建完整的分析脚本。

#### 使用子程序技能

1. **选择子程序类型**
   
   根据需求选择对应的子程序类型（如 UMAT、DLOAD 等）。

2. **查看技能文档**
   
   阅读对应目录下的 `.md` 文件，了解子程序的接口定义和使用方法。

3. **复制官方示例**
   
   `official_examples/` 目录包含可直接编译运行的官方示例代码。

4. **编译运行**
   ```bash
   # 示例：编译 UMAT 子程序
   abaqus make library=umat_elastic_official.f
   ```

### 📖 详细文档

- [脚本控制使用手册](abaqus_scriptcontrol_skills/manual.md)
- [子程序使用手册](abaqus_subroutine_skills/manual.md)
- [AI 提示词指南](abaqus_scriptcontrol_skills/prompts/ai_guide.md)

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！在贡献代码时，请确保：

1. 代码经过测试，可以在 Abaqus 中正常运行
2. 提供清晰的注释和说明文档
3. 遵循现有的文件组织和命名规范

### 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

---

<a name="english"></a>
## 📚 English Introduction

### Project Overview

This project is a comprehensive Abaqus development skills library, designed to help engineers, researchers, and students quickly master Abaqus scripting and user subroutine development. Through structured knowledge organization and rich code examples, it significantly lowers the learning curve for Abaqus customization.

### 🎯 Core Contents

This skills library contains two main modules:

#### 1. Abaqus Script Control Skills (`abaqus_scriptcontrol_skills/`)

Use Python for automated modeling, analysis, and post-processing in Abaqus.

**Coverage Areas:**
- **General Skills** - Modeling, materials, boundary conditions, meshing, job submission
- **Static Analysis** - Linear elastic and nonlinear static analysis
- **Fatigue Analysis** - High-cycle and low-cycle fatigue analysis
- **Thermal Analysis** - Heat transfer, thermal-stress coupling
- **Composite Materials** - Laminate modeling, failure analysis
- **XFEM** - Crack propagation simulation

#### 2. Abaqus Subroutine Skills (`abaqus_subroutine_skills/`)

Develop custom user subroutines using Fortran to extend Abaqus functionality.

**Subroutine Types:**
| Subroutine | Description | Solver |
|------------|-------------|--------|
| UMAT | Custom material constitutive | Standard |
| VUMAT | Custom material constitutive | Explicit |
| DLOAD/VDLOAD | Distributed load definition | Standard/Explicit |
| DISP/VDISP | Custom displacement BC | Standard/Explicit |
| USDFLD | User-defined field variables | General |
| SIGINI/SDVINI | Initial stress/state variables | General |
| FRIC/VRIC | Custom friction | Standard/Explicit |
| HETVAL | Heat generation | Thermal |
| UEL/VUEL | Custom elements | Standard/Explicit |

### 📁 Project Structure

```
abaqus-skills/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── .gitignore                         # Git ignore file
│
├── abaqus_scriptcontrol_skills/       # Script control skills
│   ├── manual.md                      # User manual
│   ├── README.md                      # Module documentation
│   ├── prompts/                       # AI prompt guides
│   ├── general/                       # General skills
│   │   ├── skill_modeling.md
│   │   ├── skill_material.md
│   │   ├── skill_bc_load.md
│   │   ├── skill_mesh.md
│   │   └── ...
│   ├── static/                        # Static analysis
│   ├── fatigue/                       # Fatigue analysis
│   ├── thermal/                       # Thermal analysis
│   ├── composite/                     # Composite materials
│   ├── xfem/                          # XFEM crack analysis
│   └── examples/                      # Comprehensive examples
│
└── abaqus_subroutine_skills/          # Subroutine skills
    ├── manual.md                      # User manual
    ├── material/                      # Material subroutines
    │   ├── skill_umat_elastic.md
    │   └── skill_umat_plasticity.md
    ├── load/                          # Load subroutines
    ├── boundary/                      # Boundary condition subroutines
    ├── initial/                       # Initial condition subroutines
    ├── field/                         # Field variable subroutines
    ├── friction/                      # Friction subroutines
    ├── thermal/                       # Thermal subroutines
    ├── element/                       # Custom elements
    ├── examples/                      # Complete examples
    └── official_examples/             # Official example codes
        ├── umat/
        ├── vumat/
        ├── dload/
        └── ...
```

### 🚀 Quick Start

#### Requirements

- **Abaqus**: 2016 or later
- **Python**: 2.7 or 3.x (depends on Abaqus version)
- **Fortran Compiler**: Intel Fortran or GNU Fortran (for subroutines)

#### Using Script Control Skills

1. **Browse skill documentation**
   ```bash
   cd abaqus_scriptcontrol_skills
   # Check manual.md for usage instructions
   ```

2. **Use skill modules**
   
   Each `.md` file contains ready-to-use code templates. For example, find modeling-related snippets in `general/skill_modeling.md`.

3. **Combine to create complete scripts**
   
   Based on your analysis needs, combine code snippets from different modules to build complete analysis scripts.

#### Using Subroutine Skills

1. **Select subroutine type**
   
   Choose the appropriate subroutine type based on your needs (e.g., UMAT, DLOAD).

2. **Review skill documentation**
   
   Read the `.md` files in the corresponding directories to understand interface definitions and usage.

3. **Copy official examples**
   
   The `official_examples/` directory contains official example code ready to compile and run.

4. **Compile and run**
   ```bash
   # Example: Compile UMAT subroutine
   abaqus make library=umat_elastic_official.f
   ```

### 📖 Detailed Documentation

- [Script Control Manual](abaqus_scriptcontrol_skills/manual.md)
- [Subroutine Manual](abaqus_subroutine_skills/manual.md)
- [AI Prompt Guide](abaqus_scriptcontrol_skills/prompts/ai_guide.md)

### 🤝 Contributing

Issues and Pull Requests are welcome! When contributing, please ensure:

1. Code is tested and runs properly in Abaqus
2. Clear comments and documentation are provided
3. Existing file organization and naming conventions are followed

### 📄 License

This project is open-sourced under the [MIT License](LICENSE).

---

<div align="center">

**Star ⭐ this repo if it helps you!**

Made with ❤️ by Abaqus developers for the Abaqus community

</div>
