#pragma once

#include "../mesh/Mesh.h"

namespace ThreeDimensions::Sculpt {

using Vec3 = ThreeDimensions::Math::Vec3;

void Inflate(ThreeDimensions::Core::Mesh& mesh, const Vec3& center, float radius, float strength);
void Smooth(ThreeDimensions::Core::Mesh& mesh, const Vec3& center, float radius, float strength);

} // namespace ThreeDimensions::Sculpt

