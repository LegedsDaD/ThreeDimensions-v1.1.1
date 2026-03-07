#pragma once

#include <cmath>
#include <iostream>

namespace ThreeDimensions {
namespace Math {

template <typename T>
class Vector3 {
public:
    T x, y, z;

    Vector3() : x(0), y(0), z(0) {}
    Vector3(T x, T y, T z) : x(x), y(y), z(z) {}

    Vector3 operator+(const Vector3& other) const {
        return Vector3(x + other.x, y + other.y, z + other.z);
    }

    Vector3 operator-(const Vector3& other) const {
        return Vector3(x - other.x, y - other.y, z - other.z);
    }

    Vector3 operator*(T scalar) const {
        return Vector3(x * scalar, y * scalar, z * scalar);
    }

    T dot(const Vector3& other) const {
        return x * other.x + y * other.y + z * other.z;
    }

    Vector3 cross(const Vector3& other) const {
        return Vector3(
            y * other.z - z * other.y,
            z * other.x - x * other.z,
            x * other.y - y * other.x
        );
    }

    T length() const {
        return std::sqrt(x * x + y * y + z * z);
    }

    void normalize() {
        T len = length();
        if (len > 0) {
            x /= len;
            y /= len;
            z /= len;
        }
    }
};

using Vec3 = Vector3<float>;
using Vec3d = Vector3<double>;

}
}
