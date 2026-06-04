# Abaqus Skills Corpus — Script Control Module

[English](#english) | [中文](#中文)

---

<a name="english"></a>

## Overview

Structured Abaqus Python scripting knowledge for AI-assisted code generation. Covering modeling, materials, boundary conditions, meshing, and specialized analysis types.

**For detailed documentation, see [`manual.md`](manual.md)**.

## Skills at a Glance

| Module | File | Key Topics |
|--------|------|------------|
| **General** | [`general/SKILL.md`](general/SKILL.md) | Modeling, materials, BCs, mesh, steps, job submission |
| **Static** | [`static/SKILL.md`](static/SKILL.md) | Linear elastic, nonlinear (plasticity, contact) |
| **Fatigue** | [`fatigue/SKILL.md`](fatigue/SKILL.md) | High-cycle S-N curve, mean stress correction |
| **Thermal** | [`thermal/SKILL.md`](thermal/SKILL.md) | Steady/transient heat transfer, thermal-stress coupling |
| **XFEM** | [`xfem/SKILL.md`](xfem/SKILL.md) | Crack initiation, propagation, damage evolution |
| **Composite** | [`composite/SKILL.md`](composite/SKILL.md) | Laminate layup, Hashin failure, progressive damage |

## Quick Start

```
User describes analysis → AI clarifies needs (2-3 questions) → AI generates script from skill templates
```

**For AI assistants**: See [`prompts/ai_guide.md`](prompts/ai_guide.md) for the generation workflow.

## Directory Structure

```
abaqus_scriptcontrol_skills/
├── manual.md              # Full user manual (tutorials, module details)
├── manual_zh.md           # Chinese manual
├── README.md              # ← This file (brief overview)
├── README_zh.md           # Chinese overview
├── prompts/ai_guide.md    # AI script generation guide
├── general/               # Foundation skills
│   ├── SKILL.md           # Overview + code snippets
│   └── reference/         # Complete code templates
├── static/                # Static analysis
│   ├── SKILL.md
│   └── reference/
├── fatigue/               # Fatigue analysis
│   ├── SKILL.md
│   └── reference/
├── thermal/               # Thermal analysis
│   ├── SKILL.md
│   └── reference/
├── xfem/                  # XFEM crack analysis
│   ├── SKILL.md
│   └── reference/
└── composite/             # Composite materials
    ├── SKILL.md
    └── reference/
```

## License

MIT License — see [LICENSE](../LICENSE) for details.

---

<a name="中文"></a>

## 概述

用于AI辅助代码生成的结构化Abaqus Python脚本知识库，涵盖建模、材料、边界条件、网格划分和各类专业分析类型。

**详细文档请参见 [`manual_zh.md`](manual_zh.md)**。

### 技能模块

| 模块 | 文件 | 主要内容 |
|------|------|---------|
| **通用** | `general/SKILL.md` | 建模、材料、边界条件、网格、分析步、作业提交 |
| **静力** | `static/SKILL.md` | 线弹性，非线性（塑性、接触）|
| **疲劳** | `fatigue/SKILL.md` | 高周疲劳S-N曲线，平均应力修正 |
| **热分析** | `thermal/SKILL.md` | 稳态/瞬态热传导，热-力耦合 |
| **XFEM** | `xfem/SKILL.md` | 裂纹萌生、扩展、损伤演化 |
| **复合材料** | `composite/SKILL.md` | 层合板铺层，Hashin失效，渐进损伤 |

### 快速上手

```
用户描述需求 → AI确认关键信息 → 从模板生成脚本
```

**AI助手**：参见 [`prompts/ai_guide.md`](prompts/ai_guide.md) 获取生成流程。

### 许可证

MIT License — 详见 [LICENSE](../LICENSE)。
