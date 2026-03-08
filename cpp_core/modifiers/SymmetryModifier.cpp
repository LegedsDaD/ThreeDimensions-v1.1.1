#include "SymmetryModifier.h"

using ThreeDimensions::Math::Vec3;

void SymmetryModifier::apply(Mesh& mesh)
{
    size_t originalCount = mesh.vertices.size();

    for (size_t i = 0; i < originalCount; i++)
    {
        Vertex* v = mesh.vertices[i];
        Vec3 mirrored = v->position;

        if (axis == 'x') mirrored.x = -mirrored.x;
        if (axis == 'y') mirrored.y = -mirrored.y;
        if (axis == 'z') mirrored.z = -mirrored.z;

        mesh.createVertex(mirrored);
    }

    mesh.buildTwins();

}
