#include "Mesh.h"
#include <cmath>
#include <algorithm>
#include <map>
#include <unordered_map>
#include <fstream>
#include <string>
#include <cctype>

namespace ThreeDimensions {
namespace Core {

Mesh::Mesh(const std::string& name) : name(name) {}

Mesh::~Mesh() {}

void Mesh::addVertex(const Vec3& position) {
    Vertex v;
    v.position = position;
    v.index = vertices.size();
    vertices.push_back(v);
}

void Mesh::addFace(const std::vector<int>& indices) {
    Face f;
    f.indices = indices;
    faces.push_back(f);
}

void Mesh::calculateNormals() {
    // Simple face normal calculation
    for (auto& face : faces) {
        if (face.indices.size() < 3) continue;
        
        const Vec3& v0 = vertices[face.indices[0]].position;
        const Vec3& v1 = vertices[face.indices[1]].position;
        const Vec3& v2 = vertices[face.indices[2]].position;
        
        Vec3 edge1 = v1 - v0;
        Vec3 edge2 = v2 - v0;
        
        face.normal = edge1.cross(edge2);
        face.normal.normalize();
    }
    
    // Vertex normals (averaging face normals)
    for (auto& v : vertices) {
        v.normal = Vec3(0, 0, 0);
    }
    
    for (const auto& face : faces) {
        for (int idx : face.indices) {
            vertices[idx].normal = vertices[idx].normal + face.normal;
        }
    }
    
    for (auto& v : vertices) {
        v.normal.normalize();
    }
}

void Mesh::clear() {
    vertices.clear();
    faces.clear();
}

// Transforms

void Mesh::translate(const Vec3& translation) {
    for (auto& v : vertices) {
        v.position = v.position + translation;
    }
}

void Mesh::scale(const Vec3& scaleFactor) {
    for (auto& v : vertices) {
        v.position.x *= scaleFactor.x;
        v.position.y *= scaleFactor.y;
        v.position.z *= scaleFactor.z;
    }
}

void Mesh::rotateX(float angle) {
    float c = std::cos(angle);
    float s = std::sin(angle);
    for (auto& v : vertices) {
        float y = v.position.y * c - v.position.z * s;
        float z = v.position.y * s + v.position.z * c;
        v.position.y = y;
        v.position.z = z;
    }
    calculateNormals();
}

void Mesh::rotateY(float angle) {
    float c = std::cos(angle);
    float s = std::sin(angle);
    for (auto& v : vertices) {
        float x = v.position.x * c + v.position.z * s;
        float z = -v.position.x * s + v.position.z * c;
        v.position.x = x;
        v.position.z = z;
    }
    calculateNormals();
}

void Mesh::rotateZ(float angle) {
    float c = std::cos(angle);
    float s = std::sin(angle);
    for (auto& v : vertices) {
        float x = v.position.x * c - v.position.y * s;
        float y = v.position.x * s + v.position.y * c;
        v.position.x = x;
        v.position.y = y;
    }
    calculateNormals();
}

// Basic Editing

void Mesh::extrudeFace(int faceIndex, float distance) {
    if (faceIndex < 0 || faceIndex >= faces.size()) return;

    // 1. Identify the face and its vertices
    Face& originalFace = faces[faceIndex];
    std::vector<int> originalIndices = originalFace.indices;
    std::vector<int> newIndices;

    // 2. Duplicate vertices
    for (int idx : originalIndices) {
        Vertex newV = vertices[idx]; // Copy
        newV.index = vertices.size();
        // Move new vertex along normal
        newV.position = newV.position + (originalFace.normal * distance);
        vertices.push_back(newV);
        newIndices.push_back(newV.index);
    }

    // 3. Create side faces (quads)
    int n = originalIndices.size();
    for (int i = 0; i < n; ++i) {
        int next = (i + 1) % n;
        
        int bottom1 = originalIndices[i];
        int bottom2 = originalIndices[next];
        int top1 = newIndices[i];
        int top2 = newIndices[next];

        // Create side quad. Winding order depends on normal direction.
        // Assuming original face normal points OUT.
        // Side face normal should also point OUT.
        addFace({bottom1, bottom2, top2, top1});
    }

    // 4. Update the original face to use new vertices (effectively moving the cap)
    // Actually, extrude usually leaves the hole behind. 
    // In this simple implementation, we just "move" the face by reassigning its indices to the new ones.
    // The "original" face geometry stays as the "floor" of the extrusion, but we often want to remove it 
    // if it's internal.
    // For a solid extrusion (like lengthening a cylinder), we want to KEEP the sides and MOVE the cap.
    // So the original face object becomes the top cap.
    
    originalFace.indices = newIndices;
    
    calculateNormals();
}

void Mesh::translateFace(int faceIndex, const Vec3& translation) {
    if (faceIndex < 0 || faceIndex >= faces.size()) return;
    
    Face& face = faces[faceIndex];
    for (int idx : face.indices) {
        vertices[idx].position = vertices[idx].position + translation;
    }
    calculateNormals(); // Recompute normals
}

void Mesh::scaleFace(int faceIndex, float scaleFactor) {
    if (faceIndex < 0 || faceIndex >= faces.size()) return;
    
    Face& face = faces[faceIndex];
    
    // Calculate center of face
    Vec3 center(0, 0, 0);
    for (int idx : face.indices) {
        center = center + vertices[idx].position;
    }
    center = center * (1.0f / face.indices.size());
    
    // Scale vertices relative to center
    for (int idx : face.indices) {
        Vec3 diff = vertices[idx].position - center;
        vertices[idx].position = center + (diff * scaleFactor);
    }
    calculateNormals();
}

void Mesh::join(const Mesh& other, const Vec3& offset) {
    int vertexOffset = vertices.size();
    
    // Copy vertices with offset
    for (const auto& v : other.vertices) {
        Vertex newV = v;
        newV.position = newV.position + offset;
        newV.index = vertices.size();
        vertices.push_back(newV);
    }
    
    // Copy faces with index offset
    for (const auto& f : other.faces) {
        Face newF = f;
        for (auto& idx : newF.indices) {
            idx += vertexOffset;
        }
        faces.push_back(newF);
    }
    calculateNormals();
}

void Mesh::joinFast(const Mesh& other, const Vec3& offset) {
    int vertexOffset = static_cast<int>(vertices.size());

    for (const auto& v : other.vertices) {
        Vertex newV = v;
        newV.position = newV.position + offset;
        newV.index = static_cast<int>(vertices.size());
        vertices.push_back(newV);
    }

    for (const auto& f : other.faces) {
        Face newF = f;
        for (auto& idx : newF.indices) idx += vertexOffset;
        faces.push_back(newF);
    }
}

Mesh Mesh::clone() const {
    Mesh out(name + "_copy");
    out.vertices = vertices;
    out.faces = faces;
    // Reindex vertices to match container ordering
    for (size_t i = 0; i < out.vertices.size(); ++i) {
        out.vertices[i].index = static_cast<int>(i);
    }
    return out;
}

void Mesh::mirror(const std::string& axis) {
    float sx = 1.0f, sy = 1.0f, sz = 1.0f;
    if (axis == "X" || axis == "x") sx = -1.0f;
    else if (axis == "Y" || axis == "y") sy = -1.0f;
    else if (axis == "Z" || axis == "z") sz = -1.0f;
    else return;

    for (auto& v : vertices) {
        v.position.x *= sx;
        v.position.y *= sy;
        v.position.z *= sz;
    }

    // Mirroring flips winding; reverse faces to keep outward normals consistent
    for (auto& f : faces) {
        std::reverse(f.indices.begin(), f.indices.end());
    }

    calculateNormals();
}

static int addVertexFromPos(std::vector<Vertex>& verts, const Vec3& p) {
    Vertex v;
    v.position = p;
    v.index = static_cast<int>(verts.size());
    verts.push_back(v);
    return v.index;
}

void Mesh::subdivide(int levels) {
    if (levels <= 0) return;
    for (int level = 0; level < levels; ++level) {
        if (faces.empty()) break;

        std::vector<Vertex> newVerts = vertices;
        std::vector<Face> newFaces;
        newFaces.reserve(faces.size() * 4);

        auto midpoint = [&](int ia, int ib) -> int {
            const Vec3& a = newVerts[ia].position;
            const Vec3& b = newVerts[ib].position;
            Vec3 m = (a + b) * 0.5f;
            return addVertexFromPos(newVerts, m);
        };

        for (const auto& f : faces) {
            if (f.indices.size() < 3) continue;

            if (f.indices.size() == 3) {
                int i0 = f.indices[0];
                int i1 = f.indices[1];
                int i2 = f.indices[2];

                int m01 = midpoint(i0, i1);
                int m12 = midpoint(i1, i2);
                int m20 = midpoint(i2, i0);

                newFaces.push_back(Face{{i0, m01, m20}, Vec3()});
                newFaces.push_back(Face{{m01, i1, m12}, Vec3()});
                newFaces.push_back(Face{{m20, m12, i2}, Vec3()});
                newFaces.push_back(Face{{m01, m12, m20}, Vec3()});
                continue;
            }

            if (f.indices.size() == 4) {
                int i0 = f.indices[0];
                int i1 = f.indices[1];
                int i2 = f.indices[2];
                int i3 = f.indices[3];

                int m01 = midpoint(i0, i1);
                int m12 = midpoint(i1, i2);
                int m23 = midpoint(i2, i3);
                int m30 = midpoint(i3, i0);

                Vec3 c = (newVerts[i0].position + newVerts[i1].position + newVerts[i2].position + newVerts[i3].position) * 0.25f;
                int ic = addVertexFromPos(newVerts, c);

                newFaces.push_back(Face{{i0, m01, ic, m30}, Vec3()});
                newFaces.push_back(Face{{m01, i1, m12, ic}, Vec3()});
                newFaces.push_back(Face{{ic, m12, i2, m23}, Vec3()});
                newFaces.push_back(Face{{m30, ic, m23, i3}, Vec3()});
                continue;
            }

            // N-gons: simple fan triangulation then subdivide triangles
            int i0 = f.indices[0];
            for (size_t i = 1; i + 1 < f.indices.size(); ++i) {
                int i1 = f.indices[i];
                int i2 = f.indices[i + 1];

                int m01 = midpoint(i0, i1);
                int m12 = midpoint(i1, i2);
                int m20 = midpoint(i2, i0);

                newFaces.push_back(Face{{i0, m01, m20}, Vec3()});
                newFaces.push_back(Face{{m01, i1, m12}, Vec3()});
                newFaces.push_back(Face{{m20, m12, i2}, Vec3()});
                newFaces.push_back(Face{{m01, m12, m20}, Vec3()});
            }
        }

        vertices.swap(newVerts);
        faces.swap(newFaces);

        for (size_t i = 0; i < vertices.size(); ++i) vertices[i].index = static_cast<int>(i);
        calculateNormals();
    }
}

void Mesh::inflate(const Vec3& center, float radius, float strength) {
    if (radius <= 0.0f || strength == 0.0f) return;
    calculateNormals();
    float r2 = radius * radius;
    for (auto& v : vertices) {
        float dx = v.position.x - center.x;
        float dy = v.position.y - center.y;
        float dz = v.position.z - center.z;
        float d2 = dx * dx + dy * dy + dz * dz;
        if (d2 > r2) continue;
        float d = std::sqrt(std::max(d2, 0.0f));
        float falloff = 1.0f - (d / radius);
        float factor = strength * falloff;
        v.position = v.position + (v.normal * factor);
    }
    calculateNormals();
}

void Mesh::smooth(const Vec3& center, float radius, float strength) {
    if (radius <= 0.0f) return;
    strength = std::clamp(strength, 0.0f, 1.0f);
    if (strength == 0.0f) return;

    // Adjacency-based smoothing (much faster than global radius search).
    float r2 = radius * radius;

    std::vector<std::vector<int>> adj(vertices.size());
    auto addEdge = [&](int a, int b) {
        if (a < 0 || b < 0) return;
        if (static_cast<size_t>(a) >= adj.size() || static_cast<size_t>(b) >= adj.size()) return;
        adj[static_cast<size_t>(a)].push_back(b);
        adj[static_cast<size_t>(b)].push_back(a);
    };

    for (const auto& f : faces) {
        const int n = static_cast<int>(f.indices.size());
        if (n < 2) continue;
        for (int i = 0; i < n; ++i) {
            int a = f.indices[static_cast<size_t>(i)];
            int b = f.indices[static_cast<size_t>((i + 1) % n)];
            addEdge(a, b);
        }
    }

    for (auto& nb : adj) {
        std::sort(nb.begin(), nb.end());
        nb.erase(std::unique(nb.begin(), nb.end()), nb.end());
    }

    std::vector<Vec3> base(vertices.size());
    std::vector<Vec3> newPos(vertices.size());
    for (size_t i = 0; i < vertices.size(); ++i) {
        base[i] = vertices[i].position;
        newPos[i] = vertices[i].position;
    }

    for (size_t i = 0; i < vertices.size(); ++i) {
        const Vec3& p = base[i];
        float dx = p.x - center.x;
        float dy = p.y - center.y;
        float dz = p.z - center.z;
        float d2 = dx * dx + dy * dy + dz * dz;
        if (d2 > r2) continue;

        const auto& nb = adj[i];
        if (nb.empty()) continue;

        Vec3 sum(0, 0, 0);
        for (int j : nb) sum = sum + base[static_cast<size_t>(j)];
        Vec3 avg = sum * (1.0f / static_cast<float>(nb.size()));

        float d = std::sqrt(std::max(d2, 0.0f));
        float falloff = 1.0f - (d / radius);
        float w = strength * falloff;

        newPos[i] = p + ((avg - p) * w);
    }

    for (size_t i = 0; i < vertices.size(); ++i) vertices[i].position = newPos[i];
    calculateNormals();
}

struct QuantKey {
    int x, y, z;
    bool operator==(const QuantKey& o) const { return x == o.x && y == o.y && z == o.z; }
};

struct QuantKeyHash {
    std::size_t operator()(const QuantKey& k) const noexcept {
        // Simple mixed hash
        std::size_t h = static_cast<std::size_t>(k.x) * 73856093u;
        h ^= static_cast<std::size_t>(k.y) * 19349663u;
        h ^= static_cast<std::size_t>(k.z) * 83492791u;
        return h;
    }
};

void Mesh::mergeDuplicateVertices(float tolerance) {
    if (vertices.empty()) return;
    if (tolerance <= 0.0f) tolerance = 1e-6f;

    const float inv = 1.0f / tolerance;
    std::unordered_map<QuantKey, int, QuantKeyHash> map;
    map.reserve(vertices.size());

    std::vector<int> remap(vertices.size(), -1);
    std::vector<Vertex> outVerts;
    outVerts.reserve(vertices.size());

    for (size_t i = 0; i < vertices.size(); ++i) {
        const auto& v = vertices[i];
        QuantKey key{
            static_cast<int>(std::lround(v.position.x * inv)),
            static_cast<int>(std::lround(v.position.y * inv)),
            static_cast<int>(std::lround(v.position.z * inv))
        };

        auto it = map.find(key);
        if (it == map.end()) {
            int newIndex = static_cast<int>(outVerts.size());
            Vertex nv = v;
            nv.index = newIndex;
            outVerts.push_back(nv);
            map.emplace(key, newIndex);
            remap[i] = newIndex;
        } else {
            remap[i] = it->second;
        }
    }

    if (outVerts.size() == vertices.size()) {
        // nothing merged
        return;
    }

    std::vector<Face> outFaces;
    outFaces.reserve(faces.size());

    for (auto f : faces) {
        std::vector<int> idx;
        idx.reserve(f.indices.size());
        for (int oldIdx : f.indices) {
            if (oldIdx < 0 || static_cast<size_t>(oldIdx) >= remap.size()) continue;
            idx.push_back(remap[static_cast<size_t>(oldIdx)]);
        }

        // Remove consecutive duplicates (can happen after remap)
        idx.erase(std::unique(idx.begin(), idx.end()), idx.end());

        // Drop degenerate faces (need at least 3 distinct vertices)
        if (idx.size() < 3) continue;
        {
            std::unordered_map<int, bool> seen;
            seen.reserve(idx.size());
            int distinct = 0;
            for (int v : idx) {
                if (seen.emplace(v, true).second) ++distinct;
            }
            if (distinct < 3) continue;
        }

        Face nf;
        nf.indices = std::move(idx);
        outFaces.push_back(nf);
    }

    vertices.swap(outVerts);
    faces.swap(outFaces);
    calculateNormals();
}

static std::string toLowerExt(const std::string& path) {
    auto dot = path.find_last_of('.');
    if (dot == std::string::npos) return "";
    std::string ext = path.substr(dot);
    for (auto& c : ext) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return ext;
}

void Mesh::save(const std::string& filepath) const {
    const std::string ext = toLowerExt(filepath);
    if (ext != ".obj" && ext != ".stl") {
        throw std::runtime_error("Unsupported export format: " + ext);
    }

    Mesh tmp = this->clone();
    tmp.calculateNormals();

    if (ext == ".obj") {
        std::ofstream f(filepath, std::ios::out);
        if (!f) throw std::runtime_error("Failed to open file for writing: " + filepath);

        f << "# ThreeDimensions OBJ Export: " << tmp.name << "\n";
        for (const auto& v : tmp.vertices) {
            f << "v " << v.position.x << " " << v.position.y << " " << v.position.z << "\n";
        }
        for (const auto& v : tmp.vertices) {
            f << "vn " << v.normal.x << " " << v.normal.y << " " << v.normal.z << "\n";
        }
        for (const auto& face : tmp.faces) {
            if (face.indices.size() < 3) continue;
            f << "f";
            for (int idx : face.indices) {
                const int objIdx = idx + 1; // 1-based
                f << " " << objIdx << "//" << objIdx;
            }
            f << "\n";
        }
        return;
    }

    std::ofstream f(filepath, std::ios::binary);
    if (!f) throw std::runtime_error("Failed to open file for writing: " + filepath);

    std::string header = "ThreeDimensions Export: " + tmp.name;
    header.resize(80, ' ');
    f.write(header.data(), 80);

    struct Tri {
        Vec3 n, a, b, c;
    };
    std::vector<Tri> tris;
    tris.reserve(static_cast<size_t>(tmp.faceCount()) * 2);

    for (const auto& face : tmp.faces) {
        const auto& idx = face.indices;
        if (idx.size() < 3) continue;
        const Vec3 n = face.normal;
        const Vec3 v0 = tmp.vertices[idx[0]].position;
        for (size_t i = 1; i + 1 < idx.size(); ++i) {
            const Vec3 v1 = tmp.vertices[idx[i]].position;
            const Vec3 v2 = tmp.vertices[idx[i + 1]].position;
            tris.push_back(Tri{n, v0, v1, v2});
        }
    }

    const uint32_t triCount = static_cast<uint32_t>(tris.size());
    f.write(reinterpret_cast<const char*>(&triCount), sizeof(uint32_t));

    for (const auto& t : tris) {
        f.write(reinterpret_cast<const char*>(&t.n.x), sizeof(float) * 3);
        f.write(reinterpret_cast<const char*>(&t.a.x), sizeof(float) * 3);
        f.write(reinterpret_cast<const char*>(&t.b.x), sizeof(float) * 3);
        f.write(reinterpret_cast<const char*>(&t.c.x), sizeof(float) * 3);
        const uint16_t attr = 0;
        f.write(reinterpret_cast<const char*>(&attr), sizeof(uint16_t));
    }
}

}
}
