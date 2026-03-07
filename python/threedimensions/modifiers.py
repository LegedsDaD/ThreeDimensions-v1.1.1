from abc import ABC, abstractmethod

from .mesh import Mesh, Vector3


class Modifier(ABC):
    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    @abstractmethod
    def apply(self, mesh: Mesh) -> Mesh:
        raise NotImplementedError


class SubdivisionModifier(Modifier):
    def __init__(self, levels: int = 1):
        super().__init__("Subdivision")
        self.levels = levels

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.subdivide(self.levels)
        return out


class MirrorModifier(Modifier):
    def __init__(self, axis: str = "X"):
        super().__init__("Mirror")
        self.axis = axis

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.mirror(self.axis)
        return out


class ArrayModifier(Modifier):
    def __init__(self, count: int = 2, offset=(1.0, 0.0, 0.0)):
        super().__init__("Array")
        self.count = count
        self.offset = offset

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.array(self.count, self.offset)
        return out


class SolidifyModifier(Modifier):
    def __init__(self, thickness: float = 0.05):
        super().__init__("Solidify")
        self.thickness = thickness

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.solidify(self.thickness)
        return out


class BooleanModifier(Modifier):
    def __init__(self, target: Mesh, operation: str = "UNION"):
        super().__init__("Boolean")
        self.target = target
        self.operation = operation

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.boolean(self.target, self.operation)
        return out


class DecimateModifier(Modifier):
    def __init__(self, ratio: float = 0.5):
        super().__init__("Decimate")
        self.ratio = ratio

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.decimate(self.ratio)
        return out


class LatticeModifier(Modifier):
    def __init__(self, factor: float = 0.25, axis: str = "Y"):
        super().__init__("Lattice")
        self.factor = factor
        self.axis = axis

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.taper(self.factor, self.axis)
        return out


class WeldModifier(Modifier):
    def __init__(self, tolerance: float = 1e-6):
        super().__init__("Weld")
        self.tolerance = tolerance

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        if self.enabled:
            out.merge_duplicate_vertices(self.tolerance)
        return out


class ModifierStack:
    def __init__(self):
        self.modifiers: list[Modifier] = []

    def add(self, modifier: Modifier):
        self.modifiers.append(modifier)
        return self

    def apply(self, mesh: Mesh) -> Mesh:
        out = mesh.clone()
        for modifier in self.modifiers:
            if modifier.enabled:
                out = modifier.apply(out)
        return out
