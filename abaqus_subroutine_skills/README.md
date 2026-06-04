# Abaqus Subroutine Skills Library

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## Overview

Structured Fortran subroutine knowledge for AI-assisted Abaqus user subroutine development. Covers UMAT/VUMAT, DLOAD/VDLOAD, DISP/VDISP, USDFLD, SIGINI/SDVINI, FRIC/VRIC, HETVAL/FILM, and UEL/VUEL.

**For detailed documentation, see [`manual.md`](manual.md)** and the **[AI generation guide](prompts/ai_guide.md)**.

## Quick Reference

| Subroutine | Solver | Purpose | Reference |
|-----------|--------|---------|-----------|
| UMAT | Standard | Custom material | `reference/material/umat_*.md` |
| VUMAT | Explicit | Custom material | `reference/material/vumat_*.md` |
| DLOAD | Standard | Distributed load | `reference/load/dload_moving.md` |
| VDLOAD | Explicit | Distributed load | `reference/load/vdload_moving.md` |
| DISP | Standard | Custom boundary | `reference/boundary/disp_control.md` |
| VDISP | Explicit | Custom boundary | `reference/boundary/vdisp_control.md` |
| USDFLD | General | Field variables | `reference/field/usdfld_spatial.md` |
| SIGINI | General | Initial stress | `reference/initial/sigini_stress.md` |
| SDVINI | General | Initial state variables | `reference/initial/sdvini_state_variables.md` |
| FRIC | Standard | Custom friction | `reference/friction/fric_contact.md` |
| HETVAL | Thermal | Heat generation | `reference/thermal/hetval_heat.md` |
| FILM | Thermal | Custom convection | `reference/thermal/film_convection.md` |
| UEL | Standard | Custom element | `reference/element/uel_spring.md` |

## Quick Start

```
1. Read SKILL.md for overall capabilities
2. Select a reference file based on your need
3. Copy and modify the code template
4. Compile: abaqus make library=subroutine.f
5. Run: abaqus job=jobname user=subroutine.f
```

## Directory Structure

```
abaqus_subroutine_skills/
├── SKILL.md                  # Main skill file
├── manual.md                 # Full manual (tutorials, best practices)
├── manual_zh.md              # Chinese manual
├── README.md                 # ← This file (brief overview)
├── prompts/ai_guide.md       # AI subroutine generation guide
├── reference/                # Reference documentation
│   ├── material/             # UMAT/VUMAT
│   ├── load/                 # DLOAD/VDLOAD
│   ├── boundary/             # DISP/VDISP
│   ├── field/                # USDFLD
│   ├── initial/              # SIGINI/SDVINI
│   ├── thermal/              # HETVAL/FILM
│   ├── friction/             # FRIC/VRIC
│   └── element/              # UEL/VUEL
└── official_examples/        # Verified Fortran examples
```

## Requirements

- Abaqus 2020 or later
- Intel Fortran 19.0+ or GNU Fortran 9.0+
- Fixed-format Fortran knowledge

## License

Provided for educational and research purposes under MIT License.

---

<a name="中文"></a>

## 概述

用于AI辅助Abaqus用户子程序开发的结构化Fortran知识库。涵盖UMAT/VUMAT、DLOAD/VDLOAD、DISP/VDISP、USDFLD、SIGINI/SDVINI、FRIC/VRIC、HETVAL/FILM和UEL/VUEL。

**详细文档请参见 [`manual_zh.md`](manual_zh.md)** 和 **[AI生成指南](prompts/ai_guide.md)**。

### 快速参考

| 子程序 | 求解器 | 用途 | 参考 |
|--------|-------|------|------|
| UMAT | Standard | 自定义材料 | `reference/material/umat_*.md` |
| VUMAT | Explicit | 自定义材料 | `reference/material/vumat_*.md` |
| DLOAD | Standard | 分布载荷 | `reference/load/dload_moving.md` |
| VDLOAD | Explicit | 分布载荷 | `reference/load/vdload_moving.md` |
| DISP | Standard | 自定义边界 | `reference/boundary/disp_control.md` |
| VDISP | Explicit | 自定义边界 | `reference/boundary/vdisp_control.md` |
| USDFLD | 通用 | 场变量 | `reference/field/usdfld_spatial.md` |
| SIGINI | 通用 | 初始应力 | `reference/initial/sigini_stress.md` |
| SDVINI | 通用 | 初始状态变量 | `reference/initial/sdvini_state_variables.md` |
| FRIC | Standard | 自定义摩擦 | `reference/friction/fric_contact.md` |
| HETVAL | 热分析 | 热生成 | `reference/thermal/hetval_heat.md` |
| FILM | 热分析 | 自定义对流 | `reference/thermal/film_convection.md` |
| UEL | Standard | 自定义单元 | `reference/element/uel_spring.md` |

### 快速上手

```
1. 阅读 SKILL.md 了解整体功能
2. 根据需求选择参考文件
3. 复制并修改代码模板
4. 编译：abaqus make library=subroutine.f
5. 运行：abaqus job=jobname user=subroutine.f
```

### 环境要求

- Abaqus 2020 或更高版本
- Intel Fortran 19.0+ 或 GNU Fortran 9.0+

### 许可证

MIT License，仅供教育和研究使用。
