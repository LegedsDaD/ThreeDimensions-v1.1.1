#pragma once
#include "../topology/Mesh.h"

class Modifier {
public:
    bool enabled = true;

    virtual void apply(Mesh& mesh) = 0;

    virtual ~Modifier() {}
}; #pragma once
