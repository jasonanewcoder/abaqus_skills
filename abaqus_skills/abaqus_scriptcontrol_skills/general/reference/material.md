# Material Definition Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus material property definition.

## Core API

### Creating Materials

```python
# Create material
material = model.Material(name='Steel')

# Define elastic properties
material.Elastic(table=((210000.0, 0.3),))  # (E, nu)

# Define density
material.Density(table=((7.85e-09),))  # tonne/mm³

# Define plasticity
material.Plastic(table=((250.0, 0.0), (350.0, 0.1), (400.0, 0.2)))

# Create section
section = model.HomogeneousSolidSection(
    name='Section-1',
    material='Steel',
    thickness=None  # Solid section = None
)

# Assign section
part.SectionAssignment(
    region=(part.cells,),
    sectionName='Section-1',
    offset=0.0,
    offsetType=MIDDLE_SURFACE,
    thicknessAssignment=FROM_SECTION
)
```

## Code Templates

### Template 1: Isotropic Linear Elastic Material

```python
# Parameters
E = 210000.0      # MPa
nu = 0.3
rho = 7.85e-09     # tonne/mm³

# Create
model = mdb.models['Model-1']
material = model.Material(name='Steel')
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# Create section
section = model.HomogeneousSolidSection(
    name='SteelSection',
    material='Steel',
    thickness=None
)

# Assign to part
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

### Template 2: Ideal Elastic-Plastic Material

```python
E = 210000.0      # MPa
nu = 0.3
rho = 7.85e-09
yield_stress = 250.0  # MPa

model = mdb.models['Model-1']
material = model.Material(name='Steel_EPP')

# Elastic
material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# Plastic (ideal elastic-plastic)
plastic_data = (
    (yield_stress, 0.0),    # Yield point
    (yield_stress, 0.5),    # Plateau segment
)
material.Plastic(table=plastic_data)

# Section
section = model.HomogeneousSolidSection(name='EPPSection', material='Steel_EPP')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='EPPSection')
```

### Template 3: Bilinear Kinematic Hardening Material

```python
E = 210000.0
nu = 0.3
rho = 7.85e-09
yield_stress = 350.0
tangent_modulus = 2000.0  # MPa

model = mdb.models['Model-1']
material = model.Material(name='Steel_Bilinear')

material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# Bilinear plasticity
epsilon_yield = yield_stress / E
epsilon_max = 0.2
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

### Template 4: Aluminum Alloy

```python
E = 69000.0       # MPa
nu = 0.33
rho = 2.7e-09     # tonne/mm³
yield_stress = 276.0  # MPa
ultimate_stress = 310.0  # MPa

model = mdb.models['Model-1']
material = model.Material(name='Al6061-T6')

material.Elastic(table=((E, nu),))
material.Density(table=((rho),))

# Plastic data
plastic_data = (
    (yield_stress, 0.0),
    (ultimate_stress, 0.15),
)
material.Plastic(table=plastic_data)

section = model.HomogeneousSolidSection(name='AlSection', material='Al6061-T6')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='AlSection')
```

### Template 5: Hyperelastic Material (Rubber)

```python
# Mooney-Rivlin parameters
C10 = 0.293  # MPa
C01 = 0.177  # MPa
D1 = 0.002   # MPa^-1

model = mdb.models['Model-1']
material = model.Material(name='Rubber')

# Mooney-Rivlin hyperelastic model
material.Hyperelastic(
    materialType=ISOTROPIC,
    type=MOONEY_RIVLIN,
    volumetricResponse=VOLUMETRIC_DATA,
    table=((C10, C01, D1),)
)

# Or use test data
# material.Hyperelastic(
#     materialType=ISOTROPIC,
#     type=TEST_DATA,
#     uniaxialTests=((stress1, strain1), ...),
#     biaxialTests=((...),),
#     planarTests=((...),)
# )

section = model.HomogeneousSolidSection(name='RubberSection', material='Rubber')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='RubberSection')
```

### Template 6: Orthotropic Material

```python
# Elastic constants (e.g., wood)
E1 = 12000.0   # MPa, longitudinal
E2 = 800.0     # MPa, transverse
E3 = 500.0     # MPa, radial
nu12 = 0.3
nu13 = 0.3
nu23 = 0.4
G12 = 600.0    # MPa
G13 = 400.0    # MPa
G23 = 100.0    # MPa

model = mdb.models['Model-1']
material = model.Material(name='Wood_Orthotropic')

# Orthotropic elasticity
material.Elastic(
    type=ENGINEERING_CONSTANTS,
    table=((E1, E2, E3, nu12, nu13, nu23, G12, G13, G23),)
)

section = model.HomogeneousSolidSection(name='WoodSection', material='Wood_Orthotropic')
part = model.parts['Part-1']
part.SectionAssignment(region=(part.cells,), sectionName='WoodSection')
```

### Template 7: Shell Section

```python
E = 210000.0  # MPa
nu = 0.3
thickness = 5.0  # mm

model = mdb.models['Model-1']
material = model.Material(name='ShellMaterial')
material.Elastic(table=((E, nu),))

# Create shell section
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

# Assign to shell part
part = model.parts['ShellPart']
region = (part.faces,)
part.SectionAssignment(region=region, sectionName='ShellSection')
```

### Template 8: Beam Section

```python
E = 210000.0  # MPa
nu = 0.3

model = mdb.models['Model-1']
material = model.Material(name='BeamMaterial')
material.Elastic(table=((E, nu),))

# Create beam section (rectangular)
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

# Assign to beam part and define orientation
part = model.parts['BeamPart']
region = (part.edges,)
part.SectionAssignment(region=region, sectionName='BeamSection')

# Define beam orientation
edges = part.edges
region = regionToolset.Region(edges=edges)
part.assignBeamSectionOrientation(
    region=region,
    method=N1_COSINES,
    n1=(0.0, 0.0, -1.0)
)
```

## Thermal Material Properties

### Heat Conduction Material

```python
# Create thermal material
material = model.Material(name='Steel_Thermal')

# Thermal conductivity
# W/(m·K) → mW/(mm·K) = value unchanged
thermal_conductivity = 45.0  # W/(m·K)
material.Conductivity(table=((thermal_conductivity),))

# Specific heat
# J/(kg·K) → mJ/(tonne·K) = value × 10^9
specific_heat = 460.0  # J/(kg·K)
material.SpecificHeat(table=((specific_heat * 1e9),))

# Thermal expansion coefficient
expansion_coeff = 1.2e-05  # /°C
material.Expansion(table=((expansion_coeff),))
```

### Temperature-Dependent Material Properties

```python
# Temperature-dependent elastic modulus
material.Elastic(
    temperatureDependency=ON,
    table=((210000.0, 0.3, 20.0),    # 20°C
           (200000.0, 0.3, 200.0),   # 200°C
           (180000.0, 0.3, 400.0),   # 400°C
           (150000.0, 0.3, 600.0))   # 600°C
)

# Temperature-dependent yield strength
material.Plastic(
    temperatureDependency=ON,
    table=((250.0, 0.0, 20.0),
           (200.0, 0.0, 200.0),
           (150.0, 0.0, 400.0))
)
```

## Common Material Library

```python
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

def create_material_from_library(model, material_name, part):
    """Create material from library"""
    if material_name not in MATERIAL_LIBRARY:
        raise ValueError(f"Unknown material: {material_name}")
    
    props = MATERIAL_LIBRARY[material_name]
    material = model.Material(name=material_name)
    material.Elastic(table=((props['E'], props['nu']),))
    material.Density(table=((props['rho']),),))
    
    if 'yield' in props:
        material.Plastic(table=((props['yield'], 0.0),))
    
    # Create section
    section = model.HomogeneousSolidSection(
        name=f'{material_name}Section',
        material=material_name
    )
    part.SectionAssignment(region=(part.cells,), sectionName=f'{material_name}Section')
    
    return material
```

## Elastic Types

```python
# Isotropic
material.Elastic(table=((E, nu),))

# Orthotropic (engineering constants)
material.Elastic(
    type=ENGINEERING_CONSTANTS,
    table=((E1, E2, E3, nu12, nu13, nu23, G12, G13, G23),)
)

# Orthotropic (lamina)
material.Elastic(
    type=LAMINA,
    table=((E1, E2, nu12, G12, G13, G23),)
)

# Anisotropic
material.Elastic(
    type=ANISOTROPIC,
    matrixType=SYMMETRIC,
    table=((D11, D12, D13, D14, D15, D16, ...),)
)

# Plane stress
material.Elastic(
    type=ISOTROPIC,
    planeStress=ON,
    table=((E, nu),)
)
```

## Best Practices

1. **Unit Consistency**: Ensure material property units match model units
   - N-mm-MPa system: density in tonne/mm³, stress in MPa
   - N-m-Pa system: density in kg/m³, stress in Pa

2. **Material Naming**: Use meaningful names, e.g., `'Steel_Q235'` instead of `'Material-1'`

3. **Temperature Dependency**: Must define temperature-dependent material properties for high-temperature analysis

4. **Check Assignment**: Ensure each part has correct section assignment

5. **Density Check**: Density required for dynamic analysis and gravity loads

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Material not assigned | Material created but not assigned to part | Check SectionAssignment |
| Unit error | Incorrect density unit | Confirm tonne/mm³ = kg/m³ × 10⁻¹² |
| Section type mismatch | Solid part assigned shell section | Check section type matches part dimensionality |
| Missing plastic data | Nonlinear analysis without plasticity | Add Plastic property |
