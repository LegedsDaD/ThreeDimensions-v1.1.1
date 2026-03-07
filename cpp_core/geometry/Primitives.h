#pragma once

#include "../mesh/Mesh.h"
#include <memory>

namespace ThreeDimensions {
namespace Geometry {

class Primitives {
public:
    static std::unique_ptr<Core::Mesh> CreateCube(float size);
    static std::unique_ptr<Core::Mesh> CreateSphere(float radius, int segments, int rings);
    static std::unique_ptr<Core::Mesh> CreateCylinder(float radius, float height, int segments);
    static std::unique_ptr<Core::Mesh> CreateCone(float radius, float height, int segments);
    static std::unique_ptr<Core::Mesh> CreateTorus(float mainRadius, float tubeRadius, int mainSegments, int tubeSegments);
    static std::unique_ptr<Core::Mesh> CreatePlane(float size, int subdivisions);
};

}
}
