#pragma once
#include "Modifier.h"

class BooleanModifier : public Modifier {
public:
    Mesh* operand = nullptr;

    BooleanModifier(Mesh* otherMesh)
        : operand(otherMesh) {
    }

    void apply(Mesh& mesh) override;
};

