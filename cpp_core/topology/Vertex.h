#pragma once
#include "../math/Vector3.h"

using ThreeDimensions::Math::Vec3;

struct HalfEdge;

struct Vertex {
    Vec3 position;
    HalfEdge* edge = nullptr;

    Vertex(const Vec3& pos) : position(pos) {}
};
