#include "Topology.h"

#include <unordered_map>
#include <vector>
#include <algorithm>

namespace ThreeDimensions::Topology {

using ThreeDimensions::Core::Mesh;
using ThreeDimensions::Math::Vec3;

static void buildVertexAdjacency(const Mesh& mesh, std::vector<std::vector<int>>& adj) {
    adj.clear();
    adj.resize(mesh.vertexCount());

    auto addUndirected = [&](int a, int b) {
        if (a == b) return;
        adj[a].push_back(b);
        adj[b].push_back(a);
    };

    for (const auto& f : mesh.faces) {
        const auto& idx = f.indices;
        if (idx.size() < 2) continue;
        for (size_t i = 0; i < idx.size(); ++i) {
            int a = idx[i];
            int b = idx[(i + 1) % idx.size()];
            if (a >= 0 && b >= 0 && a < mesh.vertexCount() && b < mesh.vertexCount()) {
                addUndirected(a, b);
            }
        }
    }

    // Deduplicate adjacency lists
    for (auto& n : adj) {
        std::sort(n.begin(), n.end());
        n.erase(std::unique(n.begin(), n.end()), n.end());
    }
}

void LaplacianSmooth(Mesh& mesh, int iterations, float strength) {
    iterations = std::max(0, iterations);
    strength = std::clamp(strength, 0.0f, 1.0f);
    if (iterations == 0 || strength == 0.0f || mesh.vertexCount() == 0) return;

    std::vector<std::vector<int>> adj;
    buildVertexAdjacency(mesh, adj);

    std::vector<Vec3> newPos(mesh.vertexCount());
    for (int it = 0; it < iterations; ++it) {
        for (int i = 0; i < mesh.vertexCount(); ++i) {
            const auto& nb = adj[i];
            if (nb.empty()) {
                newPos[i] = mesh.vertices[i].position;
                continue;
            }
            Vec3 avg(0, 0, 0);
            for (int j : nb) avg = avg + mesh.vertices[j].position;
            avg = avg * (1.0f / static_cast<float>(nb.size()));

            const Vec3 cur = mesh.vertices[i].position;
            newPos[i] = cur * (1.0f - strength) + avg * strength;
        }
        for (int i = 0; i < mesh.vertexCount(); ++i) mesh.vertices[i].position = newPos[i];
    }

    mesh.calculateNormals();
}

} // namespace ThreeDimensions::Topology

