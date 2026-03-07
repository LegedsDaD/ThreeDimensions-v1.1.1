#include "SymmetryModifier.h"

void SymmetryModifier::apply(Mesh& mesh)
{
    size_t originalCount = mesh.vertices.size();

    for (size_t i = 0; i < originalCount; i++)
    {
        Vertex* v = mesh.vertices[i];
        Vector3 mirrored = v->position;

        if (axis == 'x') mirrored.x = -mirrored.x;
        if (axis == 'y') mirrored.y = -mirrored.y;
        if (axis == 'z') mirrored.z = -mirrored.z;

        mesh.createVertex(mirrored);
    }

    mesh.buildTwins();
}