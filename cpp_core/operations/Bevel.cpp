#include "Bevel.h"

void bevelEdge(Mesh& mesh, Edge* edge, double width)
{
    if (!edge || !edge->halfEdge) return;

    HalfEdge* he = edge->halfEdge;
    HalfEdge* twin = he->twin;

    if (!twin) return;

    Vector3 dir = he->vertex->position - twin->vertex->position;
    Vector3 offset = dir * (width * 0.5);

    he->vertex->position = he->vertex->position + offset;
    twin->vertex->position = twin->vertex->position - offset;
}