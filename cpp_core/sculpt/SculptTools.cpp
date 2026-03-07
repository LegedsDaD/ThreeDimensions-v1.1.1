#include "SculptTools.h"
#include <cmath>

static double distance(const Vector3& a, const Vector3& b)
{
    Vector3 d = a - b;
    return std::sqrt(d.x * d.x + d.y * d.y + d.z * d.z);
}

/*
========================================
GRAB BRUSH
Moves vertices inside radius toward offset
========================================
*/
void grabBrush(Mesh& mesh,
    const Vector3& center,
    const Vector3& offset,
    double radius)
{
    for (Vertex* v : mesh.vertices)
    {
        double dist = distance(v->position, center);

        if (dist < radius)
        {
            double falloff = 1.0 - (dist / radius);
            v->position = v->position + offset * falloff;
        }
    }
}

/*
========================================
INFLATE BRUSH
Pushes vertices outward from center
========================================
*/
void inflateBrush(Mesh& mesh,
    const Vector3& center,
    double strength,
    double radius)
{
    for (Vertex* v : mesh.vertices)
    {
        double dist = distance(v->position, center);

        if (dist < radius)
        {
            Vector3 dir = v->position - center;
            double len = std::sqrt(dir.x * dir.x + dir.y * dir.y + dir.z * dir.z);

            if (len > 0.0001)
            {
                dir = dir / len;

                double falloff = 1.0 - (dist / radius);
                v->position = v->position + dir * strength * falloff;
            }
        }
    }
}

/*
========================================
SMOOTH BRUSH
Averages neighbor positions using half-edge
========================================
*/
void smoothBrush(Mesh& mesh,
    double strength)
{
    std::vector<Vector3> newPositions;
    newPositions.reserve(mesh.vertices.size());

    for (Vertex* v : mesh.vertices)
    {
        if (!v->edge)
        {
            newPositions.push_back(v->position);
            continue;
        }

        Vector3 avg(0, 0, 0);
        int count = 0;

        HalfEdge* start = v->edge;
        HalfEdge* he = start;

        do {
            avg = avg + he->vertex->position;
            count++;

            if (!he->twin) break;
            he = he->twin->next;

        } while (he && he != start);

        if (count > 0)
            avg = avg / (double)count;

        Vector3 blended =
            v->position * (1.0 - strength) +
            avg * strength;

        newPositions.push_back(blended);
    }

    for (size_t i = 0; i < mesh.vertices.size(); i++)
    {
        mesh.vertices[i]->position = newPositions[i];
    }
}

// Python-facing helpers referenced by bindings.cpp.
// These forward to the already-implemented Core::Mesh methods.
namespace ThreeDimensions::Sculpt {

void Inflate(ThreeDimensions::Core::Mesh& mesh, const Vec3& center, float radius, float strength) {
    mesh.inflate(center, radius, strength);
}

void Smooth(ThreeDimensions::Core::Mesh& mesh, const Vec3& center, float radius, float strength) {
    mesh.smooth(center, radius, strength);
}

} // namespace ThreeDimensions::Sculpt