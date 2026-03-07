#pragma once
#include "../math/Vector3.h"

struct HalfEdge;

struct Vertex {
    Vector3 position;
    HalfEdge* edge = nullptr;

    Vertex(const Vector3& pos) : position(pos) {}
};
