#include "BooleanModifier.h"
#include "../math/Vector3.h"

using ThreeDimensions::Math::Vec3;

void BooleanModifier::apply(Mesh& mesh)
{
    if (!enabled) return;

    for (auto* v : mesh.vertices)
    {
        for (auto* ov : mesh.vertices)
        {
            if (v == ov) continue;

            Vec3 diff = v->position - ov->position;

            if (diff.length() < 0.001f)
            {
                v->position = v->position + Vec3(0.05f, 0.05f, 0.05f);
            }
        }
    }
}
