#include "FaceSplit.h"

void splitFaceCenter(Mesh& mesh, Face* face)
{
    if (!face || !face->edge) return;

    HalfEdge* start = face->edge;
    HalfEdge* he = start;

    Vector3 center(0, 0, 0);
    int count = 0;

    // Compute centroid
    do {
        center = center + he->vertex->position;
        count++;
        he = he->next;
    } while (he != start);

    center = center / (double)count;

    Vertex* centerVertex = mesh.createVertex(center);

    // Create triangles from each edge to center
    he = start;

    do {
        Vertex* v1 = he->prev->vertex;
        Vertex* v2 = he->vertex;

        mesh.createQuad(v1, v2, centerVertex, centerVertex);

        he = he->next;
    } while (he != start);
}