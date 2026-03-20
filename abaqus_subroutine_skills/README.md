# Abaqus Subroutine Skills Library

[English](#english) | [中文](#中文)

---

## English

### Overview

This is a comprehensive skill library for developing Abaqus user subroutines. It provides AI-assisted programming guidance with standardized Fortran code templates, detailed theoretical explanations, and complete engineering examples.

### Features

- **Multiple Subroutine Types**: UMAT, VUMAT, DLOAD, VDLOAD, DISP, VDISP, USDFLD, SIGINI, SDVINI, FRIC, VRIC, HETVAL, FILM, UEL, VUEL
- **Complete Templates**: Ready-to-use Fortran code for various engineering applications
- **Theoretical Background**: Mathematical formulas and physical models
- **Best Practices**: Code standards, debugging tips, and performance optimization
- **Troubleshooting Guide**: Common errors and solutions

### Directory Structure

```
abaqus_subroutine_skills/
├── SKILL.md              # Main skill file (Claude Code format)
├── manual.md             # English manual
├── manual_zh.md          # Chinese manual
├── README.md             # This file
├── README_zh.md          # Chinese README
├── reference/            # Reference documentation
│   ├── material/         # Material subroutines
│   ├── load/            # Load subroutines
│   ├── boundary/        # Boundary subroutines
│   ├── field/           # Field variable subroutines
│   ├── initial/         # Initial condition subroutines
│   ├── thermal/         # Thermal subroutines
│   ├── friction/        # Friction subroutines
│   └── element/         # Custom element subroutines
└── official_examples/    # Official Abaqus examples
```

### Quick Start

1. **Read the SKILL.md** to understand the overall capabilities
2. **Select a reference file** based on your requirement (see manual for guidance)
3. **Copy and modify** the code template for your specific problem
4. **Compile and test** following the instructions in the reference

### Requirements

- Abaqus 2020 or later
- Intel Fortran 19.0+ or GNU Fortran 9.0+
- Basic knowledge of Fortran programming
- Familiarity with Abaqus FEA software

### Version

- Current Version: 1.0
- Last Updated: 2026-03-20

### License

This skill library is provided for educational and research purposes.

---

## 中文

### 概述

这是一个全面的Abaqus用户子程序开发技能库。它提供AI辅助编程指导，包含标准化的Fortran代码模板、详细的理论说明和完整的工程示例。

### 功能特点

- **多种子程序类型**：UMAT、VUMAT、DLOAD、VDLOAD、DISP、VDISP、USDFLD、SIGINI、SDVINI、FRIC、VRIC、HETVAL、FILM、UEL、VUEL
- **完整模板**：可直接使用的Fortran代码，适用于各种工程应用
- **理论背景**：数学公式和物理模型
- **最佳实践**：编码规范、调试技巧和性能优化
- **故障排除指南**：常见错误和解决方案

### 目录结构

```
abaqus_subroutine_skills/
├── SKILL.md              # 主技能文件（Claude Code格式）
├── manual.md             # 英文手册
├── manual_zh.md          # 中文手册
├── README.md             # 本文件
├── README_zh.md          # 中文自述文件
├── reference/            # 参考文档
│   ├── material/         # 材料子程序
│   ├── load/            # 载荷子程序
│   ├── boundary/        # 边界子程序
│   ├── field/           # 场变量子程序
│   ├── initial/         # 初始条件子程序
│   ├── thermal/         # 热分析子程序
│   ├── friction/         # 摩擦子程序
│   └── element/         # 自定义单元子程序
└── official_examples/    # Abaqus官方示例
```

### 快速开始

1. **阅读SKILL.md** 了解整体功能
2. **选择参考文件** 根据您的需求（参见手册获取指导）
3. **复制并修改** 代码模板以适应您的具体问题
4. **编译测试** 按照参考文件中的说明进行

### 需求

- Abaqus 2020或更高版本
- Intel Fortran 19.0+ 或 GNU Fortran 9.0+
- Fortran编程基础知识
- 熟悉Abaqus有限元软件

### 版本

- 当前版本：1.0
- 最后更新：2026-03-20

### 许可证

本技能库仅供教育和研究目的使用。
