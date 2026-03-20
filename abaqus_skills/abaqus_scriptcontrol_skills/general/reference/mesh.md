# Mesh Generation Detailed Reference

## Overview

This reference document provides complete API reference and code templates for Abaqus mesh generation.

## Core API

```python
# Set seeds
part.seedPart(size=10.0, deviationFactor=0.1, minSizeFactor=0.1)

# Edge seeding
part.seedEdgeBySize(edges=edges, size=5.0)

# Set mesh controls
part.setMeshControls(regions=cells, elemShape=HEX, technique=STRUCTURED)

# Set element type
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))

# Generate mesh
part.generateMesh()
```

## Code Templates

### Template 1: Automatic Mesh

```python
element_size = 10.0
deviation_factor = 0.1
min_size_factor = 0.1

part = model.parts['Part-1']

# Set seeds
part.seedPart(
    size=element_size,
    deviationFactor=deviation_factor,
    minSizeFactor=min_size_factor,
    constraint=FINER
)

# Generate mesh
part.generateMesh()

print(f"Number of elements: {len(part.elements)}")
print(f"Number of nodes: {len(part.nodes)}")
```

### Template 2: Structured Mesh (Hexahedral)

```python
part = model.parts['Part-1']

# Set mesh controls
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED,
    algorithm=MEDIAL_AXIS
)

# Set seeds
part.seedPart(size=5.0, deviationFactor=0.1)

# Set element type
elem_type = mesh.ElemType(
    elemCode=C3D8R,
    elemLibrary=STANDARD,
    kinematicSplit=AVERAGE_STRAIN,
    secondOrderAccuracy=OFF,
    hourglassControl=DEFAULT,
    distortionControl=DEFAULT
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

# Generate mesh
part.generateMesh()
```

### Template 3: Sweep Mesh

```python
part = model.parts['Part-1']
cells = part.cells

# Set sweep mesh controls
part.setMeshControls(
    regions=cells,
    elemShape=HEX,
    technique=SWEEP,
    algorithm=MEDIAL_AXIS
)

# Set seeds
part.seedPart(size=5.0)

# Set element type
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))

part.generateMesh()
```

### Template 4: Free Mesh (Tetrahedral)

```python
part = model.parts['Part-1']
all_cells = part.cells

# Set mesh controls
part.setMeshControls(
    regions=all_cells,
    elemShape=TET,
    technique=FREE,
    algorithm=ADVANCING_FRONT
)

# Set seeds
part.seedPart(size=3.0, deviationFactor=0.1)

# Set element type
elem_type = mesh.ElemType(
    elemCode=C3D10,
    elemLibrary=STANDARD,
    secondOrderAccuracy=ON
)
part.setElementType(regions=(all_cells,), elemTypes=(elem_type,))

part.generateMesh()
```

### Template 5: Shell Mesh

```python
part = model.parts['Shell-Part']
all_faces = part.faces

# Set mesh controls
part.setMeshControls(
    regions=all_faces,
    elemShape=QUAD,
    technique=FREE,
    algorithm=MEDIAL_AXIS
)

# Edge seeding
edges = part.edges
part.seedEdgeBySize(edges=edges, size=5.0)

# Set shell element type
elem_type = mesh.ElemType(
    elemCode=S4R,
    elemLibrary=STANDARD,
    hourglassControl=DEFAULT
)
part.setElementType(regions=(all_faces,), elemTypes=(elem_type,))

part.generateMesh()
```

### Template 6: Beam Element Mesh

```python
part = model.parts['Beam-Part']
all_edges = part.edges

# Edge seeding
part.seedEdgeByNumber(edges=all_edges, number=10)

# Set beam element type
elem_type = mesh.ElemType(
    elemCode=B31,
    elemLibrary=STANDARD
)
part.setElementType(regions=(all_edges,), elemTypes=(elem_type,))

part.generateMesh()
```

### Template 7: Local Refinement

```python
part = model.parts['Part-1']

# Global seeds
part.seedPart(size=10.0)

# Local refinement - via edge seeding
refine_edges = part.edges.findAt(
    ((50.0, 0.0, 10.0),),
    ((50.0, 50.0, 10.0),)
)

part.seedEdgeBySize(
    edges=refine_edges,
    size=2.0,
    deviationFactor=0.1,
    minSizeFactor=0.1,
    constraint=FINER
)

# Set element type and generate mesh
cells = part.cells
elem_type = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
part.setElementType(regions=(cells,), elemTypes=(elem_type,))
part.generateMesh()
```

### Template 8: Mesh After Partitioning

```python
part = model.parts['Part-1']
cells = part.cells
partition_face = part.faces[0]
partition_edge = part.edges[0]

# Partition via sketch
sketch = model.ConstrainedSketch(name='__partition__', sheetSize=200.0)
sketch.Line(point1=(0.0, 0.0), point2=(100.0, 0.0))

part.PartitionCellBySketch(
    sketch=sketch,
    cells=cells,
    sketchPlane=partition_face,
    sketchUpEdge=partition_edge
)

# Set mesh on partitioned region
all_cells = part.cells
part.setMeshControls(
    regions=all_cells,
    elemShape=HEX,
    technique=STRUCTURED
)

part.seedPart(size=5.0)
part.generateMesh()
```

## Element Type Quick Reference

### Solid Elements (3D)

| Element Code | Description | Applicable Scenario |
|-------------|-------------|---------------------|
| C3D8R | Hexahedral linear reduced integration | General, computationally efficient |
| C3D8 | Hexahedral linear fully integrated | Avoid hourglass, bending problems |
| C3D8I | Hexahedral incompatible mode | Bending problems, coarse mesh |
| C3D20R | Hexahedral second-order reduced integration | High precision, stress concentration |
| C3D20 | Hexahedral second-order fully integrated | Highest precision |
| C3D4 | Tetrahedral linear | Complex geometry, free mesh |
| C3D10 | Tetrahedral second-order | Complex geometry, high precision |
| C3D6 | Triangular prism linear | Transition mesh |
| C3D15 | Triangular prism second-order | Transition mesh, high precision |

### Shell Elements (2D)

| Element Code | Description | Applicable Scenario |
|-------------|-------------|---------------------|
| S4R | Quadrilateral linear reduced integration | General shell analysis |
| S4 | Quadrilateral linear fully integrated | Thick shell, avoid hourglass |
| S8R | Quadrilateral second-order reduced integration | High precision shell analysis |
| S3R | Triangle linear | Complex geometry transition |
| S3 | Triangle linear fully integrated | Small strain |

### Beam Elements (1D)

| Element Code | Description | Applicable Scenario |
|-------------|-------------|---------------------|
| B31 | Linear beam | General beam analysis |
| B32 | Second-order beam | High precision, distributed loads |
| B31H | Linear beam (hybrid) | Inextensional bending |
| B32H | Second-order beam (hybrid) | Inextensional bending |
| B33 | Cubic beam | Slender beams |

## Advanced Mesh Control

### Mesh Quality Check

```python
# Get mesh statistics
mesh_stats = part.getMeshStats()

# Check element quality
elem_quality = part.quality

# Check unmeshed regions
unmeshed_regions = part.getUnmeshedRegions()
```

### Delete Mesh

```python
# Delete entire mesh
part.deleteMesh()

# Delete mesh on specific region
part.deleteMesh(regions=cells)
```

### Mesh Transition (Bias)

```python
edge = part.edges[0]

# Single bias
part.seedEdgeByBias(
    biasMethod=SINGLE,
    end1Edges=(edge,),
    ratio=3.0,
    number=20
)

# Double bias
part.seedEdgeByBias(
    biasMethod=DOUBLE,
    end1Edges=(edge,),
    end2Edges=(edge2,),
    minSize=1.0,
    maxSize=5.0,
    number=15
)
```

## Best Practices

1. **Element Selection Principle**:
   - Prefer hexahedral elements (C3D8R)
   - Use second-order tetrahedra (C3D10) for complex geometry
   - Avoid linear tetrahedra (C3D4)

2. **Mesh Density**:
   - Local refinement in areas of interest
   - At least 3-4 element layers through thickness
   - Avoid excessive aspect ratio

3. **Hourglass Control**:
   - Check hourglass energy for reduced integration elements
   - Hourglass energy should be less than 5% of internal energy

4. **Convergence Check**:
   - Coarse mesh → Fine mesh comparison
   - Check result sensitivity to mesh
