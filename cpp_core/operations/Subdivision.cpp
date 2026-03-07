#include "Subdivision.h"
#include "FaceSplit.h"

void catmullClark(Mesh& mesh)
{
    std::vector<Face*> originalFaces = mesh.faces;

    for (Face* face : originalFaces)
    {
        splitFaceCenter(mesh, face);
    }

    mesh.buildTwins();
}