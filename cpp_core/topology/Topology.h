#pragma once

#include "../mesh/Mesh.h"

namespace ThreeDimensions::Topology {

void LaplacianSmooth(ThreeDimensions::Core::Mesh& mesh, int iterations = 1, float strength = 0.5f);

} // namespace ThreeDimensions::Topology

