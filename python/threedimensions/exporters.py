from .mesh import Mesh
import struct


def _face_indices(face):
    return list(face.indices) if hasattr(face, "indices") else list(face)


def _pos(v):
    return v.position if hasattr(v, "position") else v


def _normal(v):
    if hasattr(v, "normal"):
        return v.normal
    return type(_pos(v))(0.0, 1.0, 0.0)


class Exporter:
    @staticmethod
    def export_obj(mesh: Mesh, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# ThreeDimensions OBJ Export: {getattr(mesh, 'name', 'Mesh')}\n")
            for v in mesh.vertices:
                p = _pos(v)
                f.write(f"v {p.x:.6f} {p.y:.6f} {p.z:.6f}\n")
            for v in mesh.vertices:
                n = _normal(v)
                f.write(f"vn {n.x:.6f} {n.y:.6f} {n.z:.6f}\n")
            for face in mesh.faces:
                idx = _face_indices(face)
                if len(idx) < 3:
                    continue
                parts = [f"{i + 1}//{i + 1}" for i in idx]
                f.write("f " + " ".join(parts) + "\n")

    @staticmethod
    def export_stl(mesh: Mesh, filepath: str):
        with open(filepath, "wb") as f:
            header = f"ThreeDimensions Export: {getattr(mesh, 'name', 'Mesh')}".ljust(80, " ")
            f.write(header.encode("ascii"))
            triangles = []
            for face in mesh.faces:
                idx = _face_indices(face)
                if len(idx) < 3:
                    continue
                v0 = _pos(mesh.vertices[idx[0]])
                for i in range(1, len(idx) - 1):
                    v1 = _pos(mesh.vertices[idx[i]])
                    v2 = _pos(mesh.vertices[idx[i + 1]])
                    triangles.append(((0.0, 0.0, 1.0), v0, v1, v2))
            f.write(struct.pack("<I", len(triangles)))
            for n, v0, v1, v2 in triangles:
                f.write(struct.pack("<3f", *n))
                f.write(struct.pack("<3f", v0.x, v0.y, v0.z))
                f.write(struct.pack("<3f", v1.x, v1.y, v1.z))
                f.write(struct.pack("<3f", v2.x, v2.y, v2.z))
                f.write(struct.pack("<H", 0))


class Importer:
    pass
