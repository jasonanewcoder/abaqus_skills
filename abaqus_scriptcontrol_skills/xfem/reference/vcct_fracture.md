# VCCT Crack Growth — Detailed Reference

## Skill Description

VCCT (Virtual Crack Closure Technique) models **crack growth along predefined surfaces**
in Abaqus — unlike XFEM, the crack path must be meshed beforehand (a seam/interface),
but it handles interlaminar delamination, adhesive joints, and mixed-mode fracture
with accurate energy release rates without remeshing.

> 中文提示：VCCT 适合「裂纹沿预设面扩展」（分层、胶层脱粘）；XFEM 适合
> 「裂纹路径未知」的扩展。VCCT 输出 G_I/G_II/G_III 与 BEM (Benzeggagh-Kenane)
> 混合模式判据。

## When to Use VCCT vs XFEM

| Criterion | VCCT | XFEM |
|-----------|------|------|
| Crack path | Known in advance (surface/surface pair) | Unknown (initiation anywhere) |
| Interface (delamination/adhesive) | ✓ Best choice | Possible |
| Crack inside solid, path unknown | ✗ | ✓ Best choice |
| Output | Energy release rates G, BEM mixed mode | PHILSM/STATUSXFEM |
| Mesh requirement | Crack surface meshed with coincident nodes (or cohesive via contact) | None |

## Workflow (Abaqus)

1. Mesh the part so the crack plane has **coincident nodes** (duplicated nodes across
   the interface — the mesh is "unseamed")
2. Create the crack: `ContourIntegral` crack front + crack tip on the interface
3. Define damage evolution: `*Debond` / VCCT in the interaction property
   (`CrackPropagation` interaction) or via `ContourIntegral` with `allowGrowth=ON`
4. Apply mixed-mode criterion: B-K power law with G_Ic, G_IIc, G_IIIc, exponent η
5. Field output: `G11TURT`, `G22TURT`, `G33TURT` (energy release rates), `BEMTURT`

## Python Template: VCCT Interface Crack

```python
from abaqus import *
from abaqusConstants import *
from caeModules import *
import regionToolset

# ========== 1. Parameters ==========
length, width, height = 200.0, 50.0, 10.0    # mm — DCB-like specimen
crack_length = 50.0                          # mm initial crack
E1, E2, nu12, G12 = 135000.0, 10000.0, 0.3, 5000.0   # MPa (orthotropic lamina)
G_Ic, G_IIc, G_IIIc = 0.3, 0.8, 0.8          # N/mm fracture energies
BK_EXP = 1.5                                  # B-K exponent eta
P = 100.0                                     # N opening load

# ========== 2. Geometry with a crack plane ==========
model = mdb.Model(name='VCCT-Model')
sketch = model.ConstrainedSketch(name='__profile__', sheetSize=300.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))
part = model.Part(name='DCB', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']

# Partition at the crack plane (Z = crack plane): split into two halves
# so the interface has coincident nodes
datum = part.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=0.0)
part.PartitionCellByDatumPlane(datumPlane=datum, cells=part.cells)

# ========== 3. Material (orthotropic + damage) ==========
material = model.Material(name='Lamina')
material.Elastic(type=LAMINA, table=((E1, E2, nu12, G12, G12, G12),))
material.Density(table=((1.6e-9,),))

# ========== 4. Section on both halves ==========
section = model.HomogeneousSolidSection(name='Sec', material='Lamina')
part.SectionAssignment(region=(part.cells,), sectionName='Sec')

# ========== 5. Assembly ==========
assembly = model.rootAssembly
instance = assembly.Instance(name='DCB-1', part=part, dependent=ON)

# ========== 6. Step ==========
model.StaticStep(name='Open', previous='Initial', nlgeom=ON,
                 initialInc=0.01, minInc=1e-8, maxInc=0.05,
                 maxNumInc=10000)

# ========== 7. Crack definition (VCCT) ==========
# The crack front is the edge where the crack starts; the crack tip the
# interface ahead of it. In a 3D solid, define a node/edge-based crack:
# crack front = edge at x=crack_length on the interface
crack_front_edges = part.edges.findAt(((crack_length, width/2.0, 0.0),))
crack_tip_edges = part.edges.findAt(((crack_length, width/2.0, 0.0),))
front_region = regionToolset.Region(edges=crack_front_edges)
tip_region = regionToolset.Region(edges=crack_tip_edges)

model.ContourIntegral(
    name='Crack-1',
    crackFront=front_region,
    crackTip=tip_region,
    crackName='Crack-1',
    type=STRESS_INTENS_FACTORS,   # or J-INTEGRAL
    numContours=5,
    extensionDirectionMethod=Q_VECTORS,
    allowGrowth=ON                # ← enables VCCT growth
)

# ========== 8. Loads & BCs ==========
# Fix the bottom half at the loaded end; pull the top half
bottom_face = instance.faces.getByBoundingBox(0,0,-1, 1,width,1)
top_face = instance.faces.getByBoundingBox(0,0,height-1, 1,width,height)
model.DisplacementBC(name='Fix-Bottom', createStepName='Initial',
                     region=assembly.Set(name='FixB', faces=bottom_face),
                     u1=0.0, u2=0.0, u3=0.0)
model.DisplacementBC(name='Open-Top', createStepName='Open',
                     region=assembly.Set(name='OpenT', faces=top_face),
                     u3=5.0)      # opening displacement

# ========== 9. Field output with VCCT variables ==========
model.FieldOutputRequest(
    name='VCCT-Out', createStepName='Open',
    variables=('S', 'U', 'RF', 'G11TURT', 'G22TURT', 'G33TURT', 'BEMTURT'),
    frequency=1
)
```

> **Note on crack front selection**: in practice the crack front/tip regions must
> be **edge sets on the crack surface** (or node sets). `findAt` coordinates must
> lie exactly on the mesh edges — when meshing is done after, define the crack on
> the *mesh* geometry or use node-based cracks. Verify the exact selection in
> your Abaqus version (see `docs/ERRATA.md` section 2).

## Mixed-Mode Criterion

B-K law (Benzeggagh-Kenane):

```
G_c = G_Ic + (G_IIc − G_Ic)·( (G_II + G_III)/(G_I + G_II + G_III) )^η
```

Crack grows when total energy release rate reaches G_c.
Power law: `(G_I/G_Ic)^α + (G_II/G_IIc)^α + (G_III/G_IIIc)^α = 1`.

In the input file, the debond behavior is defined with:

```abaqus
*Debond, slave=..., master=..., time increment=0.01
*Fracture Criterion, type=BK
0.3, 0.8, 0.8, 1.5
** G_Ic, G_IIc, G_IIIc, eta
```

(Or in CAE via `Interaction → Contact property → Debond/VCCT`.)

## Result Interpretation

| Output | Meaning |
|--------|---------|
| G11TURT / G22TURT / G33TURT | Energy release rate in modes I / II / III |
| BEMTURT | B-K criterion value at crack tip |
| STATUS | 1 = intact, 0 = fully separated (elements) |
| RF | Reaction force → R-curve (load vs crack length) |

Checks:
- G should approach the critical G_c as the crack grows (steady-state)
- R-curve smoothness: mesh-size-dependent saw-tooth = refine mesh at crack tip
- Unstable growth: use displacement control, not force control

## Related

- `crack_initiation.md` — XFEM (unknown crack paths)
- `postprocess_odb.md` — extracting G/BEMTURT
- `verification.md` — DCB analytical G for validation: G = 12·P²·a²/(E·b²·h³)
