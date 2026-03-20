# Abaqus子程序技能库

[English](../README.md) | [中文](#中文)

---

## 概述

这是一个全面的Abaqus用户子程序开发技能库。它提供AI辅助编程指导，包含标准化的Fortran代码模板、详细的理论说明和完整的工程示例。

## 功能特点

- **多种子程序类型**：UMAT、VUMAT、DLOAD、VDLOAD、DISP、VDISP、USDFLD、SIGINI、SDVINI、FRIC、VRIC、HETVAL、FILM、UEL、VUEL
- **完整模板**：可直接使用的Fortran代码，适用于各种工程应用
- **理论背景**：数学公式和物理模型
- **最佳实践**：编码规范、调试技巧和性能优化
- **故障排除指南**：常见错误和解决方案

## 目录结构

```
abaqus_subroutine_skills/
├── SKILL.md              # 主技能文件（Claude Code格式）
├── manual.md             # 英文手册
├── manual_zh.md         # 中文手册
├── README.md            # 英文自述文件
├── README_zh.md         # 本文件
├── reference/           # 参考文档
│   ├── material/        # 材料子程序
│   │   ├── umat_elastic.md      # 线弹性UMAT
│   │   ├── umat_plasticity.md   # 弹塑性UMAT
│   │   └── vumat_elastic.md     # 线弹性VUMAT
│   ├── load/            # 载荷子程序
│   │   └── dload_moving.md      # 移动载荷
│   ├── boundary/        # 边界子程序
│   │   └── disp_control.md      # 自定义位移
│   ├── field/           # 场变量子程序
│   │   └── usdfld_spatial.md    # 空间场变量
│   ├── initial/         # 初始条件子程序
│   │   └── sigini_stress.md     # 初始应力
│   ├── thermal/         # 热分析子程序
│   │   └── hetval_heat.md       # 热生成
│   ├── friction/        # 摩擦子程序
│   │   └── fric_contact.md       # 自定义摩擦
│   └── element/         # 自定义单元子程序
│       └── uel_spring.md         # 非线性弹簧
└── official_examples/   # Abaqus官方示例
    ├── disp/
    ├── dload/
    ├── film/
    ├── fric/
    ├── hetval/
    ├── sdvini/
    ├── sigini/
    ├── uel/
    ├── umat/
    ├── usdfld/
    ├── vdisp/
    ├── vdload/
    ├── vric/
    ├── vuel/
    └── vumat/
```

## 快速开始

1. **阅读SKILL.md** 了解整体功能和能力
2. **选择参考文件** 根据您的需求（参见manual.md手册获取指导）
3. **复制并修改** 代码模板以适应您的具体问题
4. **编译测试** 按照参考文件中的说明进行

## 需求

- Abaqus 2020或更高版本
- Intel Fortran 19.0+ 或 GNU Fortran 9.0+
- Fortran编程基础知识
- 熟悉Abaqus有限元软件

## 版本信息

- 当前版本：1.0
- 最后更新：2026-03-20

## 许可证

本技能库仅供教育和研究目的使用。
