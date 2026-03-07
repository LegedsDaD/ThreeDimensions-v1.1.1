#include "BezierCurve.h"
#include <algorithm>

namespace ThreeDimensions::Curves {

static Vec3 lerp(const Vec3& a, const Vec3& b, float t) {
    return a * (1.0f - t) + (b * t);
}

Vec3 BezierCurve::evaluate(float t) const {
    if (controlPoints.empty()) return Vec3(0, 0, 0);
    if (controlPoints.size() == 1) return controlPoints[0];

    t = std::clamp(t, 0.0f, 1.0f);
    std::vector<Vec3> tmp = controlPoints;
    for (size_t k = tmp.size(); k > 1; --k) {
        for (size_t i = 0; i + 1 < k; ++i) {
            tmp[i] = lerp(tmp[i], tmp[i + 1], t);
        }
    }
    return tmp[0];
}

std::vector<Vec3> BezierCurve::sample(int segments) const {
    std::vector<Vec3> pts;
    if (segments < 1) segments = 1;
    pts.reserve(static_cast<size_t>(segments) + 1);
    for (int i = 0; i <= segments; ++i) {
        float t = static_cast<float>(i) / static_cast<float>(segments);
        pts.push_back(evaluate(t));
    }
    return pts;
}

} // namespace ThreeDimensions::Curves

