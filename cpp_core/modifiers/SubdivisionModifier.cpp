#include "SubdivisionModifier.h"
#include "../operations/Subdivision.h"

void SubdivisionModifier::apply(Mesh& mesh)
{
    for (int i = 0; i < levels; i++)
    {
        catmullClark(mesh);
    }
}