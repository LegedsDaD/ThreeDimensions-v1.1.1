#include "Extrude.h"
#include "../math/Vector3.h"
using ThreeDimensions::Math::Vec3;

void extrudeFace(Mesh& mesh, Face* face, double distance)
{
    if (!face || !face->edge) return;

    HalfEdge* start = face->edge;
    HalfEdge* he = start;

    std::vector<Vertex*> newVertices;

    // Duplicate vertices
    do {
        Vector3 newPos = he->vertex->position + Vector3(0, 0, distance);
        newVertices.push_back(mesh.createVertex(newPos));
        he = he->next;
    } while (he != start);

    // Create side faces
    he = start;
    int i = 0;

    do {
        Vertex* v1 = he->vertex;
        Vertex* v2 = he->next->vertex;

        Vertex* nv1 = newVertices[i];
        Vertex* nv2 = newVertices[(i + 1) % newVertices.size()];

        mesh.createQuad(v1, v2, nv2, nv1);

        he = he->next;
        i++;
    } while (he != start);

    mesh.buildTwins();

}


