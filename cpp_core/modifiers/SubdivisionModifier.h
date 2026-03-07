#pragma once
#include "Modifier.h"

class SubdivisionModifier : public Modifier {
public:
    int levels = 1;

    SubdivisionModifier(int lvl = 1)
        : levels(lvl) {
    }

    void apply(Mesh& mesh) override;
}; #pragma once
