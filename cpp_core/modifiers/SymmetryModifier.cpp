#include "SymmetryModifier.h"
#include "../math/Vector3.h"

using ThreeDimensions::Math::Vector3;

void SymmetryModifier::apply(Mesh& mesh)
{
    std::vector<Vertex*> original = mesh.vertices;

    for (auto v : original)
    {
        Vector3 mirrored = v->position;
        mirrored.x *= -1;

        mesh.createVertex(mirrored);
    }

    mesh.buildTwins();
}
