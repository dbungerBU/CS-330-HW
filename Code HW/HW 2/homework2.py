# CS 330 — Fall 2025
# Homework 2, Problem 2 (Coding): SCC of a Source
# Reference solution (for instructors/TAs)
#
# Student submission file name on Gradescope: homework2.py
#Collaborators: none


def bfs_visited(g, s):
    """
    This is the pseudocode from class writen in python
    with an extra set "visited" which will make your life easier
    """
    layers = {}
    dist = {}
    visited = set()
    for v in g:
        dist[v] = float('inf')
    tree = {}
    layers[0] = [s]
    dist[s] = 0
    visited.add(s)  # s has been visited
    i = 0
    while len(layers[i])>0:
        layers[i+1] = []
        for v in layers[i]:
            for u in g[v]:
                if dist[u] == float('inf'):
                    layers[i+1].append(u)
                    visited.add(u)  # u has been visted
                    dist[u] = i+1
                    tree[u] = v
        i += 1
    return layers, dist, visited

def flip_edges(g):
    flipped = {}
    for u in g:
        flipped[u] = {}
    for u in g:
        for v in g[u]:
            flipped[v][u] = 1
    return flipped

def scc_of_source(g, s):
    """Return exactly the vertices in the SCC containing s (or set() if s absent).

    Idea: Let F = nodes reachable from s in G.
          Let B = nodes which reach s in G
          Answer = F intersect B.
    """
    if s not in g:
        return set()
    _, _, F = bfs_visited(g,s)
    g_flipped = flip_edges(g)
    print(g_flipped)
    _, _, B = bfs_visited(g_flipped,s)
    answer = F & B
    return answer