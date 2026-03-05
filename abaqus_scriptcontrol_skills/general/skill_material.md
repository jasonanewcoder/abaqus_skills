# 技能：材料定义 (Material Definition)

## 📖 功能描述

定义材料属性并创建截面属性，将材料分配给几何部件。

## 🔧 API 参考

### 核心类和方法

```python
# 创建材料
material = model.Material(name='Steel')

# 定义弹性属性
material.Elastic(table=((210000.0, 0.3),))  # E, nu

# 定义密度
material.Density(table=((7.8e-09,),))  # tonne/mm^3

# 定义塑性
material.Plastic(table=((250.0, 0.0), (350.0, 0.1), (400.0, 0.2)))

# 创建截面
section = model.HomogeneousSolidSection(name='Section-1', material='Steel', thickness=None)

# 分配截面
part.SectionAssignment(region=(part.cells,), sectionName='Section-1')
```

## 💻 代码模板

### 模板 1：各向同性线弹性材料

```python
# ========== 材料参数 ==========
E = 210000.0      # MPa, 弹性模量
nu = 0.3          # 泊松比
rho = 7.8e-09     # tonne/mm^3, 密度

# ========== 创建材料 ==========
model = mdb.models['Model-1']

# 创建材料
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 创建截面
section = model.HomogeneousSolidSection(
    name='SteelSection',
    material='Steel',
    thickness=None
)

# 分配给部件
part = model.parts['Part-1']
region = (part.cells,)
part.SectionAssignment(
    region=region,
    sectionName='SteelSection',
    offset=0.0,
    offsetType=MIDDLE_SURFACE,
    offsetField='',
    thicknessAssignment=FROM_SECTION
)
```

### 模板 2：理想弹塑性材料

```python
# ========== 材料参数 ==========
E = 210000.0      # MPa
nu = 0.3
rho = 7.8e-09     # tonne/mm^3
yield_stress = 250.0  # MPa

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='Steel_EPP')

# 弹性
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 塑性（理想弹塑性）
plastic_data = (
    (yield_stress, 0.0),    # 屈服点
    (yield_stress, 0.5),    # 平台段
)
material.Plastic(table=plastic_data)

# 创建和分配截面
section = model.HomogeneousSolidSection(name='EPPSection', material='Steel_EPP')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='EPPSection')
```

### 模板 3：双线性随动强化材料

```python
# ========== 材料参数 ==========
E = 210000.0      # MPa
nu = 0.3
rho = 7.8e-09
yield_stress = 350.0   # MPa
tangent_modulus = 2000.0  # MPa, 切线模量

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='Steel_Bilinear')

material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 双线性塑性
epsilon_yield = yield_stress / E
epsilon_max = 0.2  # 最大塑性应变
stress_max = yield_stress + tangent_modulus * (epsilon_max - epsilon_yield)

plastic_data = (
    (yield_stress, epsilon_yield),
    (stress_max, epsilon_max),
)
material.Plastic(table=plastic_data)

section = model.HomogeneousSolidSection(name='BilinearSection', material='Steel_Bilinear')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='BilinearSection')
```

### 模板 4：铝合金

```python
# ========== 铝合金 6061-T6 参数 ==========
E = 69000.0       # MPa
nu = 0.33
rho = 2.7e-09     # tonne/mm^3
yield_stress = 276.0  # MPa
ultimate_stress = 310.0  # MPa

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='Al6061-T6')

material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# 塑性数据（简化）
plastic_data = (
    (yield_stress, 0.0),
    (ultimate_stress, 0.15),
)
material.Plastic(table=plastic_data)

section = model.HomogeneousSolidSection(name='AlSection', material='Al6061-T6')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='AlSection')
```

### 模板 5：超弹性材料（橡胶）

```python
# ========== 超弹性材料参数（Mooney-Rivlin） ==========
C10 = 0.293  # MPa
C01 = 0.177  # MPa
D1 = 0.002   # MPa^-1 (可压缩性)

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='Rubber')

# Mooney-Rivlin 超弹性模型
material.Hyperelastic(
    materialType=ISOTROPIC,
    type=MOONEY_RIVLIN,
    volumetricResponse=VOLUMETRIC_DATA,
    table=((C10, C01, D1),)
)

# 或者使用试验数据
# material.Hyperelastic(
#     materialType=ISOTROPIC,
#     type=TEST_DATA,
#     uniaxialTests=((stress1, strain1), (stress2, strain2), ...),
#     biaxialTests=((...),),
#     planarTests=((...),)
# )

section = model.HomogeneousSolidSection(name='RubberSection', material='Rubber')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='RubberSection')
```

### 模板 6：正交各向异性材料

```python
# ========== 正交各向异性材料参数（例如木材） ==========
# 弹性常数
E1 = 12000.0   # MPa, 纵向
E2 = 800.0     # MPa, 横向
E3 = 500.0     # MPa, 径向
nu12 = 0.3
nu13 = 0.3
nu23 = 0.4
G12 = 600.0    # MPa
G13 = 400.0    # MPa
G23 = 100.0    # MPa

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='Wood_Orthotropic')

# 正交各向异性弹性
material.Elastic(
    type=ENGINEERING_CONSTANTS,
    table=((E1, E2, E3, nu12, nu13, nu23, G12, G13, G23),)
)

section = model.HomogeneousSolidSection(name='WoodSection', material='Wood_Orthotropic')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='WoodSection')
```

### 模板 7：壳体截面

```python
# ========== 壳体材料参数 ==========
E = 210000.0  # MPa
nu = 0.3
thickness = 5.0  # mm

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='ShellMaterial')
material.Elastic(table=((E, nu),))

# 创建壳体截面
shell_section = model.HomogeneousShellSection(
    name='ShellSection',
    preIntegrate=OFF,
    material='ShellMaterial',
    thicknessType=UNIFORM,
    thickness=thickness,
    thicknessField='',
    idealization=NO_IDEALIZATION,
    poissonDefinition=DEFAULT,
    thicknessModulus=None,
    temperature=GRADIENT,
    useDensity=OFF,
    integrationRule=SIMPSON,
    numIntPts=5
)

# 分配给壳体部件
part = model.parts['ShellPart']
region = (part.faces,)
part.SectionAssignment(region=region, sectionName='ShellSection')
```

### 模板 8：梁截面

```python
# ========== 梁材料参数 ==========
E = 210000.0  # MPa
nu = 0.3

# ========== 创建材料 ==========
model = mdb.models['Model-1']
material = model.Material(name='BeamMaterial')
material.Elastic(table=((E, nu),))

# 创建梁截面（矩形）
beam_section = model.RectangularProfile(name='RectProfile', a=50.0, b=30.0)

beam_section_assignment = model.BeamSection(
    name='BeamSection',
    profile='RectProfile',
    material='BeamMaterial',
    integration=BEFORE_ANALYSIS,
    poissonRatio=0.0,
    temperatureVar=LINEAR,
    consistentMassMatrix=False
)

# 分配给梁部件并定义方向
part = model.parts['BeamPart']
region = (part.edges,)
part.SectionAssignment(region=region, sectionName='BeamSection')

# 定义梁方向
edges = part.edges
region = regionToolset.Region(edges=edges)
part.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))
```

## 🌡️ 热相关材料属性

### 热传导材料

```python
# 创建热传导材料
material = model.Material(name='Steel_Thermal')

# 导热系数 (W/m·K → mW/mm·K, 在N-mm制中)
thermal_conductivity = 45.0  # W/m·K = 0.045 W/mm·K = 45 mW/mm·K
material.Conductivity(table=((thermal_conductivity,),))

# 比热容 (J/kg·K → mJ/tonne·K)
specific_heat = 460.0  # J/kg·K
material.SpecificHeat(table=((specific_heat * 1e9,),))  # 单位转换

# 热膨胀系数
expansion_coeff = 1.2e-05  # /°C
material.Expansion(table=((expansion_coeff,),))
```

### 温度相关材料属性

```python
# 温度相关的弹性模量
material.Elastic(
    temperatureDependency=ON,
    table=((210000.0, 0.3, 20.0),    # 20°C
           (200000.0, 0.3, 200.0),   # 200°C
           (180000.0, 0.3, 400.0),   # 400°C
           (150000.0, 0.3, 600.0))   # 600°C
)

# 温度相关的屈服强度
material.Plastic(
    temperatureDependency=ON,
    table=((250.0, 0.0, 20.0),
           (200.0, 0.0, 200.0),
           (150.0, 0.0, 400.0))
)
```

## 🎯 常用材料属性库

```python
# 预定义常用材料属性
MATERIAL_LIBRARY = {
    'Steel_Q235': {
        'E': 210000.0,
        'nu': 0.3,
        'rho': 7.85e-09,
        'yield': 235.0,
        'ultimate': 375.0
    },
    'Steel_Q345': {
        'E': 210000.0,
        'nu': 0.3,
        'rho': 7.85e-09,
        'yield': 345.0,
        'ultimate': 470.0
    },
    'Aluminum_6061': {
        'E': 69000.0,
        'nu': 0.33,
        'rho': 2.70e-09,
        'yield': 276.0,
        'ultimate': 310.0
    },
    'Aluminum_7075': {
        'E': 72000.0,
        'nu': 0.33,
        'rho': 2.81e-09,
        'yield': 503.0,
        'ultimate': 572.0
    },
    'Titanium_Ti6Al4V': {
        'E': 113800.0,
        'nu': 0.342,
        'rho': 4.43e-09,
        'yield': 880.0,
        'ultimate': 950.0
    },
    'Concrete_C30': {
        'E': 30000.0,
        'nu': 0.2,
        'rho': 2.50e-09,
        'compressive': 30.0,
        'tensile': 2.0
    }
}

# 使用示例
def create_material_from_library(model, material_name):
    """从材料库创建材料"""
    if material_name not in MATERIAL_LIBRARY:
        raise ValueError(f"未知材料: {material_name}")
    
    props = MATERIAL_LIBRARY[material_name]
    material = model.Material(name=material_name)
    material.Elastic(table=((props['E'], props['nu']),))
    material.Density(table=((props['rho'],),))
    
    if 'yield' in props:
        material.Plastic(table=((props['yield'], 0.0),))
    
    return material
```

## 💡 最佳实践

1. **单位一致性**：确保材料属性单位与模型单位一致
   - N-mm-MPa 制：密度用 tonne/mm³，应力用 MPa
   - N-m-Pa 制：密度用 kg/m³，应力用 Pa

2. **材料命名**：使用有意义的名称，如 `'Steel_Q235'` 而非 `'Material-1'`

3. **温度依赖**：高温分析必须定义温度相关材料属性

4. **检查分配**：确保每个部件都已正确分配截面

5. **密度检查**：动力学分析、重力载荷需要密度数据

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 材料未分配 | 创建了材料但未分配给部件 | 检查 SectionAssignment |
| 单位错误 | 密度单位不正确 | 确认 tonne/mm³ = kg/m³ × 10⁻¹² |
| 截面类型不匹配 | 实体部件分配壳截面 | 检查截面类型与部件维度 |
| 缺少塑性数据 | 非线性分析未定义塑性 | 添加 Plastic 属性 |
