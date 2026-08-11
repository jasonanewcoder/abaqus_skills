# Interactions & Contact — Detailed Reference

## Overview

Defines contact and constraints between parts/instances in Abaqus: general contact,
contact pairs, tie constraints, couplings, and MPCs. Required for assemblies, bolted
joints, press-fit, impact, etc.

> 中文提示：接触分析 90% 的收敛问题来自「初始过盈/间隙设置」和「法向方向」。
> 通用接触(General Contact)是现代首选，接触对(Contact Pair)用于精细控制。

## When to Use What

| Feature | Use case |
|---------|----------|
| **General Contact** (Std & Exp) | Default choice — auto-detect all surfaces, self-contact OK |
| **Contact Pair** (Std) | Precise control of slave/master, multiple surfaces, cohesive zones |
| **Tie** | Permanent bonding without sliding (welds, glued parts) |
| **Coupling** | Rigid/cinematic connection of a region to a reference point (load application) |
| **MPC** | Custom constraint equations (Beam/rigid/Equation) |
| **Connector** | Joints with defined DOF behavior (pins, sliders, dashpots) |
| **Cohesive surface** | Bonded interfaces with damage (adhesive layers) |

## Template 1: General Contact (recommended default)

```python
# 1. Interaction property (friction + normal behavior)
model.ContactProperty(name='IntProp')
model.interactionProperties['IntProp'].TangentialBehavior(
    formulation=PENALTY,
    frictionCoeff=0.3          # Coulomb friction
)
model.interactionProperties['IntProp'].NormalBehavior(
    allowSeparation=ON,        # allow surfaces to separate
    constraintEnforcementMethod=DEFAULT
)

# 2. Create the general contact interaction
model.ContactStd(
    name='Gen-Contact',
    createStepName='Step-1',
    main=ALL_WITH_SIDE,        # all exposed element faces
    secondary=ALL_WITH_SIDE,
    interactionProperty='IntProp'
)
```

Explicit version: `model.ContactExp(...)` with the same arguments.

## Template 2: Contact Pair (surface-to-surface)

```python
# 1. Define the two surfaces (in the assembly)
slave_surf = assembly.Surface(
    name='Slave-Surf', side1Faces=instance.faces.getByBoundingBox(...))
master_surf = assembly.Surface(
    name='Master-Surf', side2Faces=other_instance.faces.getByBoundingBox(...))

# 2. Contact property (with smoothing for easier convergence)
model.ContactProperty(name='Fric-0.2')
model.interactionProperties['Fric-0.2'].TangentialBehavior(
    formulation=PENALTY, frictionCoeff=0.2)
model.interactionProperties['Fric-0.2'].NormalBehavior(allowSeparation=ON)

# 3. Contact pair interaction
model.SurfaceToSurfaceContactStd(
    name='Pair-1',
    createStepName='Step-1',
    master=master_surf,
    slave=slave_surf,
    sliding=FINITE,                # FINITE or SMALL
    interactionProperty='Fric-0.2'
)
```

**Choosing slave/master**: the slave is the finer-meshed / softer / smaller surface;
the master's face normals must point TOWARD the slave (check with `instance.flipNormals`).

## Template 3: Tie Constraint

```python
model.Tie(
    name='Tie-1',
    master=master_surf,            # coarser side
    slave=slave_surf,
    positionTolerance=0.05,        # 5% of characteristic length
    adjust=ON,                     # snap slave nodes onto master
    tieRotations=ON
)
```

## Template 4: Coupling (load application through a reference point)

```python
# Reference point + coupling = apply force/moment to a whole face
ref_point = assembly.ReferencePoint(point=(50.0, 25.0, 100.0))
rp = assembly.referencePoints[ref_point.id]

model.Coupling(
    name='Couple-1',
    controlPoint=rp,
    surface=assembly.Surface(name='Loaded-Surf', side1Faces=loaded_faces),
    influenceRadius=WHOLE_SURFACE,
    couplingType=KINEMATIC,        # rigid region; DISTRIBUTING also available
    u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON
)

# Then load the reference point
rp_set = assembly.Set(name='RP-Set', referencePoints=(rp,))
model.ConcentratedForce(name='F', createStepName='Step-1',
                        region=rp_set, cf2=-5000.0)
```

## Template 5: MPC — Equation constraint

```python
# Tie two nodes' DOFs with a linear equation: u1_nodeA + u1_nodeB = 0
model.Equation(
    name='Eq-1',
    terms=((1.0, 'Set-A', 1), (1.0, 'Set-B', 1)),
    createStepName='Step-1'
)
```

`terms` = list of `(coefficient, setName, dof)`; the equation sums to 0.

## Template 6: Cohesive Surfaces (bonded interface with damage)

```python
# Material with traction-separation behavior
mat = model.Material(name='Adhesive')
mat.Elastic(type=TRACTION,
            table=((Kn, Ks, Kt),))            # stiffness N/mm³
mat.MaxsDamageInitiation(
    table=((tn_max, ts_max, tt_max),),        # MPa
    definition=VALUE)
mat.maxsDamageInitiation.DamageEvolution(
    type=ENERGY, softening=LINEAR,
    table=((G_Ic,),))                          # N/mm

# Cohesive interaction property
model.ContactProperty(name='Cohesive-Prop')
model.interactionProperties['Cohesive-Prop'].CohesiveBehavior(
    table=((Kn, Ks, Kt),),
    tractionSeparationSlopes=UNCOUPLED,
    useTemperatureDependency=OFF)
model.interactionProperties['Cohesive-Prop'].Damage(
    initialStiffness=UNCOUPLED,
    table=((tn_max, ts_max, tt_max),),
    criteria=MAXS,                              # or QUADS
    evolutionType=ENERGY, mixedMode=G1G2G3,
    power=1.0, table=((G_Ic, G_IIc, G_IIIc),))

# Cohesive interaction between two surfaces
model.SurfaceToSurfaceContactStd(
    name='Cohesive-1', createStepName='Step-1',
    master=master_surf, slave=slave_surf,
    sliding=SMALL, interactionProperty='Cohesive-Prop')
```

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Contact doesn't engage | Check surface normals point toward the other body; flip if needed |
| Initial overclosure | Adjust geometry, or set `adjust=ON` / `interferenceFit` with small interference |
| Chattering | Increase contact damping (`ContactDamping`), reduce increment size |
| Contact pairs not found at interfaces | Ensure surfaces cover the full face (use `getByBoundingBox` correctly) |
| Tie with big gap | Increase `positionTolerance` or use `adjust=ON` |
| General contact missing a part | Assign the part's surfaces: `main=ALL_WITH_SIDE` catches most; add explicit surfaces if not |
| Rigid body motion until contact | Add a "pre-positioning" step or small initial load |

## Best Practices

1. **General contact first**; switch to pairs only when you need control
2. Slave = finer mesh; master normals toward slave
3. Use `PENALTY` (not augmented Lagrange) for tough convergence cases
4. Check contact status output: request `CSTRESS`, `CDISP` and `COPEN` in field output
5. For quasi-static contact use stabilization and reduce it to < 5% of internal energy
6. Verify contact force balance: total RF at supports ≈ total applied load

## Related

- `error_diagnosis.md` — contact convergence symptoms
- `postprocess_odb.md` — reading `CSTRESS`/`COPEN` from results
- `bc_load.md` — loads applied through coupling/MPC regions
