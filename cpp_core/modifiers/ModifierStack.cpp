#include "ModifierStack.h"

void ModifierStack::addModifier(Modifier* modifier)
{
    modifiers.push_back(modifier);
}

void ModifierStack::removeModifier(int index)
{
    if (index < 0 || index >= modifiers.size())
        return;

    delete modifiers[index];
    modifiers.erase(modifiers.begin() + index);
}

void ModifierStack::applyAll(Mesh& mesh)
{
    for (Modifier* mod : modifiers)
    {
        if (mod && mod->enabled)
        {
            mod->apply(mesh);
        }
    }
}

int ModifierStack::count() const
{
    return (int)modifiers.size();
}