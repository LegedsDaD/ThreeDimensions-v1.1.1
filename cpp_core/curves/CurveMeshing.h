#pragma once

#include <memory>
#include <vector>
#include "../mesh/Mesh.h"

namespace ThreeDimensions::Curves {

using Vec3 = ThreeDimensions::Math::Vec3;

// Create a tube mesh along a polyline (watertight with end caps).
std::unique_ptr<ThreeDimensions::Core::Mesh> CreateTubeAlongPolyline(
    const std::vector<Vec3>& points,
    float radius = 0.05f,
    int radialSegments = 12
);

// Revolve a 2D profile around Y axis (x=radius, y=height).
// `profile` should be ordered along Y.
std::unique_ptr<ThreeDimensions::Core::Mesh> CreateLathe(
    const std::vector<Vec3>& profile,
    int steps = 32
);

} // namespace ThreeDimensions::Curves

