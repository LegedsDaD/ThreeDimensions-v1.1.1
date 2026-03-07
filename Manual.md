# ThreeDimensions Manual

**Version: 1.1.1**

This manual reflects the current implementation in `python/threedimensions` exactly.

## 1. Installation

```bash
pip install .
```

Optional viewer dependencies:

```bash
pip install glfw PyOpenGL
```

## 2. Top-Level API (`import threedimensions as td`)

### 2.1 Constants

- `td.__version__`
- `td.CORE_MODE` (`"C++"` or `"Python (Fallback)"`)

### 2.2 Types

- `td.Vector3`
- `td.TransformOptions`
- `td.Mesh`
- `td.BezierCurve`
- `td.NURBSCurve`
- `td.Scene`
- `td.NodeGraph`
- `td.ModifierStack`

### 2.3 Primitive Constructors

- `td.create_cube(size=1.0)`
- `td.create_sphere(radius=1.0, segments=32, rings=16)`
- `td.create_uv_sphere(radius=1.0, segments=32, rings=16)`
- `td.create_icosphere(radius=1.0, subdivisions=1)`
- `td.create_cylinder(radius=1.0, height=2.0, segments=16)`
- `td.create_cone(radius=1.0, height=2.0, segments=16)`
- `td.create_torus(main_radius=1.0, tube_radius=0.4, main_segments=32, tube_segments=16)`
- `td.create_plane(size=2.0, subdivisions=1)`
- `td.create_grid(size=2.0, x_subdivisions=10, y_subdivisions=10)`

### 2.4 Other Top-Level Functions

- `td.lathe(profile, steps=32)`
- `td.viewer(mesh=None, width=960, height=540, title="ThreeDimensions Viewer")`

## 3. Mesh Class Full Reference

All methods return `self` unless noted.

### 3.1 Core Mesh IO / Construction

- `add_vertex(position)`
- `add_face(indices)`
- `calculate_normals()`
- `clone()` -> new mesh
- `clear()`
- `save(filepath)` (`.obj` and `.stl` via backend)
- `merge_duplicate_vertices(tolerance=1e-6)`

Properties:

- `vertices`
- `faces`
- `vertex_count`
- `face_count`

### 3.2 Transform System

- `move(delta, options=None)`
- `translate(v)` or `translate(x, y, z)`
- `rotate(angle, axis="Z", options=None)`
- `rotate_x(angle)`, `rotate_y(angle)`, `rotate_z(angle)`
- `scale(s)` or `scale(x, y, z)` or `scale((x,y,z))`
- `mirror(axis="X")`
- `mirror_transform(axis="X")`

Cursor helpers:

- `Mesh.set_cursor(position)`
- `Mesh.cursor()`

`TransformOptions` fields:

- `mode` (`"OBJECT"|"VERTEX"|"EDGE"|"FACE"`)
- `pivot` (`"MEDIAN_POINT"|"CURSOR"`)
- `snap` (`None|"GRID"|"INCREMENT"|"VERTEX"`)
- `increment` (float)
- `proportional` (bool)
- `proportional_radius` (float)
- `falloff` (`"SMOOTH"|"SPHERE"|"ROOT"|"SHARP"|"LINEAR"`)

### 3.3 Selection System

- `select_mode(mode)`
- `select_vertex(index, extend=False)`
- `select_edge((v0, v1), extend=False)`
- `select_face(index, extend=False)`
- `select_loop((v0, v1))`
- `select_ring((v0, v1))`
- `box_select(min_corner, max_corner, mode=None)`
- `circle_select(center, radius, mode="VERTEX")`
- `lasso_select(points, mode="VERTEX")`
- `select_similar(by="face_size", value=None, tolerance=0.1)`

Selection sets available:

- `selected_vertices`
- `selected_edges`
- `selected_faces`

### 3.4 Mesh Editing Tools

- `extrude_face(face_index, distance=0.1)`
- `extrude(distance=0.1, face_indices=None)`
- `inset_faces(amount=0.05)`
- `bevel(width=0.05, segments=1)`
- `bridge_edge_loops(loop_a, loop_b)`
- `fill(vertices=None)`
- `grid_fill(boundary, rows=2, cols=2)`
- `subdivide(levels=1)`
- `loop_cut(cuts=1)`
- `knife(start, end)`
- `bisect(plane_point, plane_normal, clear_inner=False, clear_outer=False)`
- `spin(steps=8, angle=2*pi, axis="Y")`
- `screw(steps=16, angle=2*pi, height=1.0, axis="Y")`
- `solidify(thickness=0.05)`
- `wireframe(thickness=0.02)`
- `join(other, offset_x=0.0, offset_y=0.0, offset_z=0.0)`
- `join_fast(other, offset_x=0.0, offset_y=0.0, offset_z=0.0)`

Behavior notes:

- `knife` currently selects faces crossed by the cut line direction (selection aid), it does not split topology.
- `bisect` supports side clearing (`clear_inner`/`clear_outer`) by removing whole faces across the plane side.

### 3.5 Deformation / Symmetry

- `bend(factor=0.5, axis="X")`
- `twist(angle=pi/2, axis="Y")`
- `taper(factor=0.5, axis="Y")`
- `stretch(factor=1.1, axis="Y")`
- `shear(factor=0.2, axis="X", by="Y")`
- `warp(center=(0,0,0), strength=0.2, radius=1.0)`
- `symmetrize(axis="X", direction="POSITIVE")`

### 3.6 Sculpting

- `brush(brush_type, center, radius, strength=0.1, falloff="SMOOTH", direction=(0,1,0))`
- `dyntopo(detail_size=0.05, subdivide_collapse=0.5)`
- `sculpt_filter(filter_type="smooth", strength=0.25, radius=None)`

Supported brush names:

- draw, clay, clay_strips, inflate, blob, crease, pinch, flatten, polish, smooth, grab, snake_hook, thumb, scrape, fill, mask

Related tools:

- `mask_brush(center, radius, strength=0.5)`
- `box_mask(min_corner, max_corner, value=1.0)`
- `lasso_mask(points, value=1.0)`
- `clear_mask()`
- `cloth_brush(center, radius, strength=0.1)`
- `pose_brush(center, radius, angle, axis="Y")`
- `face_set(face_indices, set_id)`
- `multires_subdivide(levels=1)`

### 3.7 Remesh / Reduction / Boolean

- `voxel_remesh(voxel_size=0.1)`
- `quad_remesh(target_faces=2000)`
- `decimate(ratio=0.5)`
- `boolean(other, operation="UNION")`

Boolean behavior:

- `UNION`: joins both meshes.
- `DIFFERENCE`: keeps faces of `self` whose face centers are outside `other` AABB.
- `INTERSECTION`: keeps faces of `self` whose face centers are inside `other` AABB.

### 3.8 Shading + UV

- `shade_smooth()`
- `shade_flat()`
- `auto_smooth(angle=radians(30))`
- `mark_seam((v0, v1))`
- `unwrap(method="angle_based", uv_layer=None)`
- `smart_uv_project(uv_layer=None)`
- `project_from_view(axis="Z", uv_layer=None)`

UV state:

- `uv_layers` (dict)
- `active_uv_layer`
- `uv_seams`

### 3.9 Retopo Helpers

- `shrinkwrap(target, strength=1.0, max_samples=20000)`
- `poly_build(points, faces)`
- `relax_topology(iterations=1, strength=0.5)`

## 4. Modifiers

### 4.1 Per-Mesh Modifier Queue

- `add_modifier(modifier, **params)`
- `apply_modifiers()`

Supported modifier names in `apply_modifiers()`:

- `SUBDIVISION` / `SUBDIVISION_SURFACE`
- `MIRROR`
- `ARRAY`
- `SOLIDIFY`
- `DECIMATE`
- `LATTICE`

### 4.2 Modifier Classes (`threedimensions.modifiers`)

- `SubdivisionModifier(levels=1)`
- `MirrorModifier(axis="X")`
- `ArrayModifier(count=2, offset=(1,0,0))`
- `SolidifyModifier(thickness=0.05)`
- `BooleanModifier(target, operation="UNION")`
- `DecimateModifier(ratio=0.5)`
- `LatticeModifier(factor=0.25, axis="Y")`
- `WeldModifier(tolerance=1e-6)`
- `ModifierStack().add(mod).apply(mesh)`

## 5. Curves

### 5.1 BezierCurve

- `BezierCurve(control_points)`
- `evaluate(t)`
- `sample(segments=32)`
- `to_mesh(radius=0.05, radial_segments=12, segments=64)`
- `extrude(distance=0.1)`
- `bevel(radius=0.05)`

### 5.2 NURBSCurve

- `NURBSCurve(control_points, degree=3)`
- `sample(segments=32)`
- `to_mesh(radius=0.05, radial_segments=12, segments=64)`

### 5.3 Lathe

- `td.lathe(profile, steps=32)`

## 6. Node Graph API

- `graph = td.NodeGraph()`
- `n = graph.node(type, **params)`
- `graph.connect(a, b)`
- `mesh = graph.evaluate()`

Primitive node types:

- `Cube`, `Sphere`, `UVSphere`, `Icosphere`, `Cylinder`, `Cone`, `Torus`, `Plane`, `Grid`

Transform/edit node types:

- `Move`, `Translate`, `Rotate`, `Scale`, `Subdivision`, `Subdivide`, `SubdivisionSurface`, `Extrude`, `Bevel`, `Mirror`, `Solidify`, `Decimate`, `Boolean`, `Sculpt`, `Brush`

## 7. Viewer

### 7.1 Blocking Preview

```python
import threedimensions as td
mesh = td.create_torus()
td.viewer(mesh)
```

### 7.2 Interactive Session

```python
import threedimensions as td

with td.viewer() as scene:
    mesh = td.create_cube()
    scene.update(mesh)
    scene.run()
```

Controls:

- Left mouse drag: orbit
- Mouse wheel: zoom

## 8. End-to-End Example

```python
import math
import threedimensions as td

mesh = td.create_cube(1.0)
mesh.select_face(1)
mesh.extrude(0.35)
mesh.bevel(0.05, segments=2)
mesh.subdivide(1)
mesh.brush("smooth", center=(0,0,0), radius=2.0, strength=0.2)
mesh.mark_seam((0, 1)).unwrap()
mesh.add_modifier("MIRROR", axis="X")
mesh.apply_modifiers()
mesh.save("model.obj")
```

## 9. Performance Notes

- Large mesh workflows (100k+ vertices) are fastest with C++ core mode (`td.CORE_MODE == "C++"`).
- In Python fallback mode, prefer fewer high-level passes (`subdivide`, `decimate`, `shrinkwrap`) on huge meshes.
- `shrinkwrap` uses nearest-sample projection with `max_samples` cap for speed control.
