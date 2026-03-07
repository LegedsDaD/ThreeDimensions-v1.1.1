"""
ThreeDimensions v1.1.1
Hybrid 3D modeling engine with C++ kernel and Python API.
"""

__version__ = "1.1.1"

from .mesh import (
    CORE_AVAILABLE,
    Mesh,
    TransformOptions,
    Vector3,
    create_cone,
    create_cube,
    create_cylinder,
    create_grid,
    create_icosphere,
    create_plane,
    create_sphere,
    create_torus,
    create_uv_sphere,
)
from .curves import BezierCurve, NURBSCurve, lathe
from .modifiers import ModifierStack
from .nodes import NodeGraph
from .scene import Scene
from .viewer import viewer

CORE_MODE = "C++" if CORE_AVAILABLE else "Python (Fallback)"

__all__ = [
    "__version__",
    "CORE_MODE",
    "Vector3",
    "TransformOptions",
    "Mesh",
    "create_cube",
    "create_sphere",
    "create_uv_sphere",
    "create_icosphere",
    "create_cylinder",
    "create_cone",
    "create_torus",
    "create_plane",
    "create_grid",
    "BezierCurve",
    "NURBSCurve",
    "lathe",
    "ModifierStack",
    "Scene",
    "NodeGraph",
    "viewer",
]
