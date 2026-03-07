import math


class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x,
                       self.y + other.y,
                       self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x,
                       self.y - other.y,
                       self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar,
                       self.y * scalar,
                       self.z * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3()
        return Vector3(self.x/l, self.y/l, self.z/l)

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"


class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def add_vertex(self, v):
        self.vertices.append(v)

    def add_face(self, indices):
        self.faces.append(indices)

    def translate(self, offset):
        for v in self.vertices:
            v.x += offset.x
            v.y += offset.y
            v.z += offset.z

    def scale(self, factor):
        for v in self.vertices:
            v.x *= factor
            v.y *= factor
            v.z *= factor

    def extrude_face(self, face_index, distance):
        if face_index >= len(self.faces):
            return

        face = self.faces[face_index]
        direction = Vector3(0, 1, 0)

        new_indices = []
        for idx in face:
            orig = self.vertices[idx]
            new_v = orig + direction * distance
            self.add_vertex(new_v)
            new_indices.append(len(self.vertices) - 1)

        self.faces.append(new_indices)

    def save(self, filepath: str):
        ext = filepath.lower().split(".")[-1] if "." in filepath else ""
        if ext == "obj":
            # Minimal OBJ (positions + faces)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# ThreeDimensions OBJ Export (Python fallback)\n")
                for v in self.vertices:
                    f.write(f"v {v.x:.6f} {v.y:.6f} {v.z:.6f}\n")
                for face in self.faces:
                    if len(face) < 3:
                        continue
                    indices = [str(i + 1) for i in face]  # 1-based
                    f.write("f " + " ".join(indices) + "\n")
            return
        raise ValueError(f"Unsupported export format for fallback Mesh: {filepath}")
