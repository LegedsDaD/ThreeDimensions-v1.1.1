#pragma once
#include "Vector3.h"
#include <array>

namespace ThreeDimensions {
namespace Math {

class Matrix4 {
public:
    std::array<float, 16> m;

    Matrix4() {
        m.fill(0);
        m[0] = m[5] = m[10] = m[15] = 1.0f;
    }

    static Matrix4 Identity() {
        return Matrix4();
    }

    static Matrix4 Translate(const Vec3& v) {
        Matrix4 mat;
        mat.m[12] = v.x;
        mat.m[13] = v.y;
        mat.m[14] = v.z;
        return mat;
    }
    
    // Simple multiplication
    Vec3 multiply(const Vec3& v) const {
        float x = v.x * m[0] + v.y * m[4] + v.z * m[8] + m[12];
        float y = v.x * m[1] + v.y * m[5] + v.z * m[9] + m[13];
        float z = v.x * m[2] + v.y * m[6] + v.z * m[10] + m[14];
        return Vec3(x, y, z);
    }
};

}
}
