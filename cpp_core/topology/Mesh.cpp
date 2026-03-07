#include "Mesh.h"
#include <map>

Vertex* Mesh::createVertex(const Vector3& pos) {
    Vertex* v = new Vertex(pos);
    vertices.push_back(v);
    return v;
}

Face* Mesh::createQuad(Vertex* v1, Vertex* v2, Vertex* v3, Vertex* v4) {

    Face* f = new Face();

    HalfEdge* e1 = new HalfEdge();
    HalfEdge* e2 = new HalfEdge();
    HalfEdge* e3 = new HalfEdge();
    HalfEdge* e4 = new HalfEdge();

    e1->vertex = v1;
    e2->vertex = v2;
    e3->vertex = v3;
    e4->vertex = v4;

    e1->next = e2; e2->next = e3;
    e3->next = e4; e4->next = e1;

    e1->prev = e4; e2->prev = e1;
    e3->prev = e2; e4->prev = e3;

    e1->face = e2->face = e3->face = e4->face = f;
    f->edge = e1;

    halfEdges.insert(halfEdges.end(), { e1,e2,e3,e4 });
    faces.push_back(f);

    return f;
}

void Mesh::buildTwins() {

    std::map<std::pair<Vertex*, Vertex*>, HalfEdge*> edgeMap;

    for (auto he : halfEdges) {
        Vertex* vStart = he->prev->vertex;
        Vertex* vEnd = he->vertex;
        edgeMap[{vStart, vEnd}] = he;
    }

    for (auto he : halfEdges) {
        Vertex* vStart = he->vertex;
        Vertex* vEnd = he->prev->vertex;

        auto it = edgeMap.find({ vStart, vEnd });
        if (it != edgeMap.end()) {
            he->twin = it->second;
        }
    }
}

void Mesh::clear() {
    for (auto v : vertices) delete v;
    for (auto e : halfEdges) delete e;
    for (auto f : faces) delete f;
    for (auto ed : edges) delete ed;
}