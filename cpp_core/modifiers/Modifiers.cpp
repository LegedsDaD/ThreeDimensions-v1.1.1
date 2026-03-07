#include "Modifiers.h"

namespace ThreeDimensions::Modifiers {

Mesh ApplySubdivision(const Mesh& mesh, int levels) {
    Mesh out = mesh.clone();
    out.subdivide(levels);
    return out;
}

Mesh ApplyMirror(const Mesh& mesh, const std::string& axis) {
    Mesh out = mesh.clone();
    out.mirror(axis);
    return out;
}

Mesh ApplyArray(const Mesh& mesh, int count, const Vec3& offset) {
    if (count <= 1) return mesh.clone();
    Mesh out = mesh.clone();
    Mesh base = mesh.clone();
    for (int i = 1; i < count; ++i) {
        Mesh copy = base.clone();
        out.joinFast(copy, Vec3(offset.x * i, offset.y * i, offset.z * i));
    }
    out.calculateNormals();
    return out;
}

Mesh ApplyWeld(const Mesh& mesh, float tolerance) {
    Mesh out = mesh.clone();
    out.mergeDuplicateVertices(tolerance);
    return out;
}

} // namespace ThreeDimensions::Modifiers

