# Geometric Modeling Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus geometric modeling.

## Core API

### Creating Models and Parts

```python
# Create model
mdb.Model(name='Model-1')
model = mdb.models['Model-1']

# Create 3D solid part
part = model.Part(
    name='Part-1',
    dimensionality=THREE_D,  # THREE_D, TWO_D_PLANAR, AXISYMMETRIC
    type=DEFORMABLE_BODY     # DEFORMABLE_BODY, RIGID_BODY, ELEMENT_INSTANCE
)

# Create 2D planar part
part = model.Part(
    name='Part-2D',
    dimensionality=TWO_D_PLANAR,
    type=DEFORMABLE_BODY
)
```

### Creating 3D Solids from Sketches

```python
# Create sketch
sketch = model.ConstrainedSketch(
    name='__profile__',
    sheetSize=200.0  # Sketch workspace size
)

# Extrude to create solid
part.BaseSolidExtrude(
    sketch=sketch,
    depth=100.0  # Extrusion depth
)

# Revolve to create solid
part.BaseSolidRevolve(
    sketch=sketch,
    angle=360.0,
    flipRevolveDirection=OFF
)

# Create shell
part.BaseShellExtrude(
    sketch=sketch,
    depth=100.0
)

# Create 2D planar
part.BaseShell(sketch=sketch)

# Delete temporary sketch
del model.sketches['__profile__']
```

## Sketch Methods

### Basic Geometries

```python
sketch = model.ConstrainedSketch(name='sketch', sheetSize=200.0)

# Point
sketch.Point(point=(x, y))

# Line
sketch.Line(point1=(x1, y1), point2=(x2, y2))

# Rectangle
sketch.rectangle(point1=(x1, y1), point2=(x2, y2))

# Circle (center + point on circumference)
sketch.CircleByCenterPerimeter(center=(cx, cy), point1=(px, py))

# Circle (center + radius)
sketch.circle(centerPoint=(cx, cy), point1=(cx + r, cy))

# Arc (center + endpoints)
sketch.ArcByCenterEnds(
    center=(cx, cy),
    point1=(x1, y1),
    point2=(x2, y2),
    direction=CLOCKWISE  # CLOCKWISE, COUNTERCLOCKWISE
)

# Ellipse
sketch.EllipseByCenterPerimeter(
    center=(cx, cy),
    axisPoint1=(ax1, ay1),
    axisPoint2=(ax2, ay2)
)

# Polygon (circumscribed)
sketch.regularPolygonByCircumscribeCircle(
    centerPoint=(cx, cy),
    pointOnCircle=(px, py),
    numberOfSides=6
)

# Polygon (inscribed)
sketch.regularPolygonByInscribedCircle(
    centerPoint=(cx, cy),
    pointOnCircle=(px, py),
    numberOfSides=6
)
```

### Constraints

```python
# Fixed constraint
sketch.FixedConstraint(entity=vertex)

# Coincident constraint
sketch.CoincidentConstraint(entity1=vertex1, entity2=vertex2)

# Horizontal constraint
sketch.HorizontalConstraint(entity=line)

# Vertical constraint
sketch.VerticalConstraint(entity=line)

# Parallel constraint
sketch.ParallelConstraint(entity1=line1, entity2=line2)

# Perpendicular constraint
sketch.PerpendicularConstraint(entity1=line1, entity2=line2)

# Equal length constraint
sketch.EqualLengthConstraint(entity1=line1, entity2=line2)

# Radius constraint
sketch.RadiusConstraint(entity=curve, radius=value)

# Angular constraint
sketch.AngularConstraint(entity1=line1, entity2=line2, value=angle)
```

### Dimensions

```python
# Linear dimension
sketch.Dimension(
    entity=line,
    textPoint=(x, y),
    value=length
)

# Radial dimension
sketch.RadialDimension(
    curve=circle,
    textPoint=(x, y),
    radius=radius
)

# Angular dimension
sketch.AngularDimension(
    entity1=line1,
    entity2=line2,
    textPoint=(x, y),
    value=angle
)
```

## Code Templates

### Template 1: Block

```python
# Parameters
length = 100.0   # mm, X direction
width = 50.0     # mm, Y direction
height = 20.0    # mm, Z direction

# Create
model = mdb.models['Model-1']
part = model.Part(name='Block', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.rectangle(point1=(0.0, 0.0), point2=(length, width))

part.BaseSolidExtrude(sketch=sketch, depth=height)

del model.sketches['__profile__']
```

### Template 2: Cylinder

```python
radius = 25.0    # mm
height = 100.0   # mm

model = mdb.models['Model-1']
part = model.Part(name='Cylinder', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(radius, 0.0))

part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']
```

### Template 3: Hollow Cylinder

```python
outer_radius = 50.0   # mm
inner_radius = 45.0   # mm
height = 200.0        # mm

model = mdb.models['Model-1']
part = model.Part(name='Pipe', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# Outer circle
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(outer_radius, 0.0))
# Inner circle (hole)
sketch.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(inner_radius, 0.0))

part.BaseSolidExtrude(sketch=sketch, depth=height)
del model.sketches['__profile__']
```

### Template 4: Sphere

```python
radius = 50.0   # mm

model = mdb.models['Model-1']
part = model.Part(name='Sphere', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
# Half circle
sketch.ArcByCenterEnds(
    center=(0.0, 0.0),
    point1=(-radius, 0.0),
    point2=(radius, 0.0),
    direction=CLOCKWISE
)
# Close profile
sketch.Line(point1=(-radius, 0.0), point2=(radius, 0.0))

part.BaseSolidRevolve(sketch=sketch, angle=360.0)
del model.sketches['__profile__']
```

### Template 5: L-Bracket

```python
leg1_length = 100.0
leg1_width = 50.0
leg1_thickness = 10.0
leg2_length = 80.0
leg2_width = 50.0
leg2_thickness = 10.0

model = mdb.models['Model-1']
part = model.Part(name='L-Bracket', dimensionality=THREE_D, type=DEFORMABLE_BODY)

sketch = model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
sketch.Line(point1=(0.0, 0.0), point2=(leg1_length, 0.0))
sketch.Line(point1=(leg1_length, 0.0), point2=(leg1_length, leg1_width))
sketch.Line(point1=(leg1_length, leg1_width), point2=(leg2_thickness, leg1_width))
sketch.Line(point1=(leg2_thickness, leg1_width), point2=(leg2_thickness, leg1_width + leg2_length))
sketch.Line(point1=(leg2_thickness, leg1_width + leg2_length), point2=(0.0, leg1_width + leg2_length))
sketch.Line(point1=(0.0, leg1_width + leg2_length), point2=(0.0, 0.0))

part.BaseSolidExtrude(sketch=sketch, depth=leg1_thickness)
del model.sketches['__profile__']
```

## Geometry Selection

### Selecting Geometry Objects

```python
# Select all cells
cells = part.cells

# Select by index
cell = part.cells[0]

# Select by coordinate (cells containing point)
selected_cells = part.cells.findAt(((x, y, z),))

# Select faces
faces = part.faces
face = part.faces.findAt(((x, y, z),))

# Select edges
edges = part.edges
edge = part.edges.findAt(((x, y, z),))

# Select vertices
vertices = part.vertices
vertex = part.vertices.findAt(((x, y, z),))

# Bounding box selection
cells = part.cells.getByBoundingBox(xMin, xMax, yMin, yMax, zMin, zMax)
faces = part.faces.getByBoundingBox(...)
edges = part.edges.getByBoundingBox(...)

# Cylindrical bounding selection
cells = part.cells.getByBoundingCylinder(center1, center2, radius)
edges = part.edges.getByBoundingCylinder(...)
```

## Feature Operations

### Cutting

```python
# Extrude cut
part.CutExtrude(
    sketchPlane=face,
    sketchUpEdge=edge,
    sketchPlaneSide=SIDE1,
    sketchOrientation=RIGHT,
    sketch=sketch,
    depth=cut_depth,
    flipExtrudeDirection=OFF
)

# Revolve cut
part.CutRevolve(
    sketchPlane=face,
    sketchUpEdge=edge,
    sketchPlaneSide=SIDE1,
    sketchOrientation=RIGHT,
    sketch=sketch,
    angle=90.0
)

# Sweep cut
part.CutSweep(pathEdge=path_edge, sketch=sketch)
```

### Filleting and Chamfering

```python
# Fillet
edges_for_fillet = part.edges.findAt(
    ((x1, y1, z1),),
    ((x2, y2, z2),)
)
part.Round(radius=5.0, edgeList=edges_for_fillet)

# Chamfer
edges_for_chamfer = part.edges.findAt(((x, y, z),))
part.Chamfer(
    length=2.0,
    length2=2.0,
    edgeList=edges_for_chamfer
)
```

### Shelling

```python
# Shell (remove face)
face_to_remove = part.faces.findAt(((x, y, z),))
part.Shell(thickness=2.0, faceList=(face_to_remove,))

# Shell all faces
part.SolidExtrude(...)
part.Shell(thickness=2.0, faceList=part.faces)
```

### Mirroring

```python
# Create datum plane
datum_plane = part.DatumPlaneByPrincipalPlane(
    principalPlane=XYPLANE,
    offset=0.0
)

# Mirror feature
part.Mirror(
    mirrorPlane=datum_plane,
    featureList=(feature1, feature2)
)
```

### Patterning

```python
# Linear pattern
edge_for_direction = part.edges[0]
part.LinearPattern(
    featureList=(feature,),
    direction1=edge_for_direction,
    number1=3,
    spacing1=50.0
)

# Circular pattern
axis_for_rotation = part.datums[datum_axis_id]
part.CircularPattern(
    featureList=(feature,),
    axis=axis_for_rotation,
    number=6,
    totalAngle=360.0
)
```

## Best Practices

1. **Naming Conventions**: Use meaningful part names, e.g., `'Beam_100x50'`
2. **Unit Consistency**: Use consistent units for all dimensions (mm recommended)
3. **Sketch Cleanup**: Delete temporary sketches after creation `del model.sketches['__profile__']`
4. **Parametric Design**: Define dimensions as variables for easy modification
5. **Validate Geometry**: Check for free edges, short edges, etc. after creating complex models

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Sketch not closed | Contour lines not closed | Check if all line endpoints coincide |
| Self-intersection | Sketch lines cross | Modify sketch to avoid intersection |
| Zero thickness | Extrusion depth is 0 | Check depth parameter |
| Invalid selection | findAt coordinate not on target | Adjust coordinate or use index selection |
