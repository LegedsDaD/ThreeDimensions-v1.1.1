#pragma once

#include <vector>
#include "../math/Vector3.h"

namespace ThreeDimensions::Curves {

using Vec3 = ThreeDimensions::Math::Vec3;

class BezierCurve {
public:
    std::vector<Vec3> controlPoints;

    BezierCurve() = default;
    explicit BezierCurve(const std::vector<Vec3>& points) : controlPoints(points) {}

    Vec3 evaluate(float t) const;
    std::vector<Vec3> sample(int segments) const;
};

} // namespace ThreeDimensions::Curves

