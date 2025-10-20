from math import inf
from priorityQue import MinPriorityQueue

"""
In homework 6's coding assignment we have given you the code for Dijkstra from class (with some minor changes
like more input validation). 
The task of the coding homework is for you to edit this implemnation of Dijkstra 
so that if there are tied shortest paths you will return the one with the fewest edges. 
E.G. if we have a graph with three nodes a,b,c and three edges (a->b weight 1) (b->c weight 1) and (a -> c weight 2)
that you will allways pick the path a->b->c. Note what this means: you should return the SAME distances that 
normal Dijkstra does. BUT you have to return a valid shortest paths tree with this new edge count constraint. 

The goal of this problem is to give you practice thinking about Dijkstra and to make sure you 
understand what it is doing and what you can do with weights. Also, we hope that thinking deeply about the 
pseudocode/code will help you get a sense of what is happening. 

Feel free to look at the PQ implementation in the other file. 
"""


def dijkstra(G, s):
    """
    This is an implmentation of the Dijkstra algorithm from class (see slide 18 from the 10_09 lecture)

    Graph format: G[u][v] = weight l(u, v) the weights might be integers or floats

    Returns:
        d: a dict mapping node -> shortest distance from s
        parents: dict mapping node -> parent in shortest-path tree (s has parent None)
    """
    # We won't give you any graphs with negative edge weights, but here is how you could implement it
    for u, neighbors in G.items():
        for v, weight in neighbors.items():
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights; found negative weight")

    # Collect all vertices (include isolated / sink nodes that might only appear as neighbors)
    vertices = set(G.keys())

    # pi: current best-known distances (keys)
    pi = {}
    # d: finalized shortest distances
    d = {}
    # parents in shortest paths tree
    parents = {s: None}

    # your implementation from part 1
    Q = MinPriorityQueue()

    # Initialize source
    pi[s] = 0.0
    Q.insert(s, 0.0)

    # Initialize all other vertices to infinity
    for v in vertices:
        if v == s:
            continue
        pi[v] = inf
        parents.setdefault(v, None)
        Q.insert(v, inf)

    # Main loop
    while Q.heap:
        u, path_length_u = Q.extract_min()  # returns (element, priority)
        d[u] = path_length_u

        if path_length_u == inf:
            continue

        # For each neighbor v of u
        for v, weight_uv in G[u].items():
            # Update the best path length to v using edge (u, v) if it improves pi[v]
            if pi[v] > d[u] + weight_uv:
                new_priority = d[u] + weight_uv
                Q.decrease_key(v, new_priority)
                pi[v] = new_priority
                parents[v] = u

    return d, parents
