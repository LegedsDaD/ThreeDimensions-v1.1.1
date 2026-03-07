from __future__ import annotations

import math
from typing import List, Sequence, Tuple, Union

from .mesh import Mesh, Vector3, create_cylinder

try:
    from . import _threedimensions_core as _core
except ImportError:  # pragma: no cover
    _core = None

PointLike = Union[Vector3, Tuple[float, float, float]]


def _to_vec3(p: PointLike) -> Vector3:
    if isinstance(p, Vector3):
        return p
    return Vector3(float(p[0]), float(p[1]), float(p[2]))


class Curve:
    pass


class BezierCurve(Curve):
    def __init__(self, control_points: Sequence[PointLike]):
        self.control_points: List[Vector3] = [_to_vec3(p) for p in control_points]
        self._cpp = None
        if _core is not None and hasattr(_core, "BezierCurve"):
            try:
                self._cpp = _core.BezierCurve(self.control_points)
            except Exception:
                self._cpp = None

    def evaluate(self, t: float) -> Vector3:
        if self._cpp is not None:
            return self._cpp.evaluate(float(t))
        t = max(0.0, min(1.0, float(t)))
        tmp = [Vector3(p.x, p.y, p.z) for p in self.control_points]
        while len(tmp) > 1:
            tmp = [tmp[i] * (1.0 - t) + (tmp[i + 1] * t) for i in range(len(tmp) - 1)]
        return tmp[0]

    def sample(self, segments: int = 32) -> List[Vector3]:
        if self._cpp is not None:
            return list(self._cpp.sample(int(segments)))
        segments = max(1, int(segments))
        return [self.evaluate(i / segments) for i in range(segments + 1)]

    def to_mesh(self, radius: float = 0.05, radial_segments: int = 12, segments: int = 64) -> Mesh:
        pts = self.sample(segments=segments)
        if _core is not None and hasattr(_core, "create_tube_along_polyline"):
            return Mesh(_cpp_mesh=_core.create_tube_along_polyline(pts, float(radius), int(radial_segments)))
        out = Mesh("CurveMesh")
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            seg = create_cylinder(radius=radius, height=max(1e-4, math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2)), segments=max(8, radial_segments))
            seg.move(((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, (a.z + b.z) * 0.5))
            out.join(seg)
        return out.calculate_normals()

    def extrude(self, distance: float = 0.1) -> Mesh:
        return self.to_mesh(radius=max(0.001, float(distance) * 0.5))

    def bevel(self, radius: float = 0.05) -> Mesh:
        return self.to_mesh(radius=radius)


class NURBSCurve(Curve):
    def __init__(self, control_points: Sequence[PointLike], degree: int = 3):
        self.control_points: List[Vector3] = [_to_vec3(p) for p in control_points]
        self.degree = int(degree)

    def sample(self, segments: int = 32) -> List[Vector3]:
        # Lightweight fallback: use control polygon interpolation.
        if len(self.control_points) <= 1:
            return list(self.control_points)
        out: List[Vector3] = []
        segments = max(1, int(segments))
        for i in range(segments + 1):
            t = i / segments
            idx = min(len(self.control_points) - 2, int(t * (len(self.control_points) - 1)))
            lt = t * (len(self.control_points) - 1) - idx
            a = self.control_points[idx]
            b = self.control_points[idx + 1]
            out.append(a * (1.0 - lt) + b * lt)
        return out

    def to_mesh(self, radius: float = 0.05, radial_segments: int = 12, segments: int = 64) -> Mesh:
        return BezierCurve(self.control_points).to_mesh(radius=radius, radial_segments=radial_segments, segments=segments)


def lathe(profile: Sequence[PointLike], steps: int = 32) -> Mesh:
    pts = [_to_vec3(p) for p in profile]
    if _core is not None and hasattr(_core, "create_lathe"):
        return Mesh(_cpp_mesh=_core.create_lathe(pts, int(steps)))
    m = Mesh("Lathe")
    steps = max(3, int(steps))
    rings: List[List[int]] = []
    for i in range(steps):
        a = math.tau * i / steps
        ca, sa = math.cos(a), math.sin(a)
        ring = []
        for p in pts:
            ring.append(m.add_vertex((p.x * ca, p.y, p.x * sa)))
        rings.append(ring)
    for i in range(steps):
        ni = (i + 1) % steps
        for j in range(len(pts) - 1):
            m.add_face([rings[i][j], rings[ni][j], rings[ni][j + 1], rings[i][j + 1]])
    return m.calculate_normals()
