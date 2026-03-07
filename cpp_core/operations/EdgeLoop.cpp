#include "EdgeLoop.h"

std::vector<HalfEdge*> collectEdgeLoop(HalfEdge* start)
{
    std::vector<HalfEdge*> loop;

    if (!start) return loop;

    HalfEdge* current = start;

    do {
        loop.push_back(current);

        if (!current->twin) break;
        current = current->twin->next;

    } while (current && current != start);

    return loop;
}