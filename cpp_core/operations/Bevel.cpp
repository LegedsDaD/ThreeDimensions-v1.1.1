#include "Bevel.h"

using ThreeDimensions::Math::Vec3;

void bevelEdge(Mesh& mesh, Edge* edge, double width)
{
    if (!edge || !edge->halfEdge) return;

    HalfEdge* he = edge->halfEdge;
    HalfEdge* twin = he->twin;

    if (!twin) return;

    Vec3 dir = he->vertex->position - twin->vertex->position;
    Vec3 offset = dir * (width * 0.5);

    he->vertex->position = he->vertex->position + offset;
    twin->vertex->position = twin->vertex->position - offset;

}
