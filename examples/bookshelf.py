import sys
import os
import math

# Force import from local source to pick up latest changes
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python')))

import threedimensions as td


def create_bookshelf():
    print("Creating a 3D Bookshelf (curves + modifiers + topology)...")

    # Dimensions (meters-ish units)
    width = 1.0
    height = 1.8
    depth = 0.3
    panel_thickness = 0.03

    shelf_count = 5

    # Side panel (left)
    side = td.Mesh.create_cube(size=1.0)
    side.name = "Bookshelf"
    side.scale(panel_thickness, height, depth)
    side.translate(-width / 2, height / 2, 0)

    # Mirror to create right side
    right_side = side.clone()
    right_side.mirror("X")

    # Top & bottom panels
    panel = td.Mesh.create_cube(size=1.0)
    panel.scale(width, panel_thickness, depth)
    panel.translate(0, height - panel_thickness / 2, 0)
    bottom = td.Mesh.create_cube(size=1.0)
    bottom.scale(width, panel_thickness, depth)
    bottom.translate(0, panel_thickness / 2, 0)

    # One shelf template
    shelf = td.Mesh.create_cube(size=1.0)
    shelf.scale(width - panel_thickness * 2, panel_thickness, depth * 0.95)

    # Array shelves upward
    spacing = (height - panel_thickness * 2) / (shelf_count + 1)
    stack = td.ModifierStack().add(td.ArrayModifier(count=shelf_count, offset=(0.0, spacing, 0.0)))
    shelves = stack.apply(shelf)
    shelves.translate(0, panel_thickness + spacing, 0)

    # Curved front brace using a Bezier tube
    curve = td.BezierCurve([
        (-(width / 2) + panel_thickness, 0.2, depth / 2),
        (-(width / 4), 0.45, depth / 2 + 0.05),
        ((width / 4), 0.45, depth / 2 + 0.05),
        ((width / 2) - panel_thickness, 0.2, depth / 2),
    ])
    brace = curve.to_tube(radius=0.02, radial_segments=12, segments=48)

    # Compose
    side.join(right_side)
    side.join(panel)
    side.join(bottom)
    side.join(shelves)
    side.join(brace)

    # Topology cleanup: weld duplicates & smooth a touch
    side.merge_duplicate_vertices(1e-6)
    try:
        td.topology.laplacian_smooth(side, iterations=1, strength=0.1)
    except Exception:
        pass

    side.calculate_normals()

    print(f"Bookshelf generated: {side.vertex_count} vertices, {side.face_count} faces.")
    side.save("bookshelf.obj")
    print("Saved bookshelf.obj")
    side.save("bookshelf.stl")
    print("Saved bookshelf.stl")


if __name__ == "__main__":
    create_bookshelf()

