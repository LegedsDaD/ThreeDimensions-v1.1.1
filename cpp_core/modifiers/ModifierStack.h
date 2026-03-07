#pragma once
#include <vector>
#include "Modifier.h"

class ModifierStack {
private:
    std::vector<Modifier*> modifiers;

public:
    void addModifier(Modifier* modifier);
    void removeModifier(int index);
    void applyAll(Mesh& mesh);

    int count() const;
}; #pragma once
