from __future__ import annotations

try:
    from . import _threedimensions_core as _core
except ImportError:  # pragma: no cover
    _core = None

from .mesh import Mesh


def laplacian_smooth(mesh: Mesh, iterations: int = 1, strength: float = 0.5):
    """Topology smoothing using C++ core when available."""
    if _core is not None and hasattr(_core, "topology_laplacian_smooth"):
        _core.topology_laplacian_smooth(mesh._cpp_mesh, int(iterations), float(strength))
        return mesh
    return mesh.sculpt_filter("smooth", strength=float(strength))
