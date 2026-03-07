#pragma once
#include <vector>
#include "Vertex.h"
#include "HalfEdge.h"
#include "Face.h"
#include "Edge.h"

class Mesh {
public:
    std::vector<Vertex*> vertices;
    std::vector<HalfEdge*> halfEdges;
    std::vector<Face*> faces;
    std::vector<Edge*> edges;

    Vertex* createVertex(const Vector3& pos);
    Face* createQuad(Vertex* v1, Vertex* v2, Vertex* v3, Vertex* v4);

    void buildTwins();
    void clear();
};
