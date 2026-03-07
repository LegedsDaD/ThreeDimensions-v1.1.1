from .mesh import Mesh


class Sculpt:
    """Sculpt tools facade."""

    @staticmethod
    def brush(mesh: Mesh, brush: str, center, radius, strength=0.1, falloff="SMOOTH"):
        mesh.brush(brush, center, radius, strength, falloff)

    @staticmethod
    def inflate(mesh: Mesh, center, radius, strength):
        mesh.brush("inflate", center, radius, strength)

    @staticmethod
    def smooth(mesh: Mesh, center, radius, strength):
        mesh.brush("smooth", center, radius, strength)

    @staticmethod
    def mask(mesh: Mesh, center, radius, strength=0.5):
        mesh.mask_brush(center, radius, strength)
