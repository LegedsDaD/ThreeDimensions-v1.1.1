#pragma once
#include "Modifier.h"

class SymmetryModifier : public Modifier {
public:
    char axis = 'x';   // 'x', 'y', or 'z'

    SymmetryModifier(char ax = 'x')
        : axis(ax) {
    }

    void apply(Mesh& mesh) override;
}; #pragma once
