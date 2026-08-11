# Tsai-Wu Failure & Continuum Shell Layups — Detailed Reference

## Skill Description

Two advanced composite topics in one reference:
1. **Tsai-Wu interactive failure criterion** — a general quadratic failure surface
   (better interaction coverage than Hashin, no mode distinction)
2. **Continuum shell layups** (`SC8R`/`S4` with `*Composite Shell Section`) — full
   3D stress state through thickness with ply definition, unlike conventional S4R

> 中文提示：Tsai-Wu 是工程上最常用的「交互式」失效准则（用 F_ij 系数矩阵）；
> 连续壳单元(SC8R)带真实厚度几何，铺层应力比 S4R 更准，适合厚层合板。

## Tsai-Wu Criterion

```
F_i·σ_i + F_ij·σ_i·σ_j = 1   (failure when LHS ≥ 1)
```

For plane stress (1,2 plane) with only F11, F22, F66, F12:

```
F11·σ11² + F22·σ22² + F66·τ12² + 2·F12·σ11·σ22 + F1·σ11 + F2·σ22 = 1
```

Coefficients from strength data:

```
F1 = 1/X_T − 1/X_C        F2 = 1/Y_T − 1/Y_C
F11 = 1/(X_T·X_C)          F22 = 1/(Y_T·Y_C)
F66 = 1/S²                 F12 = −0.5·√(F11·F22)   (typical choice)
```

| Symbol | Meaning |
|--------|---------|
| X_T, X_C | Longitudinal tensile / compressive strength |
| Y_T, Y_C | Transverse tensile / compressive strength |
| S | In-plane shear strength |

**In Abaqus**: Tsai-Wu is not a built-in UDMGINI in older versions; implement via
`*User Defined Field` (USDFLD) + damage, or post-process stress with the formula.
The built-in `Maxpe`/`Maxs` etc. cover stress/strain limits; for interactive criteria
use post-processing or `*Damage Initiation, criterion=USER` with a UDMGINI/UMAT.

## Python Template: Continuum Shell with Per-Ply Output

```python
from abaqus import *
from abaqusConstants import *
from caeModules import *

# ========== 1. Material (orthotropic lamina, MPa) ==========
model = mdb.Model(name='CSHELL-Plate')
material = model.Material(name='T300-5208')
material.Elastic(
    type=LAMINA,
    table=((135000.0, 10000.0, 0.3, 5000.0, 5000.0, 5000.0),)  # E1 E2 nu12 G12 G13 G23
)
material.Density(table=((1.6e-9,),))
# Strength data for Tsai-Wu post-processing
XT, XC, YT, YC, S = 1500.0, 1500.0, 40.0, 246.0, 68.0  # MPa

# ========== 2. Geometry ==========
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=400.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(300.0, 100.0))
part = model.Part(name='Plate', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=2.0)   # total thickness = 2 mm
del model.sketches['__profile__']

# ========== 3. Composite shell section (continuum shell) ==========
# SC8R elements need a composite shell section with through-thickness plies
part.CompositeShellSection(
    name='Layup-CS',
    preIntegrate=OFF,
    poissonDefinition=DEFAULT,
    useDensity=OFF,
    integrationRule=SIMPSON,
    numIntPts=3,
    thicknessType=UNIFORM,
    thickness=2.0
)

# Add plies: (angle, thickness)
plies = [(0, 0.5), (45, 0.5), (-45, 0.5), (90, 0.5)]
cs_section = part.sections['Layup-CS']
for i, (angle, thick) in enumerate(plies):
    cs_section.CompositePly(
        plyName=f'Ply-{i+1}',
        material='T300-5208',
        thicknessType=SPECIFY_THICKNESS,
        thickness=thick,
        orientationType=SPECIFY_ORIENT,
        orientationValue=angle,
        numIntPts=3
    )
part.SectionAssignment(region=(part.cells,), sectionName='Layup-CS')

# ========== 4. Assembly / Step / BC / Load ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='Plate-1', part=part, dependent=ON)
model.StaticStep(name='Load', previous='Initial', nlgeom=OFF,
                 initialInc=1.0, maxInc=1.0, maxNumInc=1)

# tension load
loaded_face = instance.faces.findAt(((300.0, 50.0, 1.0),))
model.Pressure(name='P', createStepName='Load',
               region=assembly.Surface(name='LoadSurf', side1Faces=loaded_face),
               magnitude=50.0)   # MPa

# ========== 5. Mesh: continuum shell ==========
part.setMeshControls(regions=(part.cells,), elemShape=HEX, technique=SWEEP)
elem_type = mesh.ElemType(elemCode=SC8R, elemLibrary=STANDARD)
part.setElementType(regions=(part.cells,), elemTypes=(elem_type,))
part.seedPart(size=10.0)
part.generateMesh()

# ========== 6. Output: ply stresses at section points ==========
model.FieldOutputRequest(
    name='F-Out', createStepName='Load',
    variables=('S', 'E', 'U', 'RF'), frequency=1
)
```

## Post-Processing: Tsai-Wu Index per Ply

```python
from odbAccess import openOdb

odb = openOdb(path='Job-1.odb', readOnly=True)
frame = odb.steps['Load'].frames[-1]
s_field = frame.fieldOutputs['S']

XT, XC, YT, YC, S = 1500.0, 1500.0, 40.0, 246.0, 68.0
F1, F2  = 1.0/XT - 1.0/XC, 1.0/YT - 1.0/YC
F11, F22, F66 = 1.0/(XT*XC), 1.0/(YT*YC), 1.0/(S*S)
F12 = -0.5 * (F11*F22) ** 0.5

worst = 0.0
for v in s_field.values:
    s11, s22, s33 = v.data[0], v.data[1], v.data[2]
    s12 = v.data[3]
    # plane-stress Tsai-Wu in the ply coordinate system:
    # NOTE: for rotated plies, transform s11/s22/s12 into the ply axes
    index = (F11*s11**2 + F22*s22**2 + F66*s12**2
             + 2.0*F12*s11*s22 + F1*s11 + F2*s22)
    if index > worst:
        worst = index
        hot = (v.elementLabel, v.integrationPoint, v.sectionPoint)
print(f'Max Tsai-Wu index: {worst:.3f} at {hot} (≥1.0 = failure)')
```

> For rotated plies you must transform stresses into each ply's local axes using
> the ply angle — the S tensor in the ODB is in the *material orientation* (ply)
> system only if an orientation was assigned; otherwise transform manually.

## Continuum Shell vs Conventional Shell

| Feature | S4R (conventional) | SC8R (continuum) |
|---------|--------------------|------------------|
| Geometry | Mid-surface + section offset | Full 3D geometry |
| Through-thickness stress | Smear from section points | Direct (3D constitutive) |
| Edge contact / free edges | Approximate | Accurate |
| Ply output | Section points (S11..S12) | Section points too, plus σ33 |
| Cost | Low | Higher |

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| `CompositePly` not found on section | It is a method of the section object, not the part: `part.sections['Layup-CS'].CompositePly(...)` |
| SC8R orientation flips | Define a datum/CSYS orientation for the section (`orientation` param) |
| Tsai-Wu index > 1 everywhere | Stresses in wrong axes — verify ply transformation |
| `F12` must satisfy stability: F12² < F11·F22 | Use the recommended −0.5√(F11·F22) |
| Section points not printed | Request section point output (`sectionPoints=DEFAULT`) |

## Related

- `layup_definition.md` — classical laminate theory + programmatic plies (S4R)
- `failure_analysis.md` — Hashin/Puck/LaRC progressive damage
- `postprocess_odb.md` — extracting per-ply stresses
