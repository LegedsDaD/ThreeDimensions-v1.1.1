#include "CurveMeshing.h"
#include <cmath>
#include <algorithm>

namespace ThreeDimensions::Curves {

static Vec3 safeNormalize(Vec3 v) {
    float len = v.length();
    if (len <= 1e-12f) return Vec3(0, 0, 0);
    return v * (1.0f / len);
}

static Vec3 cross(const Vec3& a, const Vec3& b) { return a.cross(b); }

static int addVertex(ThreeDimensions::Core::Mesh& m, const Vec3& p) {
    m.addVertex(p);
    return static_cast<int>(m.vertices.size() - 1);
}

std::unique_ptr<ThreeDimensions::Core::Mesh> CreateTubeAlongPolyline(
    const std::vector<Vec3>& points,
    float radius,
    int radialSegments
) {
    auto mesh = std::make_unique<ThreeDimensions::Core::Mesh>("Tube");
    if (points.size() < 2) return mesh;
    if (radius <= 0.0f) radius = 0.01f;
    if (radialSegments < 3) radialSegments = 3;

    const int ringSize = radialSegments;
    const int rings = static_cast<int>(points.size());
    std::vector<int> ringStart(static_cast<size_t>(rings), 0);

    Vec3 up(0, 1, 0);

    for (int i = 0; i < rings; ++i) {
        Vec3 p = points[static_cast<size_t>(i)];
        Vec3 t;
        if (i == 0) t = points[1] - points[0];
        else if (i == rings - 1) t = points[static_cast<size_t>(rings - 1)] - points[static_cast<size_t>(rings - 2)];
        else t = points[static_cast<size_t>(i + 1)] - points[static_cast<size_t>(i - 1)];
        t = safeNormalize(t);

        // Choose a stable normal
        Vec3 n = cross(up, t);
        if (n.length() < 1e-6f) {
            up = Vec3(1, 0, 0);
            n = cross(up, t);
        }
        n = safeNormalize(n);
        Vec3 b = safeNormalize(cross(t, n));

        ringStart[static_cast<size_t>(i)] = static_cast<int>(mesh->vertices.size());
        for (int s = 0; s < ringSize; ++s) {
            float a = (static_cast<float>(s) / static_cast<float>(ringSize)) * 2.0f * 3.14159265359f;
            float ca = std::cos(a);
            float sa = std::sin(a);
            Vec3 off = (n * (radius * ca)) + (b * (radius * sa));
            addVertex(*mesh, p + off);
        }
    }

    // Side quads
    for (int r = 0; r < rings - 1; ++r) {
        int a0 = ringStart[static_cast<size_t>(r)];
        int b0 = ringStart[static_cast<size_t>(r + 1)];
        for (int s = 0; s < ringSize; ++s) {
            int s1 = (s + 1) % ringSize;
            int v00 = a0 + s;
            int v01 = a0 + s1;
            int v11 = b0 + s1;
            int v10 = b0 + s;
            mesh->addFace({v00, v01, v11, v10});
        }
    }

    // End caps (triangle fan)
    int startCenter = addVertex(*mesh, points.front());
    int endCenter = addVertex(*mesh, points.back());

    int startRing = ringStart.front();
    int endRing = ringStart.back();

    for (int s = 0; s < ringSize; ++s) {
        int s1 = (s + 1) % ringSize;
        // Start cap (reverse winding)
        mesh->addFace({startCenter, startRing + s1, startRing + s});
        // End cap
        mesh->addFace({endCenter, endRing + s, endRing + s1});
    }

    mesh->calculateNormals();
    return mesh;
}

std::unique_ptr<ThreeDimensions::Core::Mesh> CreateLathe(const std::vector<Vec3>& profile, int steps) {
    auto mesh = std::make_unique<ThreeDimensions::Core::Mesh>("Lathe");
    if (profile.size() < 2) return mesh;
    if (steps < 3) steps = 3;

    const int ringCount = steps + 1; // duplicate seam for simple indexing
    const int profCount = static_cast<int>(profile.size());

    // Build vertices
    for (int r = 0; r < ringCount; ++r) {
        float u = static_cast<float>(r) / static_cast<float>(steps);
        float ang = u * 2.0f * 3.14159265359f;
        float c = std::cos(ang);
        float s = std::sin(ang);

        for (int p = 0; p < profCount; ++p) {
            const Vec3& pr = profile[static_cast<size_t>(p)];
            float rad = pr.x;
            float y = pr.y;
            // revolve around Y: xz-plane
            addVertex(*mesh, Vec3(rad * c, y, rad * s));
        }
    }

    auto vid = [&](int r, int p) {
        return (r * profCount) + p;
    };

    // Build faces between rings
    for (int r = 0; r < steps; ++r) {
        for (int p = 0; p < profCount - 1; ++p) {
            int v00 = vid(r, p);
            int v01 = vid(r, p + 1);
            int v11 = vid(r + 1, p + 1);
            int v10 = vid(r + 1, p);
            mesh->addFace({v00, v01, v11, v10});
        }
    }

    mesh->calculateNormals();
    return mesh;
}

} // namespace ThreeDimensions::Curves

