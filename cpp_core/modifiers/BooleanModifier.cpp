#include "BooleanModifier.h"

using ThreeDimensions::Math::Vec3;

void BooleanModifier::apply(Mesh& mesh)
{
    if (!operand) return;

    // Placeholder for topology-aware boolean.
    // Real implementation would:
    // 1. Detect face intersections
    // 2. Split edges at intersection points
    // 3. Rebuild topology
    // 4. Remove interior faces

    for (Vertex* v : mesh.vertices)
    {
        for (Vertex* ov : operand->vertices)
        {
            Vector3 diff = v->position - ov->position;

            if (diff.x * diff.x + diff.y * diff.y + diff.z * diff.z < 0.01)
            {
                v->position = v->position + Vector3(0.05, 0.05, 0.05);
            }
        }
    }

}
