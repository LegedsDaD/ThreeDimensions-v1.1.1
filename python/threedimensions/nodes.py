from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class Node:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    inputs: List["Node"] = field(default_factory=list)


class NodeGraph:
    """Python-constructed geometry node graph evaluated through mesh operations."""

    def __init__(self):
        self._nodes: List[Node] = []
        self._connections: List[Tuple[Node, Node]] = []

    def node(self, type: str, **params: Any) -> Node:
        n = Node(type=type, params=dict(params))
        self._nodes.append(n)
        return n

    def connect(self, a: Node, b: Node) -> None:
        b.inputs.append(a)
        self._connections.append((a, b))

    def _primitive(self, td, t: str, params: Dict[str, Any]):
        m = {
            "cube": td.create_cube,
            "sphere": td.create_sphere,
            "uvsphere": td.create_uv_sphere,
            "icosphere": td.create_icosphere,
            "cylinder": td.create_cylinder,
            "cone": td.create_cone,
            "torus": td.create_torus,
            "plane": td.create_plane,
            "grid": td.create_grid,
        }
        if t in m:
            return m[t](**params)
        return None

    def evaluate(self):
        import threedimensions as td

        if not self._nodes:
            raise ValueError("Cannot evaluate an empty graph")

        cache: Dict[int, Any] = {}

        def eval_node(n: Node):
            key = id(n)
            if key in cache:
                return cache[key]

            t = n.type.lower().replace(" ", "")
            prim = self._primitive(td, t, n.params)
            if prim is not None:
                cache[key] = prim
                return prim

            ins = [eval_node(i) for i in n.inputs]
            if not ins:
                raise ValueError(f"Node '{n.type}' requires an input mesh")
            mesh = ins[-1]

            if t in ("move", "translate"):
                mesh.move(n.params.get("delta", (n.params.get("x", 0.0), n.params.get("y", 0.0), n.params.get("z", 0.0))))
            elif t in ("rotate",):
                mesh.rotate(float(n.params.get("angle", 0.0)), axis=str(n.params.get("axis", "Z")))
            elif t in ("scale",):
                mesh.scale(n.params.get("factor", n.params.get("value", 1.0)))
            elif t in ("subdivision", "subdivide", "subdivisionsurface"):
                mesh.subdivide(int(n.params.get("levels", n.params.get("level", 1))))
            elif t in ("extrude", "extrudeface"):
                mesh.extrude(distance=float(n.params.get("distance", 0.1)), face_indices=n.params.get("faces"))
            elif t in ("bevel",):
                mesh.bevel(float(n.params.get("width", 0.05)), int(n.params.get("segments", 1)))
            elif t in ("boolean",):
                op = str(n.params.get("operation", "UNION"))
                if len(ins) > 1:
                    mesh.boolean(ins[-2], op)
            elif t in ("mirror",):
                mesh.mirror(str(n.params.get("axis", "X")))
            elif t in ("solidify",):
                mesh.solidify(float(n.params.get("thickness", 0.05)))
            elif t in ("decimate",):
                mesh.decimate(float(n.params.get("ratio", 0.5)))
            elif t in ("sculpt", "brush"):
                mesh.brush(
                    str(n.params.get("brush", "inflate")),
                    n.params.get("center", (0.0, 0.0, 0.0)),
                    float(n.params.get("radius", 1.0)),
                    float(n.params.get("strength", 0.1)),
                )
            else:
                raise ValueError(f"Unknown node type: {n.type}")

            cache[key] = mesh
            return mesh

        return eval_node(self._nodes[-1])
