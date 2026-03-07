#pragma once

struct Vertex;
struct Face;
struct Edge;

struct HalfEdge {
    Vertex* vertex = nullptr;
    HalfEdge* next = nullptr;
    HalfEdge* prev = nullptr;
    HalfEdge* twin = nullptr;
    Face* face = nullptr;
    Edge* edge = nullptr;
};