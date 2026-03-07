#pragma once

#include <vector>
#include <string>
#include <memory>
#include "../math/Vector3.h"

namespace ThreeDimensions {
namespace Core {

using Vec3 = ThreeDimensions::Math::Vec3;

struct Vertex {
    Vec3 position;
    Vec3 normal;
    Vec3 uv;
    int index;
};

struct Face {
    std::vector<int> indices;
    Vec3 normal;
};

class Mesh {
public:
    std::string name;
    std::vector<Vertex> vertices;
    std::vector<Face> faces;

    Mesh(const std::string& name = "Mesh");
    ~Mesh();

    void addVertex(const Vec3& position);
    void addFace(const std::vector<int>& indices);
    
    void calculateNormals();
    void clear();
    
    // Transforms
    void translate(const Vec3& translation);
    void scale(const Vec3& scaleFactor);
    void rotateX(float angle);
    void rotateY(float angle);
    void rotateZ(float angle);
    
    // Basic Editing
    void extrudeFace(int faceIndex, float distance);
    void scaleFace(int faceIndex, float scaleFactor);
    void translateFace(int faceIndex, const Vec3& translation);
    
    // Combination
    void join(const Mesh& other, const Vec3& offset);
    void joinFast(const Mesh& other, const Vec3& offset);

    // Modifiers
    void subdivide(int levels = 1);
    void mirror(const std::string& axis);
    Mesh clone() const;

    // Sculpt
    void inflate(const Vec3& center, float radius, float strength);
    void smooth(const Vec3& center, float radius, float strength);

    // Topology
    void mergeDuplicateVertices(float tolerance = 1e-6f);

    // IO
    void save(const std::string& filepath) const;

    // Topology helpers
    int vertexCount() const { return vertices.size(); }
    int faceCount() const { return faces.size(); }
};

}
}
