from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Set, Tuple, Union

try:
    from . import _threedimensions_core as _core
    CORE_AVAILABLE = True
except ImportError:  # pragma: no cover
    from . import core as _core
    CORE_AVAILABLE = False

Vector3 = _core.Vector3
VecLike = Union[Vector3, Tuple[float, float, float], List[float]]


def _vec3(v: VecLike) -> Vector3:
    if isinstance(v, Vector3):
        return Vector3(float(v.x), float(v.y), float(v.z))
    return Vector3(float(v[0]), float(v[1]), float(v[2]))


def _length(v: Vector3) -> float:
    return math.sqrt(float(v.x * v.x + v.y * v.y + v.z * v.z))


def _normalize(v: Vector3) -> Vector3:
    l = _length(v)
    if l <= 1e-12:
        return Vector3(0.0, 0.0, 0.0)
    return Vector3(v.x / l, v.y / l, v.z / l)


def _face_indices(face) -> List[int]:
    return list(face.indices) if hasattr(face, "indices") else list(face)


@dataclass
class TransformOptions:
    mode: str = "OBJECT"
    pivot: str = "MEDIAN_POINT"
    snap: Optional[str] = None
    increment: float = 1.0
    proportional: bool = False
    proportional_radius: float = 1.0
    falloff: str = "SMOOTH"


class Mesh:
    _cursor = Vector3(0.0, 0.0, 0.0)

    def __init__(self, name: str = "Mesh", _cpp_mesh=None):
        if _cpp_mesh is not None:
            self._cpp_mesh = _cpp_mesh
        else:
            try:
                self._cpp_mesh = _core.Mesh(name)
            except TypeError:
                self._cpp_mesh = _core.Mesh()
                if hasattr(self._cpp_mesh, "name"):
                    self._cpp_mesh.name = name
        self.selection_mode = "FACE"
        self.selected_vertices: Set[int] = set()
        self.selected_edges: Set[Tuple[int, int]] = set()
        self.selected_faces: Set[int] = set()
        self.mask_weights: Dict[int, float] = {}
        self.uv_layers: Dict[str, List[Tuple[float, float]]] = {}
        self.active_uv_layer = "UVMap"
        self.modifier_stack: List[Tuple[str, Dict[str, object]]] = []
        self.uv_seams: Set[Tuple[int, int]] = set()
        self.face_sets: Dict[int, int] = {}

    def __getattr__(self, name):
        return getattr(self._cpp_mesh, name)

    @property
    def vertices(self):
        return self._cpp_mesh.vertices

    @property
    def faces(self):
        return self._cpp_mesh.faces

    @property
    def vertex_count(self) -> int:
        return int(getattr(self._cpp_mesh, "vertex_count", len(self._cpp_mesh.vertices)))

    @property
    def face_count(self) -> int:
        return int(getattr(self._cpp_mesh, "face_count", len(self._cpp_mesh.faces)))

    def _pos(self, vertex) -> Vector3:
        return vertex.position if hasattr(vertex, "position") else vertex

    def _set_pos(self, vertex, position: Vector3) -> None:
        if hasattr(vertex, "position"):
            vertex.position = position
        else:
            vertex.x = position.x
            vertex.y = position.y
            vertex.z = position.z

    def _all_edges(self) -> List[Tuple[int, int]]:
        edges: Set[Tuple[int, int]] = set()
        for face in self.faces:
            idx = _face_indices(face)
            if len(idx) < 2:
                continue
            for i in range(len(idx)):
                a = int(idx[i])
                b = int(idx[(i + 1) % len(idx)])
                if a == b:
                    continue
                edges.add((a, b) if a < b else (b, a))
        return list(edges)

    def _edge_midpoint(self, edge: Tuple[int, int]) -> Vector3:
        a = self._pos(self.vertices[int(edge[0])])
        b = self._pos(self.vertices[int(edge[1])])
        return Vector3((a.x + b.x) * 0.5, (a.y + b.y) * 0.5, (a.z + b.z) * 0.5)

    def _face_center(self, fi: int) -> Vector3:
        idx = _face_indices(self.faces[int(fi)])
        if not idx:
            return Vector3(0.0, 0.0, 0.0)
        sx = sy = sz = 0.0
        for vi in idx:
            p = self._pos(self.vertices[int(vi)])
            sx += p.x
            sy += p.y
            sz += p.z
        inv = 1.0 / float(len(idx))
        return Vector3(sx * inv, sy * inv, sz * inv)

    def _rebuild_from_faces(self, faces_idx: List[List[int]]) -> "Mesh":
        used: Set[int] = set()
        for f in faces_idx:
            for i in f:
                used.add(int(i))
        remap: Dict[int, int] = {}
        points: List[Tuple[float, float, float]] = []
        for old in sorted(used):
            p = self._pos(self.vertices[old])
            remap[old] = len(points)
            points.append((p.x, p.y, p.z))
        self.clear()
        for p in points:
            self.add_vertex(p)
        for f in faces_idx:
            rf = [remap[int(i)] for i in f if int(i) in remap]
            if len(set(rf)) >= 3:
                self.add_face(rf)
        return self.calculate_normals()

    def _aabb(self) -> Tuple[Vector3, Vector3]:
        if self.vertex_count == 0:
            z = Vector3(0.0, 0.0, 0.0)
            return z, z
        pts = [self._pos(v) for v in self.vertices]
        minp = Vector3(min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))
        maxp = Vector3(max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))
        return minp, maxp

    @staticmethod
    def set_cursor(position: VecLike) -> None:
        Mesh._cursor = _vec3(position)

    @staticmethod
    def cursor() -> Vector3:
        return Mesh._cursor

    def add_vertex(self, position: VecLike) -> int:
        p = _vec3(position)
        if hasattr(self._cpp_mesh, "add_vertex"):
            self._cpp_mesh.add_vertex(p)
        else:
            self._cpp_mesh.addVertex(p)
        return self.vertex_count - 1

    def add_face(self, indices: Sequence[int]) -> int:
        if hasattr(self._cpp_mesh, "add_face"):
            self._cpp_mesh.add_face([int(i) for i in indices])
        else:
            self._cpp_mesh.addFace([int(i) for i in indices])
        return self.face_count - 1

    def calculate_normals(self) -> "Mesh":
        if hasattr(self._cpp_mesh, "calculate_normals"):
            self._cpp_mesh.calculate_normals()
        elif hasattr(self._cpp_mesh, "calculateNormals"):
            self._cpp_mesh.calculateNormals()
        return self

    def clone(self) -> "Mesh":
        if hasattr(self._cpp_mesh, "clone"):
            return Mesh(_cpp_mesh=self._cpp_mesh.clone())
        out = Mesh()
        for v in self.vertices:
            p = self._pos(v)
            out.add_vertex((p.x, p.y, p.z))
        for f in self.faces:
            out.add_face(_face_indices(f))
        return out.calculate_normals()

    def clear(self) -> "Mesh":
        if hasattr(self._cpp_mesh, "clear"):
            self._cpp_mesh.clear()
        else:
            self._cpp_mesh.vertices.clear()
            self._cpp_mesh.faces.clear()
        self.selected_vertices.clear()
        self.selected_edges.clear()
        self.selected_faces.clear()
        return self

    def save(self, filepath: str) -> "Mesh":
        self._cpp_mesh.save(filepath)
        return self

    def _selected_vertices(self, mode: Optional[str] = None) -> Set[int]:
        m = (mode or self.selection_mode).upper()
        if m == "VERTEX":
            return set(self.selected_vertices)
        if m == "EDGE":
            out = set()
            for a, b in self.selected_edges:
                out.add(a)
                out.add(b)
            return out
        if m == "FACE":
            out = set()
            for fi in self.selected_faces:
                if 0 <= fi < self.face_count:
                    out.update(_face_indices(self.faces[fi]))
            return out
        return set(range(self.vertex_count))

    def _pivot(self, verts: Set[int], pivot: str) -> Vector3:
        pv = pivot.upper()
        if pv == "CURSOR":
            return Mesh.cursor()
        if not verts:
            return Vector3(0.0, 0.0, 0.0)
        sx = sy = sz = 0.0
        for i in verts:
            p = self._pos(self.vertices[i])
            sx += p.x
            sy += p.y
            sz += p.z
        inv = 1.0 / len(verts)
        return Vector3(sx * inv, sy * inv, sz * inv)

    def _falloff(self, dist: float, radius: float, mode: str) -> float:
        if radius <= 0.0:
            return 0.0
        t = max(0.0, min(1.0, 1.0 - (dist / radius)))
        m = mode.upper()
        if m == "SPHERE":
            return math.sqrt(max(0.0, 1.0 - (1.0 - t) * (1.0 - t)))
        if m == "ROOT":
            return math.sqrt(t)
        if m == "SHARP":
            return t * t
        if m == "LINEAR":
            return t
        return t * t * (3.0 - 2.0 * t)

    def _snap(self, p: Vector3, snap: Optional[str], increment: float) -> Vector3:
        if snap is None:
            return p
        s = snap.upper()
        if s in ("GRID", "INCREMENT"):
            inc = max(1e-9, float(increment))
            return Vector3(round(p.x / inc) * inc, round(p.y / inc) * inc, round(p.z / inc) * inc)
        if s == "VERTEX" and self.vertex_count:
            best = self._pos(self.vertices[0])
            bd = (best.x - p.x) ** 2 + (best.y - p.y) ** 2 + (best.z - p.z) ** 2
            for v in self.vertices[1:]:
                q = self._pos(v)
                d = (q.x - p.x) ** 2 + (q.y - p.y) ** 2 + (q.z - p.z) ** 2
                if d < bd:
                    best, bd = q, d
            return Vector3(best.x, best.y, best.z)
        return p

    def move(self, delta: VecLike, options: Optional[TransformOptions] = None) -> "Mesh":
        d = _vec3(delta)
        opts = options or TransformOptions(mode=self.selection_mode)
        verts = self._selected_vertices(opts.mode)
        if not verts:
            verts = set(range(self.vertex_count))
        pivot = self._pivot(verts, opts.pivot)
        for i, v in enumerate(self.vertices):
            if i not in verts or self.mask_weights.get(i, 0.0) >= 1.0:
                continue
            p = self._pos(v)
            w = 1.0
            if opts.proportional:
                w = self._falloff(_length(Vector3(p.x - pivot.x, p.y - pivot.y, p.z - pivot.z)), opts.proportional_radius, opts.falloff)
            w *= 1.0 - self.mask_weights.get(i, 0.0)
            self._set_pos(v, self._snap(Vector3(p.x + d.x * w, p.y + d.y * w, p.z + d.z * w), opts.snap, opts.increment))
        return self.calculate_normals()

    def translate(self, *args, **kwargs) -> "Mesh":
        if len(args) == 1 and not kwargs:
            return self.move(args[0])
        if len(args) >= 3:
            return self.move((float(args[0]), float(args[1]), float(args[2])))
        return self.move((float(kwargs.get("x", 0.0)), float(kwargs.get("y", 0.0)), float(kwargs.get("z", 0.0))))

    def rotate(self, angle: float, axis: str = "Z", options: Optional[TransformOptions] = None) -> "Mesh":
        opts = options or TransformOptions(mode=self.selection_mode)
        verts = self._selected_vertices(opts.mode)
        if not verts:
            verts = set(range(self.vertex_count))
        pivot = self._pivot(verts, opts.pivot)
        c, s = math.cos(float(angle)), math.sin(float(angle))
        ax = axis.upper()
        for i, v in enumerate(self.vertices):
            if i not in verts or self.mask_weights.get(i, 0.0) >= 1.0:
                continue
            p = self._pos(v)
            x, y, z = p.x - pivot.x, p.y - pivot.y, p.z - pivot.z
            if ax == "X":
                rx, ry, rz = x, y * c - z * s, y * s + z * c
            elif ax == "Y":
                rx, ry, rz = x * c + z * s, y, -x * s + z * c
            else:
                rx, ry, rz = x * c - y * s, x * s + y * c, z
            self._set_pos(v, self._snap(Vector3(pivot.x + rx, pivot.y + ry, pivot.z + rz), opts.snap, opts.increment))
        return self.calculate_normals()

    def rotate_x(self, angle: float) -> "Mesh":
        return self.rotate(angle, "X")

    def rotate_y(self, angle: float) -> "Mesh":
        return self.rotate(angle, "Y")

    def rotate_z(self, angle: float) -> "Mesh":
        return self.rotate(angle, "Z")

    def scale(self, *args, options: Optional[TransformOptions] = None) -> "Mesh":
        if len(args) == 1 and not isinstance(args[0], (tuple, list, Vector3)):
            sv = Vector3(float(args[0]), float(args[0]), float(args[0]))
        elif len(args) == 1:
            sv = _vec3(args[0])
        elif len(args) >= 3:
            sv = Vector3(float(args[0]), float(args[1]), float(args[2]))
        else:
            sv = Vector3(1.0, 1.0, 1.0)
        opts = options or TransformOptions(mode=self.selection_mode)
        verts = self._selected_vertices(opts.mode)
        if not verts:
            verts = set(range(self.vertex_count))
        pivot = self._pivot(verts, opts.pivot)
        for i, v in enumerate(self.vertices):
            if i not in verts or self.mask_weights.get(i, 0.0) >= 1.0:
                continue
            p = self._pos(v)
            np = Vector3(pivot.x + (p.x - pivot.x) * sv.x, pivot.y + (p.y - pivot.y) * sv.y, pivot.z + (p.z - pivot.z) * sv.z)
            self._set_pos(v, self._snap(np, opts.snap, opts.increment))
        return self.calculate_normals()
    def mirror(self, axis: str = "X") -> "Mesh":
        if hasattr(self._cpp_mesh, "mirror"):
            self._cpp_mesh.mirror(axis)
            return self
        ax = axis.upper()
        for v in self.vertices:
            p = self._pos(v)
            if ax == "X":
                self._set_pos(v, Vector3(-p.x, p.y, p.z))
            elif ax == "Y":
                self._set_pos(v, Vector3(p.x, -p.y, p.z))
            else:
                self._set_pos(v, Vector3(p.x, p.y, -p.z))
        return self.calculate_normals()

    def mirror_transform(self, axis: str = "X") -> "Mesh":
        return self.mirror(axis)

    def select_mode(self, mode: str) -> "Mesh":
        self.selection_mode = str(mode).upper()
        return self

    def select_vertex(self, vertex_index: int, extend: bool = False) -> "Mesh":
        if not extend:
            self.selected_vertices.clear()
        self.selection_mode = "VERTEX"
        self.selected_vertices.add(int(vertex_index))
        return self

    def select_edge(self, edge: Tuple[int, int], extend: bool = False) -> "Mesh":
        if not extend:
            self.selected_edges.clear()
        self.selection_mode = "EDGE"
        a, b = int(edge[0]), int(edge[1])
        self.selected_edges.add((a, b) if a < b else (b, a))
        return self

    def select_face(self, face_index: int, extend: bool = False) -> "Mesh":
        if not extend:
            self.selected_faces.clear()
        self.selection_mode = "FACE"
        self.selected_faces.add(int(face_index))
        return self

    def select_loop(self, edge: Tuple[int, int]) -> "Mesh":
        self.select_edge(edge)
        e = (min(edge), max(edge))
        for face in self.faces:
            idx = _face_indices(face)
            ed = {(min(idx[i], idx[(i + 1) % len(idx)]), max(idx[i], idx[(i + 1) % len(idx)])) for i in range(len(idx))}
            if e in ed:
                self.selected_edges.update(ed)
        return self

    def select_ring(self, edge: Tuple[int, int]) -> "Mesh":
        self.select_edge(edge)
        e = (min(edge), max(edge))
        for face in self.faces:
            idx = _face_indices(face)
            if len(idx) == 4:
                qe = [(min(idx[0], idx[1]), max(idx[0], idx[1])), (min(idx[1], idx[2]), max(idx[1], idx[2])), (min(idx[2], idx[3]), max(idx[2], idx[3])), (min(idx[3], idx[0]), max(idx[3], idx[0]))]
                if e in qe:
                    self.selected_edges.add(qe[(qe.index(e) + 2) % 4])
        return self

    def box_select(self, min_corner: VecLike, max_corner: VecLike, mode: Optional[str] = None) -> "Mesh":
        mn = _vec3(min_corner)
        mx = _vec3(max_corner)
        mode = (mode or self.selection_mode).upper()
        if mode == "VERTEX":
            self.selected_vertices = set(i for i, v in enumerate(self.vertices) if mn.x <= self._pos(v).x <= mx.x and mn.y <= self._pos(v).y <= mx.y and mn.z <= self._pos(v).z <= mx.z)
        elif mode == "EDGE":
            self.selected_edges = set(
                e for e in self._all_edges()
                if mn.x <= self._edge_midpoint(e).x <= mx.x and mn.y <= self._edge_midpoint(e).y <= mx.y and mn.z <= self._edge_midpoint(e).z <= mx.z
            )
        elif mode == "FACE":
            self.selected_faces = set(
                i for i in range(self.face_count)
                if mn.x <= self._face_center(i).x <= mx.x and mn.y <= self._face_center(i).y <= mx.y and mn.z <= self._face_center(i).z <= mx.z
            )
        self.selection_mode = mode
        return self

    def circle_select(self, center: VecLike, radius: float, mode: str = "VERTEX") -> "Mesh":
        c = _vec3(center)
        r2 = float(radius) * float(radius)
        m = mode.upper()
        if m == "VERTEX":
            self.selected_vertices = set(i for i, v in enumerate(self.vertices) if (self._pos(v).x - c.x) ** 2 + (self._pos(v).y - c.y) ** 2 + (self._pos(v).z - c.z) ** 2 <= r2)
        elif m == "EDGE":
            self.selected_edges = set(
                e for e in self._all_edges()
                if (self._edge_midpoint(e).x - c.x) ** 2 + (self._edge_midpoint(e).y - c.y) ** 2 + (self._edge_midpoint(e).z - c.z) ** 2 <= r2
            )
        elif m == "FACE":
            self.selected_faces = set(
                i for i in range(self.face_count)
                if (self._face_center(i).x - c.x) ** 2 + (self._face_center(i).y - c.y) ** 2 + (self._face_center(i).z - c.z) ** 2 <= r2
            )
        self.selection_mode = m
        return self

    def lasso_select(self, points: Sequence[VecLike], mode: str = "VERTEX") -> "Mesh":
        if not points:
            return self
        xs = [float(_vec3(p).x) for p in points]
        ys = [float(_vec3(p).y) for p in points]
        zs = [float(_vec3(p).z) for p in points]
        return self.box_select((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)), mode=mode)

    def select_similar(self, by: str = "face_size", value: Optional[float] = None, tolerance: float = 0.1) -> "Mesh":
        if by.lower() != "face_size":
            return self
        areas = []
        for fi, face in enumerate(self.faces):
            idx = _face_indices(face)
            if len(idx) < 3:
                continue
            p0 = self._pos(self.vertices[idx[0]])
            area = 0.0
            for i in range(1, len(idx) - 1):
                p1 = self._pos(self.vertices[idx[i]])
                p2 = self._pos(self.vertices[idx[i + 1]])
                a = Vector3(p1.x - p0.x, p1.y - p0.y, p1.z - p0.z)
                b = Vector3(p2.x - p0.x, p2.y - p0.y, p2.z - p0.z)
                c = Vector3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x)
                area += 0.5 * _length(c)
            areas.append((fi, area))
        if not areas:
            return self
        t = value if value is not None else areas[0][1]
        self.selected_faces = {fi for fi, a in areas if abs(a - t) <= max(1.0, t) * float(tolerance)}
        self.selection_mode = "FACE"
        return self

    def extrude_face(self, face_index: int, distance: float = 0.1) -> "Mesh":
        if hasattr(self._cpp_mesh, "extrude_face"):
            self._cpp_mesh.extrude_face(int(face_index), float(distance))
        return self.calculate_normals()

    def extrude(self, distance: float = 0.1, face_indices: Optional[Sequence[int]] = None) -> "Mesh":
        faces = list(face_indices) if face_indices is not None else (list(self.selected_faces) or [0])
        for fi in sorted(set(int(i) for i in faces if 0 <= int(i) < self.face_count), reverse=True):
            self.extrude_face(fi, distance)
        return self

    def inset_faces(self, amount: float = 0.05) -> "Mesh":
        scale = max(0.0, 1.0 - float(amount))
        for fi in list(self.selected_faces) or [0]:
            if hasattr(self._cpp_mesh, "scale_face"):
                self._cpp_mesh.scale_face(int(fi), float(scale))
            elif hasattr(self._cpp_mesh, "scaleFace"):
                self._cpp_mesh.scaleFace(int(fi), float(scale))
        return self.calculate_normals()

    def bevel(self, width: float = 0.05, segments: int = 1) -> "Mesh":
        for _ in range(max(1, int(segments))):
            self.inset_faces(width * 0.5)
            self.extrude(width)
        return self

    def bridge_edge_loops(self, loop_a: Sequence[int], loop_b: Sequence[int]) -> "Mesh":
        n = min(len(loop_a), len(loop_b))
        for i in range(n):
            self.add_face([int(loop_a[i]), int(loop_a[(i + 1) % n]), int(loop_b[(i + 1) % n]), int(loop_b[i])])
        return self.calculate_normals()

    def fill(self, vertices: Optional[Sequence[int]] = None) -> "Mesh":
        idx = list(vertices) if vertices is not None else list(self.selected_vertices)
        if len(idx) >= 3:
            self.add_face(idx)
        return self.calculate_normals()

    def grid_fill(self, boundary: Sequence[int], rows: int = 2, cols: int = 2) -> "Mesh":
        idx = list(boundary)
        if len(idx) < 4:
            return self.fill(idx)
        c = Vector3(0.0, 0.0, 0.0)
        for i in idx:
            p = self._pos(self.vertices[i])
            c = Vector3(c.x + p.x, c.y + p.y, c.z + p.z)
        ci = self.add_vertex((c.x / len(idx), c.y / len(idx), c.z / len(idx)))
        for i in range(len(idx)):
            self.add_face([idx[i], idx[(i + 1) % len(idx)], ci])
        return self.calculate_normals()

    def subdivide(self, levels: int = 1) -> "Mesh":
        if hasattr(self._cpp_mesh, "subdivide"):
            self._cpp_mesh.subdivide(int(levels))
        return self.calculate_normals()

    def loop_cut(self, cuts: int = 1) -> "Mesh":
        return self.subdivide(max(1, int(cuts)))

    def knife(self, start: VecLike, end: VecLike) -> "Mesh":
        s = _vec3(start)
        e = _vec3(end)
        n = Vector3(e.x - s.x, e.y - s.y, e.z - s.z)
        if _length(n) <= 1e-9:
            return self
        # Knife fallback: select faces intersecting the cut slab (visual segmentation aid).
        self.selected_faces.clear()
        for fi in range(self.face_count):
            idx = _face_indices(self.faces[fi])
            if not idx:
                continue
            ds: List[float] = []
            for vi in idx:
                p = self._pos(self.vertices[int(vi)])
                ds.append((p.x - s.x) * n.x + (p.y - s.y) * n.y + (p.z - s.z) * n.z)
            if min(ds) <= 0.0 <= max(ds):
                self.selected_faces.add(fi)
        self.selection_mode = "FACE"
        return self

    def bisect(self, plane_point: VecLike, plane_normal: VecLike, clear_inner: bool = False, clear_outer: bool = False) -> "Mesh":
        pp = _vec3(plane_point)
        pn = _normalize(_vec3(plane_normal))
        if _length(pn) <= 1e-9:
            return self
        kept: List[List[int]] = []
        cut_faces: Set[int] = set()
        for fi, face in enumerate(self.faces):
            idx = _face_indices(face)
            if len(idx) < 3:
                continue
            ds: List[float] = []
            for vi in idx:
                p = self._pos(self.vertices[int(vi)])
                ds.append((p.x - pp.x) * pn.x + (p.y - pp.y) * pn.y + (p.z - pp.z) * pn.z)
            all_inner = all(d < 0.0 for d in ds)
            all_outer = all(d > 0.0 for d in ds)
            if min(ds) <= 0.0 <= max(ds):
                cut_faces.add(fi)
            if clear_inner and all_inner:
                continue
            if clear_outer and all_outer:
                continue
            kept.append(idx)
        if clear_inner or clear_outer:
            self._rebuild_from_faces(kept)
        self.selected_faces = cut_faces
        self.selection_mode = "FACE"
        return self

    def spin(self, steps: int = 8, angle: float = math.tau, axis: str = "Y") -> "Mesh":
        base = self.clone()
        for i in range(1, max(1, int(steps))):
            self.join(base.clone().rotate((float(angle) / float(steps)) * i, axis))
        return self.calculate_normals()

    def screw(self, steps: int = 16, angle: float = math.tau, height: float = 1.0, axis: str = "Y") -> "Mesh":
        base = self.clone()
        for i in range(1, max(1, int(steps))):
            t = float(i) / float(steps)
            c = base.clone().rotate(float(angle) * t, axis)
            c.move((0.0, height * t, 0.0))
            self.join(c)
        return self.calculate_normals()

    def solidify(self, thickness: float = 0.05) -> "Mesh":
        shell = self.clone().move((0.0, thickness, 0.0))
        self.join(shell)
        return self.calculate_normals()

    def wireframe(self, thickness: float = 0.02) -> "Mesh":
        return self.inset_faces(thickness).extrude(-thickness)

    def join(self, other: "Mesh", offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0) -> "Mesh":
        off = Vector3(float(offset_x), float(offset_y), float(offset_z))
        if hasattr(self._cpp_mesh, "join"):
            src = other._cpp_mesh if isinstance(other, Mesh) else other
            self._cpp_mesh.join(src, off)
            return self
        base = self.vertex_count
        for v in other.vertices:
            p = other._pos(v)
            self.add_vertex((p.x + off.x, p.y + off.y, p.z + off.z))
        for f in other.faces:
            self.add_face([base + int(i) for i in _face_indices(f)])
        return self.calculate_normals()

    def join_fast(self, other: "Mesh", offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0) -> "Mesh":
        return self.join(other, offset_x, offset_y, offset_z)
    def bend(self, factor: float = 0.5, axis: str = "X") -> "Mesh":
        return self.rotate(float(factor) * math.pi * 0.5, axis)

    def twist(self, angle: float = math.pi * 0.5, axis: str = "Y") -> "Mesh":
        return self.rotate(angle, axis)

    def taper(self, factor: float = 0.5, axis: str = "Y") -> "Mesh":
        if axis.upper() == "Y":
            return self.scale(1.0 + factor, 1.0, 1.0 + factor)
        if axis.upper() == "X":
            return self.scale(1.0, 1.0 + factor, 1.0 + factor)
        return self.scale(1.0 + factor, 1.0 + factor, 1.0)

    def stretch(self, factor: float = 1.1, axis: str = "Y") -> "Mesh":
        if axis.upper() == "X":
            return self.scale(float(factor), 1.0, 1.0)
        if axis.upper() == "Z":
            return self.scale(1.0, 1.0, float(factor))
        return self.scale(1.0, float(factor), 1.0)

    def shear(self, factor: float = 0.2, axis: str = "X", by: str = "Y") -> "Mesh":
        return self.move((factor, 0.0, 0.0) if axis.upper() == "X" else ((0.0, factor, 0.0) if axis.upper() == "Y" else (0.0, 0.0, factor)))

    def warp(self, center: VecLike = (0.0, 0.0, 0.0), strength: float = 0.2, radius: float = 1.0) -> "Mesh":
        c = _vec3(center)
        for i, v in enumerate(self.vertices):
            p = self._pos(v)
            d = _length(Vector3(p.x - c.x, p.y - c.y, p.z - c.z))
            if d <= radius:
                w = self._falloff(d, radius, "SMOOTH") * strength
                self._set_pos(v, Vector3(p.x, p.y + w, p.z))
        return self.calculate_normals()

    def symmetrize(self, axis: str = "X", direction: str = "POSITIVE") -> "Mesh":
        ax = axis.upper()
        keep_positive = direction.upper().startswith("POS")
        pts = [self._pos(v) for v in self.vertices]
        side_pts: List[Tuple[float, float, float]] = []
        for p in pts:
            coord = p.x if ax == "X" else (p.y if ax == "Y" else p.z)
            if (coord >= 0.0) == keep_positive:
                side_pts.append((p.x, p.y, p.z))
        if not side_pts:
            return self
        for x, y, z in side_pts:
            if ax == "X":
                self.add_vertex((-x, y, z))
            elif ax == "Y":
                self.add_vertex((x, -y, z))
            else:
                self.add_vertex((x, y, -z))
        return self.merge_duplicate_vertices(1e-6).calculate_normals()

    def brush(self, brush_type: str, center: VecLike, radius: float, strength: float = 0.1, falloff: str = "SMOOTH", direction: VecLike = (0.0, 1.0, 0.0)) -> "Mesh":
        b = brush_type.lower().replace("_", " ")
        c = _vec3(center)
        if b in ("mask", "mask brush"):
            for i, v in enumerate(self.vertices):
                if _length(Vector3(self._pos(v).x - c.x, self._pos(v).y - c.y, self._pos(v).z - c.z)) <= radius:
                    self.mask_weights[i] = min(1.0, self.mask_weights.get(i, 0.0) + strength)
            return self
        if b in ("smooth", "polish", "relax", "flatten", "scrape"):
            return self.sculpt_filter("smooth", strength, radius)
        if b in ("inflate", "draw", "clay", "clay strips", "blob", "fill") and hasattr(self._cpp_mesh, "inflate"):
            self._cpp_mesh.inflate(c, float(radius), float(strength))
            return self
        d = _vec3(direction)
        return self.move((d.x * strength, d.y * strength, d.z * strength), TransformOptions(mode="OBJECT", proportional=True, proportional_radius=float(radius), falloff=falloff))

    def dyntopo(self, detail_size: float = 0.05, subdivide_collapse: float = 0.5) -> "Mesh":
        target = max(1000, int(1.0 / max(1e-5, detail_size)) * 120)
        if self.vertex_count < target:
            self.subdivide(1)
        elif self.vertex_count > target * 2:
            self.decimate(max(0.05, min(0.95, float(subdivide_collapse))))
        return self

    def sculpt_filter(self, filter_type: str = "smooth", strength: float = 0.25, radius: Optional[float] = None) -> "Mesh":
        if hasattr(self._cpp_mesh, "smooth"):
            c = Mesh.cursor()
            self._cpp_mesh.smooth(c, float(radius or 1.0), float(abs(strength)))
        return self

    def voxel_remesh(self, voxel_size: float = 0.1) -> "Mesh":
        return self.merge_duplicate_vertices(max(1e-6, voxel_size * 0.5))

    def quad_remesh(self, target_faces: int = 2000) -> "Mesh":
        while self.face_count < target_faces and self.face_count < 200000:
            self.subdivide(1)
        return self

    def decimate(self, ratio: float = 0.5) -> "Mesh":
        r = max(0.01, min(1.0, float(ratio)))
        if r >= 0.999 or self.face_count < 4:
            return self
        target = max(1, int(self.face_count * r))
        step = max(1, int(round(self.face_count / float(target))))
        kept: List[List[int]] = []
        for i, f in enumerate(self.faces):
            if i % step == 0:
                idx = _face_indices(f)
                if len(set(idx)) >= 3:
                    kept.append(idx)
        if not kept:
            kept = [_face_indices(self.faces[0])]
        return self._rebuild_from_faces(kept)

    def shade_smooth(self) -> "Mesh":
        return self.calculate_normals()

    def shade_flat(self) -> "Mesh":
        return self.calculate_normals()

    def auto_smooth(self, angle: float = math.radians(30.0)) -> "Mesh":
        return self.calculate_normals()

    def mark_seam(self, edge: Tuple[int, int]) -> "Mesh":
        a, b = int(edge[0]), int(edge[1])
        self.uv_seams.add((a, b) if a < b else (b, a))
        return self

    def unwrap(self, method: str = "angle_based", uv_layer: Optional[str] = None) -> "Mesh":
        layer = uv_layer or self.active_uv_layer
        if layer not in self.uv_layers or len(self.uv_layers[layer]) != self.vertex_count:
            self.uv_layers[layer] = [(0.0, 0.0) for _ in range(self.vertex_count)]
        pts = [self._pos(v) for v in self.vertices]
        if not pts:
            return self
        minx, maxx = min(p.x for p in pts), max(p.x for p in pts)
        minz, maxz = min(p.z for p in pts), max(p.z for p in pts)
        sx = max(1e-8, maxx - minx)
        sz = max(1e-8, maxz - minz)
        self.uv_layers[layer] = [((p.x - minx) / sx, (p.z - minz) / sz) for p in pts]
        return self

    def smart_uv_project(self, uv_layer: Optional[str] = None) -> "Mesh":
        return self.unwrap("smart", uv_layer)

    def project_from_view(self, axis: str = "Z", uv_layer: Optional[str] = None) -> "Mesh":
        layer = uv_layer or self.active_uv_layer
        if layer not in self.uv_layers or len(self.uv_layers[layer]) != self.vertex_count:
            self.uv_layers[layer] = [(0.0, 0.0) for _ in range(self.vertex_count)]
        pts = [self._pos(v) for v in self.vertices]
        if not pts:
            return self
        ax = axis.upper()
        if ax == "X":
            uu = [p.y for p in pts]
            vv = [p.z for p in pts]
        elif ax == "Y":
            uu = [p.x for p in pts]
            vv = [p.z for p in pts]
        else:
            uu = [p.x for p in pts]
            vv = [p.y for p in pts]
        minu, maxu = min(uu), max(uu)
        minv, maxv = min(vv), max(vv)
        su = max(1e-8, maxu - minu)
        sv = max(1e-8, maxv - minv)
        self.uv_layers[layer] = [((u - minu) / su, (v - minv) / sv) for u, v in zip(uu, vv)]
        return self

    def shrinkwrap(self, target: "Mesh", strength: float = 1.0, max_samples: int = 20000) -> "Mesh":
        if target.vertex_count == 0 or self.vertex_count == 0:
            return self
        s = max(0.0, min(1.0, float(strength)))
        samples = [target._pos(v) for v in target.vertices[: max(1, int(max_samples))]]
        for v in self.vertices:
            p = self._pos(v)
            best = samples[0]
            best_d2 = (p.x - best.x) ** 2 + (p.y - best.y) ** 2 + (p.z - best.z) ** 2
            for q in samples[1:]:
                d2 = (p.x - q.x) ** 2 + (p.y - q.y) ** 2 + (p.z - q.z) ** 2
                if d2 < best_d2:
                    best_d2 = d2
                    best = q
            self._set_pos(v, Vector3(p.x + (best.x - p.x) * s, p.y + (best.y - p.y) * s, p.z + (best.z - p.z) * s))
        return self.calculate_normals()

    def poly_build(self, points: Sequence[VecLike], faces: Sequence[Sequence[int]]) -> "Mesh":
        base = self.vertex_count
        for p in points:
            self.add_vertex(p)
        for f in faces:
            self.add_face([base + int(i) for i in f])
        return self.calculate_normals()

    def relax_topology(self, iterations: int = 1, strength: float = 0.5) -> "Mesh":
        return self.sculpt_filter("smooth", strength)

    def multires_subdivide(self, levels: int = 1) -> "Mesh":
        self.modifier_stack.append(("MULTIRES", {"levels": int(levels)}))
        return self.subdivide(levels)

    def face_set(self, face_indices: Sequence[int], set_id: int) -> "Mesh":
        sid = int(set_id)
        for fi in face_indices:
            self.face_sets[int(fi)] = sid
        return self

    def pose_brush(self, center: VecLike, radius: float, angle: float, axis: str = "Y") -> "Mesh":
        Mesh.set_cursor(center)
        return self.rotate(angle, axis)

    def cloth_brush(self, center: VecLike, radius: float, strength: float = 0.1) -> "Mesh":
        return self.brush("smooth", center, radius, strength)

    def mask_brush(self, center: VecLike, radius: float, strength: float = 0.5) -> "Mesh":
        return self.brush("mask", center, radius, strength)

    def box_mask(self, min_corner: VecLike, max_corner: VecLike, value: float = 1.0) -> "Mesh":
        mn = _vec3(min_corner)
        mx = _vec3(max_corner)
        for i, v in enumerate(self.vertices):
            p = self._pos(v)
            if mn.x <= p.x <= mx.x and mn.y <= p.y <= mx.y and mn.z <= p.z <= mx.z:
                self.mask_weights[i] = max(0.0, min(1.0, float(value)))
        return self

    def lasso_mask(self, points: Sequence[VecLike], value: float = 1.0) -> "Mesh":
        if not points:
            return self
        xs = [float(_vec3(p).x) for p in points]
        ys = [float(_vec3(p).y) for p in points]
        zs = [float(_vec3(p).z) for p in points]
        return self.box_mask((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)), value)

    def clear_mask(self) -> "Mesh":
        self.mask_weights.clear()
        return self

    def add_modifier(self, modifier: str, **params) -> "Mesh":
        self.modifier_stack.append((modifier.upper(), dict(params)))
        return self

    def apply_modifiers(self) -> "Mesh":
        for name, params in self.modifier_stack:
            if name in ("SUBDIVISION", "SUBDIVISION_SURFACE"):
                self.subdivide(int(params.get("levels", params.get("level", 1))))
            elif name == "MIRROR":
                self.mirror(str(params.get("axis", "X")))
            elif name == "ARRAY":
                self.array(int(params.get("count", 2)), _vec3(params.get("offset", (1.0, 0.0, 0.0))))
            elif name == "SOLIDIFY":
                self.solidify(float(params.get("thickness", 0.05)))
            elif name == "DECIMATE":
                self.decimate(float(params.get("ratio", 0.5)))
            elif name == "LATTICE":
                self.taper(float(params.get("factor", 0.25)), str(params.get("axis", "Y")))
        self.modifier_stack.clear()
        return self

    def array(self, count: int = 2, offset: VecLike = (1.0, 0.0, 0.0)) -> "Mesh":
        n = max(1, int(count))
        if n == 1:
            return self
        off = _vec3(offset)
        base = self.clone()
        for i in range(1, n):
            self.join(base.clone(), offset_x=off.x * i, offset_y=off.y * i, offset_z=off.z * i)
        return self

    def boolean(self, other: "Mesh", operation: str = "UNION") -> "Mesh":
        op = operation.upper()
        if op == "UNION":
            return self.join(other)
        if other.face_count == 0 or self.face_count == 0:
            return self
        omin, omax = other._aabb()
        if op in ("DIFFERENCE", "INTERSECTION"):
            kept: List[List[int]] = []
            for fi, face in enumerate(self.faces):
                c = self._face_center(fi)
                inside = (omin.x <= c.x <= omax.x and omin.y <= c.y <= omax.y and omin.z <= c.z <= omax.z)
                if op == "DIFFERENCE":
                    if not inside:
                        kept.append(_face_indices(face))
                else:  # INTERSECTION
                    if inside:
                        kept.append(_face_indices(face))
            if kept:
                return self._rebuild_from_faces(kept)
            return self.clear()
        return self

    def merge_duplicate_vertices(self, tolerance: float = 1e-6) -> "Mesh":
        if hasattr(self._cpp_mesh, "merge_duplicate_vertices"):
            self._cpp_mesh.merge_duplicate_vertices(float(tolerance))
        return self


def create_cube(size: float = 1.0) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_cube"):
        return Mesh(_cpp_mesh=_core.create_cube(float(size)))
    m = Mesh("Cube")
    s = float(size) * 0.5
    for p in [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s), (-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)]:
        m.add_vertex(p)
    for f in ([0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 3, 7, 4]):
        m.add_face(f)
    return m.calculate_normals()


def create_plane(size: float = 2.0, subdivisions: int = 1) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_plane"):
        return Mesh(_cpp_mesh=_core.create_plane(float(size), int(subdivisions)))
    m = Mesh("Plane")
    sub = max(1, int(subdivisions))
    step = float(size) / sub
    half = float(size) * 0.5
    ids = []
    for y in range(sub + 1):
        for x in range(sub + 1):
            ids.append(m.add_vertex((-half + x * step, 0.0, -half + y * step)))
    for y in range(sub):
        for x in range(sub):
            i = y * (sub + 1) + x
            m.add_face([ids[i], ids[i + 1], ids[i + sub + 2], ids[i + sub + 1]])
    return m.calculate_normals()


def create_grid(size: float = 2.0, x_subdivisions: int = 10, y_subdivisions: int = 10) -> Mesh:
    return create_plane(size=size, subdivisions=max(int(x_subdivisions), int(y_subdivisions)))


def create_sphere(radius: float = 1.0, segments: int = 32, rings: int = 16) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_sphere"):
        return Mesh(_cpp_mesh=_core.create_sphere(float(radius), int(segments), int(rings)))
    m = Mesh("Sphere")
    seg = max(3, int(segments))
    rng = max(2, int(rings))
    idx = [[0] * seg for _ in range(rng + 1)]
    for r in range(rng + 1):
        phi = math.pi * r / rng
        y = math.cos(phi) * radius
        rr = math.sin(phi) * radius
        for s in range(seg):
            th = math.tau * s / seg
            idx[r][s] = m.add_vertex((math.cos(th) * rr, y, math.sin(th) * rr))
    for r in range(rng):
        for s in range(seg):
            sn = (s + 1) % seg
            m.add_face([idx[r][s], idx[r][sn], idx[r + 1][sn], idx[r + 1][s]])
    return m.calculate_normals()


def create_uv_sphere(radius: float = 1.0, segments: int = 32, rings: int = 16) -> Mesh:
    return create_sphere(radius=radius, segments=segments, rings=rings)


def create_icosphere(radius: float = 1.0, subdivisions: int = 1) -> Mesh:
    return create_sphere(radius=radius, segments=8 * (subdivisions + 1), rings=4 * (subdivisions + 1))


def create_cylinder(radius: float = 1.0, height: float = 2.0, segments: int = 16) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_cylinder"):
        return Mesh(_cpp_mesh=_core.create_cylinder(float(radius), float(height), int(segments)))
    m = create_sphere(radius=radius, segments=segments, rings=max(2, segments // 2))
    return m.scale(1.0, float(height) / (2.0 * max(radius, 1e-6)), 1.0)


def create_cone(radius: float = 1.0, height: float = 2.0, segments: int = 16) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_cone"):
        return Mesh(_cpp_mesh=_core.create_cone(float(radius), float(height), int(segments)))
    return create_cylinder(radius=radius, height=height, segments=segments).taper(-0.95, "Y")


def create_torus(main_radius: float = 1.0, tube_radius: float = 0.4, main_segments: int = 32, tube_segments: int = 16) -> Mesh:
    if CORE_AVAILABLE and hasattr(_core, "create_torus"):
        return Mesh(_cpp_mesh=_core.create_torus(float(main_radius), float(tube_radius), int(main_segments), int(tube_segments)))
    m = Mesh("Torus")
    ms = max(3, int(main_segments))
    ts = max(3, int(tube_segments))
    idx = [[0] * ts for _ in range(ms)]
    for i in range(ms):
        a = math.tau * i / ms
        for j in range(ts):
            b = math.tau * j / ts
            r = main_radius + math.cos(b) * tube_radius
            idx[i][j] = m.add_vertex((math.cos(a) * r, math.sin(b) * tube_radius, math.sin(a) * r))
    for i in range(ms):
        ni = (i + 1) % ms
        for j in range(ts):
            nj = (j + 1) % ts
            m.add_face([idx[i][j], idx[ni][j], idx[ni][nj], idx[i][nj]])
    return m.calculate_normals()
