#python3
"""
local_dijkstra_tester.py

A lightweight local tester for a *modified* Dijkstra implementation that
breaks ties by choosing the path with the FEWEST number of edges among
all shortest (minimum total weight) paths.

Expected student API:
    from dijkstra import dijkstra
    from priorityQue import MinPriorityQueue
    from math import inf

Your dijkstra(G, s) should:
  - Return (d, parents) where:
        d[u] is the shortest-path distance from s to u (or inf if unreachable)
        parents[u] is the parent of u in the chosen shortest-path tree (parents[s] == None)
  - Among paths with equal total weight, choose the one with the fewest edges.
  - Raise ValueError if a negative edge weight is detected (as in the provided template).

Run:
    python3 local_dijkstra_tester.py
"""

from math import inf
import sys
import traceback

# The student's modules
try:
    from dijkstra import dijkstra  # function under test
except Exception as e:
    print("ERROR: Could not import dijkstra() from dijkstra.py\n")
    traceback.print_exc()
    sys.exit(1)

# NOTE: We import this to ensure the student's environment matches the spec;
# the tester doesn't *use* MinPriorityQueue directly.
try:
    from priorityQue import MinPriorityQueue  # noqa: F401
except Exception as e:
    print("WARNING: Could not import MinPriorityQueue from priorityQue.py")
    print("         (The tests don't require it directly, but your implementation likely does.)\n")


# -----------------------------
# Utilities
# -----------------------------

def reconstruct_path(parents, s, t):
    """Reconstruct path from s to t using parents table. Returns list [s, ..., t] or [] if unreachable."""
    if t not in parents:
        return []
    path = []
    cur = t
    seen = set()
    while cur is not None:
        path.append(cur)
        if cur == s:
            return list(reversed(path))
        if cur in seen:   # cycle-guard for malformed parents
            return []
        seen.add(cur)
        cur = parents.get(cur, None)
    # if we fell out without hitting s
    return []


def assert_equal(actual, expected, msg=""):
    if actual != expected:
        raise AssertionError(f"{msg}\nExpected: {expected}\nActual:   {actual}")


def assert_almost_equal(a, b, msg=""):
    if a == b:
        return
    # allow inf comparisons and exact equality only (weights assumed integral or exact floats in tests)
    raise AssertionError(f"{msg}\nExpected: {b}\nActual:   {a}")


def pretty_result(title, ok, details=""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {title}")
    if details:
        print(details)
    if not ok:
        print()


# -----------------------------
# Test Graphs
# -----------------------------

def graph_triangle_tie():
    # s --2--> t
    # s --1--> a --1--> t
    # Two s->t paths of equal total weight 2; fewest edges path is direct s->t.
    return {
        "s": {"t": 2, "a": 1},
        "a": {"t": 1},
        "t": {},
    }, "s"


def graph_two_routes_len3():
    # Two equal-weight routes to t (weight 3), but different edge counts.
    # s->a->b->t uses 3 edges (1+1+1)
    # s->c->t   uses 2 edges (2+1)
    return {
        "s": {"a": 1, "c": 2},
        "a": {"b": 1},
        "b": {"t": 1},
        "c": {"t": 1},
        "t": {},
    }, "s"


def graph_zero_weight_tie():
    # All zero-weight, prefer fewest edges:
    # s->t (0) vs s->x->t (0+0). Choose s->t.
    return {
        "s": {"t": 0, "x": 0},
        "x": {"t": 0},
        "t": {},
    }, "s"


def graph_disconnected():
    # u is unreachable
    return {
        "s": {"a": 1},
        "a": {"b": 2},
        "b": {},
        "u": {},           # disconnected node
    }, "s"


# -----------------------------
# Tests
# -----------------------------

def test_triangle_tie():
    G, s = graph_triangle_tie()
    d, parents = dijkstra(G, s)

    # Distances
    assert_almost_equal(d["s"], 0, "d[s] should be 0")
    assert_almost_equal(d["a"], 1, "d[a] incorrect")
    assert_almost_equal(d["t"], 2, "d[t] incorrect")

    # Tie-breaking: s->t should be chosen over s->a->t
    assert_equal(parents.get("s"), None, "parent[s] must be None")
    assert_equal(parents.get("t"), "s", "Tie-break failed: parent[t] should be 's' (fewest-edge path).")

    # Path check
    path = reconstruct_path(parents, s, "t")
    assert_equal(path, ["s", "t"], "Path s->t should be direct due to fewest-edge tie-break.")


def test_two_routes_len3():
    G, s = graph_two_routes_len3()
    d, parents = dijkstra(G, s)

    assert_almost_equal(d["t"], 3, "Shortest distance to t should be 3")

    # Verify it picks s->c->t (2 edges) instead of s->a->b->t (3 edges)
    path = reconstruct_path(parents, s, "t")
    assert_equal(path, ["s", "c", "t"],
                 "Tie-break failed: should choose path with fewer edges (s->c->t).")


def test_zero_weight_tie():
    G, s = graph_zero_weight_tie()
    d, parents = dijkstra(G, s)

    assert_almost_equal(d["t"], 0, "Shortest distance to t should be 0")
    path = reconstruct_path(parents, s, "t")
    assert_equal(path, ["s", "t"], "Zero-weight tie should still prefer fewest edges (direct edge).")


def test_disconnected():
    G, s = graph_disconnected()
    d, parents = dijkstra(G, s)

    # reachable
    assert_almost_equal(d["s"], 0, "d[s] should be 0")
    assert_almost_equal(d["a"], 1, "d[a] incorrect")
    assert_almost_equal(d["b"], 3, "d[b] incorrect")

    # unreachable node 'u'
    assert_almost_equal(d["u"], inf, "Unreachable node should have distance inf")
    assert_equal(parents.get("u"), None, "Unreachable node should have parent None")

# -----------------------------
# Runner
# -----------------------------

TESTS = [
    ("Triangle tie (prefer fewer edges over equal weight)", test_triangle_tie),
    ("Two equal-weight routes of length 3 (prefer fewer edges)", test_two_routes_len3),
    ("Zero-weight tie (prefer direct edge)", test_zero_weight_tie),
    ("Disconnected node has distance inf & parent None", test_disconnected),
]


def main():
    print("Running local Dijkstra tie-break tester (fewest edges among equal-weight paths)\n")
    passed = 0
    for title, fn in TESTS:
        try:
            fn()
            pretty_result(title, True)
            passed += 1
        except AssertionError as e:
            pretty_result(title, False, details=str(e))
        except Exception as e:
            pretty_result(title, False, details=f"Unexpected error:\n{traceback.format_exc()}")

    total = len(TESTS)
    print("\nSummary: {}/{} tests passed.".format(passed, total))
    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    main()
