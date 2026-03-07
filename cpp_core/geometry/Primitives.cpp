#include "Primitives.h"

#include <cmath>
#include <numbers>

namespace ThreeDimensions::Geometry {

using ThreeDimensions::Core::Mesh;
using ThreeDimensions::Math::Vec3;

static int addVertex(Mesh& m, float x, float y, float z) {
    m.addVertex(Vec3(x, y, z));
    return static_cast<int>(m.vertices.size()) - 1;
}

std::unique_ptr<Mesh> Primitives::CreateCube(float size) {
    auto m = std::make_unique<Mesh>("Cube");
    const float s = size * 0.5f;

    const int v0 = addVertex(*m, -s, -s, -s);
    const int v1 = addVertex(*m,  s, -s, -s);
    const int v2 = addVertex(*m,  s,  s, -s);
    const int v3 = addVertex(*m, -s,  s, -s);
    const int v4 = addVertex(*m, -s, -s,  s);
    const int v5 = addVertex(*m,  s, -s,  s);
    const int v6 = addVertex(*m,  s,  s,  s);
    const int v7 = addVertex(*m, -s,  s,  s);

    m->addFace({v0, v1, v2, v3}); // bottom
    m->addFace({v4, v5, v6, v7}); // top
    m->addFace({v0, v1, v5, v4});
    m->addFace({v1, v2, v6, v5});
    m->addFace({v2, v3, v7, v6});
    m->addFace({v3, v0, v4, v7});

    m->calculateNormals();
    return m;
}

std::unique_ptr<Mesh> Primitives::CreatePlane(float size, int subdivisions) {
    auto m = std::make_unique<Mesh>("Plane");
    subdivisions = std::max(1, subdivisions);

    const float half = size * 0.5f;
    const int steps = subdivisions;
    const float step = size / static_cast<float>(steps);

    // Grid of vertices
    std::vector<int> vidx;
    vidx.resize((steps + 1) * (steps + 1));

    for (int y = 0; y <= steps; ++y) {
        for (int x = 0; x <= steps; ++x) {
            float px = -half + x * step;
            float py = 0.0f;
            float pz = -half + y * step;
            vidx[y * (steps + 1) + x] = addVertex(*m, px, py, pz);
        }
    }

    // Quads
    for (int y = 0; y < steps; ++y) {
        for (int x = 0; x < steps; ++x) {
            int a = vidx[y * (steps + 1) + x];
            int b = vidx[y * (steps + 1) + (x + 1)];
            int c = vidx[(y + 1) * (steps + 1) + (x + 1)];
            int d = vidx[(y + 1) * (steps + 1) + x];
            m->addFace({a, b, c, d});
        }
    }

    m->calculateNormals();
    return m;
}

std::unique_ptr<Mesh> Primitives::CreateSphere(float radius, int segments, int rings) {
    auto m = std::make_unique<Mesh>("Sphere");
    segments = std::max(3, segments);
    rings = std::max(2, rings);

    const float pi = static_cast<float>(std::numbers::pi_v<double>);

    // vertices (lat-long)
    std::vector<std::vector<int>> v(rings + 1, std::vector<int>(segments));

    for (int r = 0; r <= rings; ++r) {
        float t = static_cast<float>(r) / static_cast<float>(rings); // 0..1
        float phi = t * pi;                                          // 0..pi
        float y = std::cos(phi) * radius;
        float rr = std::sin(phi) * radius;
        for (int s = 0; s < segments; ++s) {
            float u = static_cast<float>(s) / static_cast<float>(segments); // 0..1
            float theta = u * 2.0f * pi;
            float x = std::cos(theta) * rr;
            float z = std::sin(theta) * rr;
            v[r][s] = addVertex(*m, x, y, z);
        }
    }

    // faces (quads between rings; triangles at poles are represented as degenerate quads here)
    for (int r = 0; r < rings; ++r) {
        for (int s = 0; s < segments; ++s) {
            int s1 = (s + 1) % segments;
            int a = v[r][s];
            int b = v[r][s1];
            int c = v[r + 1][s1];
            int d = v[r + 1][s];
            m->addFace({a, b, c, d});
        }
    }

    m->calculateNormals();
    return m;
}

std::unique_ptr<Mesh> Primitives::CreateCylinder(float radius, float height, int segments) {
    auto m = std::make_unique<Mesh>("Cylinder");
    segments = std::max(3, segments);
    const float pi = static_cast<float>(std::numbers::pi_v<double>);
    const float half = height * 0.5f;

    std::vector<int> bottom(segments), top(segments);
    for (int i = 0; i < segments; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(segments);
        float a = t * 2.0f * pi;
        float x = std::cos(a) * radius;
        float z = std::sin(a) * radius;
        bottom[i] = addVertex(*m, x, -half, z);
        top[i] = addVertex(*m, x, half, z);
    }

    // sides
    for (int i = 0; i < segments; ++i) {
        int n = (i + 1) % segments;
        m->addFace({bottom[i], bottom[n], top[n], top[i]});
    }

    // caps as n-gons
    std::vector<int> capB, capT;
    capB.reserve(segments);
    capT.reserve(segments);
    for (int i = 0; i < segments; ++i) {
        capB.push_back(bottom[segments - 1 - i]); // reverse for outward normals
        capT.push_back(top[i]);
    }
    m->addFace(capB);
    m->addFace(capT);

    m->calculateNormals();
    return m;
}

std::unique_ptr<Mesh> Primitives::CreateCone(float radius, float height, int segments) {
    auto m = std::make_unique<Mesh>("Cone");
    segments = std::max(3, segments);
    const float pi = static_cast<float>(std::numbers::pi_v<double>);
    const float half = height * 0.5f;

    const int tip = addVertex(*m, 0.0f, half, 0.0f);
    std::vector<int> base(segments);
    for (int i = 0; i < segments; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(segments);
        float a = t * 2.0f * pi;
        float x = std::cos(a) * radius;
        float z = std::sin(a) * radius;
        base[i] = addVertex(*m, x, -half, z);
    }

    // sides as triangles (stored as 3-index faces)
    for (int i = 0; i < segments; ++i) {
        int n = (i + 1) % segments;
        m->addFace({base[i], base[n], tip});
    }

    // base cap
    std::vector<int> capB;
    capB.reserve(segments);
    for (int i = 0; i < segments; ++i) capB.push_back(base[segments - 1 - i]);
    m->addFace(capB);

    m->calculateNormals();
    return m;
}

std::unique_ptr<Mesh> Primitives::CreateTorus(float mainRadius, float tubeRadius, int mainSegments, int tubeSegments) {
    auto m = std::make_unique<Mesh>("Torus");
    mainSegments = std::max(3, mainSegments);
    tubeSegments = std::max(3, tubeSegments);

    const float pi = static_cast<float>(std::numbers::pi_v<double>);

    std::vector<std::vector<int>> v(mainSegments, std::vector<int>(tubeSegments));
    for (int i = 0; i < mainSegments; ++i) {
        float u = static_cast<float>(i) / static_cast<float>(mainSegments);
        float a = u * 2.0f * pi;
        float cx = std::cos(a) * mainRadius;
        float cz = std::sin(a) * mainRadius;
        float tx = std::cos(a);
        float tz = std::sin(a);

        for (int j = 0; j < tubeSegments; ++j) {
            float v0 = static_cast<float>(j) / static_cast<float>(tubeSegments);
            float b = v0 * 2.0f * pi;
            float r = mainRadius + std::cos(b) * tubeRadius;
            float x = std::cos(a) * r;
            float y = std::sin(b) * tubeRadius;
            float z = std::sin(a) * r;
            (void)cx; (void)cz; (void)tx; (void)tz;
            v[i][j] = addVertex(*m, x, y, z);
        }
    }

    for (int i = 0; i < mainSegments; ++i) {
        int in = (i + 1) % mainSegments;
        for (int j = 0; j < tubeSegments; ++j) {
            int jn = (j + 1) % tubeSegments;
            int a = v[i][j];
            int b = v[in][j];
            int c = v[in][jn];
            int d = v[i][jn];
            m->addFace({a, b, c, d});
        }
    }

    m->calculateNormals();
    return m;
}

} // namespace ThreeDimensions::Geometry