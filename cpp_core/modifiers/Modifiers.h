#pragma once

#include "../mesh/Mesh.h"
#include "../math/Vector3.h"

namespace ThreeDimensions::Modifiers {

using ThreeDimensions::Core::Mesh;
using ThreeDimensions::Math::Vec3;

Mesh ApplySubdivision(const Mesh& mesh, int levels = 1);
Mesh ApplyMirror(const Mesh& mesh, const std::string& axis);
Mesh ApplyArray(const Mesh& mesh, int count, const Vec3& offset);
Mesh ApplyWeld(const Mesh& mesh, float tolerance = 1e-6f);

} // namespace ThreeDimensions::Modifiers

