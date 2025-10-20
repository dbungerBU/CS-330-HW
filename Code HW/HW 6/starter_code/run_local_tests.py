# run_local_tests_hw6.py
# CS 330
# Local tests ofr Homework 6
#
# Uses the input_tests and output_tests folders

import os
import json
import time
from math import inf, isinf
from typing import Tuple, List, Dict, Any

# --- Import student's code ---
try:
    from dijkstra import dijkstra
except Exception as e:
    raise ImportError(
        "Could not import 'dijkstra' from dijkstra.py. "
        "Ensure dijkstra.py is in the same directory and defines dijkstra(G, s) -> (d, parents)."
    ) from e


# -------------------------
# Helpers
# -------------------------

def _pick_dirs() -> Tuple[str, str]:
    """Prefer new names; fall back to legacy names."""
    candidates = [
        ("test_inputs", "expected_outputs"),
        ("input_tests", "output_tests"),
    ]
    for inp, out in candidates:
        if os.path.isdir(inp) and os.path.isdir(out):
            return inp, out
    # default (will error later if missing)
    return "test_inputs", "expected_outputs"


def _list_json_inputs(input_dir: str) -> List[str]:
    return sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".json"))


def _matching_output_name(input_filename: str) -> str:
    base, _ = os.path.splitext(input_filename)
    return base.replace("input", "output") + ".json"


def _load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def _norm_node_set_from_graph(G: Dict[str, Dict[str, float]]) -> set:
    """All nodes that appear as keys or neighbors, normalized to strings."""
    nodes = set(str(u) for u in G.keys())
    for u, nbrs in G.items():
        for v in nbrs.keys():
            nodes.add(str(v))
    return nodes


def _to_float(v) -> float:
    if v == "inf":
        return float("inf")
    return float(v)


def _to_int_or_inf(v) -> float:
    if v == "inf":
        return float("inf")
    return int(v)


def _fmt_num(v) -> str:
    if isinstance(v, (int, float)) and isinf(v):
        return "inf"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


def implied_distances_from_parents(
    parents: Dict[str, str],
    s: str,
    G: Dict[str, Dict[str, float]],
) -> Tuple[Dict[str, float], Dict[str, int]]:
    """
    Return:
      - weighted[v]: sum of G[parent->child] along parent chain (s→v) or inf if invalid
      - unweighted[v]: hop count along parent chain or inf if invalid
    Invalid if cycle in parents, missing parent chain to s, or missing edge (p,v) in G.
    """
    nodes = set(G.keys())
    for u in G:
        nodes.update(G[u].keys())

    weighted: Dict[str, float] = {}
    unweighted: Dict[str, int] = {}
    visiting: Dict[str, bool] = {}
    memo: Dict[str, Tuple[float, int]] = {}

    def climb(v: str) -> Tuple[float, int]:
        if v in memo:
            return memo[v]
        if visiting.get(v, False):
            memo[v] = (inf, inf)
            return memo[v]
        visiting[v] = True

        if v == s:
            res = (0.0, 0)
        else:
            p = parents.get(v, None)
            if p is None:
                res = (inf, inf)
            else:
                pw, ph = climb(p)
                if isinf(pw) or p not in G or v not in G[p]:
                    res = (inf, inf)
                else:
                    res = (pw + G[p][v], ph + 1)

        visiting[v] = False
        memo[v] = res
        return res

    for v in nodes:
        w, h = climb(v)
        weighted[v] = w
        unweighted[v] = h

    return weighted, unweighted


# -------------------------
# Core runner
# -------------------------

def run_local_tests():
    input_dir, expected_dir = _pick_dirs()
    all_inputs = _list_json_inputs(input_dir)

    if not all_inputs:
        print(f"No JSON files found in '{input_dir}'. "
              f"Ensure your tests are in '{input_dir}/' and expected results in '{expected_dir}/'.")
        return

    # If you only want to hand out tests 1..10, feel free to filter here.
    # Example: keep first 10 files by name:
    # all_inputs = [f for f in all_inputs if f.startswith("test_input_")][:10]

    total = len(all_inputs)
    passed = 0
    print(f"\n--- Running HW6 Dijkstra tests ---")
    print(f"Using input dir:     {input_dir}")
    print(f"Using expected dir:  {expected_dir}")
    print(f"Discovered {total} input file(s).\n")

    for fname in all_inputs:
        in_path = os.path.join(input_dir, fname)
        out_fname = _matching_output_name(fname)
        exp_path = os.path.join(expected_dir, out_fname)

        print(f"=== Test: {in_path} ===")
        if not os.path.exists(exp_path):
            print(f"  ❌ No matching expected file found: {exp_path}\n")
            continue

        # Load input
        try:
            inp = _load_json(in_path)
        except Exception as e:
            print(f"  ❌ Failed to read/parse input JSON:\n    {type(e).__name__}: {e}\n")
            continue

        if "dijkstra" not in inp:
            print("  ❌ Input JSON missing top-level key 'dijkstra'.\n")
            continue

        G = inp["dijkstra"].get("graph", {})
        s = inp["dijkstra"].get("source", None)
        if s is None:
            print("  ❌ Input JSON missing 'source' under 'dijkstra'.\n")
            continue

        # Load expected
        try:
            exp = _load_json(exp_path)
        except Exception as e:
            print(f"  ❌ Failed to read/parse expected JSON:\n    {type(e).__name__}: {e}\n")
            continue

        if "dijkstra" not in exp:
            print("  ❌ Expected JSON missing top-level key 'dijkstra'.\n")
            continue

        exp_d = exp["dijkstra"]
        for k in ("expected_distances", "expected_implied_unweighted_by_parents"):
            if k not in exp_d:
                print(f"  ❌ Expected JSON missing '{k}'.\n")
                continue

        expected_distances = {str(k): _to_float(v) for k, v in exp_d["expected_distances"].items()}
        expected_unweighted = {str(k): _to_int_or_inf(v)
                               for k, v in exp_d["expected_implied_unweighted_by_parents"].items()}
        time_ref = float(exp_d.get("time_seconds_reference", 0.0) or 0.0)

        # Run student's Dijkstra
        try:
            t0 = time.perf_counter()
            d_stu, parents_stu = dijkstra(G, s)
            t1 = time.perf_counter()
        except Exception as e:
            print(f"  ❌ dijkstra(G, s) raised exception:\n    {type(e).__name__}: {e}\n")
            continue

        # Compute implied from student's parents
        iw_stu, iu_stu = implied_distances_from_parents(parents_stu, s, G)

        # Normalize for comparison
        d_stu = {str(k): float(v) for k, v in d_stu.items()}
        iw_stu = {str(k): float(v) for k, v in iw_stu.items()}
        iu_stu = {str(k): (float("inf") if isinf(v) else int(v)) for k, v in iu_stu.items()}

        # Build node universe (just for nice error messages)
        graph_nodes = _norm_node_set_from_graph(G)

        # Compare keys first (helps catch missing/extra nodes)
        def _compare_keys(label, got_keys, exp_keys) -> bool:
            got, exp = set(got_keys), set(exp_keys)
            ok = (got == exp)
            if not ok:
                miss = sorted(exp - got)
                extra = sorted(got - exp)
                print(f"  ❌ Key set mismatch for {label}:")
                if miss:
                    print(f"     • Missing keys:    {miss}")
                if extra:
                    print(f"     • Unexpected keys: {extra}")
            return ok

        ok_keys = True
        ok_keys &= _compare_keys("student_distances", d_stu.keys(), expected_distances.keys())
        ok_keys &= _compare_keys("student_implied_weighted_by_parents", iw_stu.keys(), expected_distances.keys())
        ok_keys &= _compare_keys("student_implied_unweighted_by_parents", iu_stu.keys(), expected_unweighted.keys())

        # Per-node comparisons with expressive errors
        EPS = 1e-9
        dist_errors = []
        iw_errors = []
        iu_errors = []
        off_graph = []

        for v in sorted(expected_distances.keys()):
            if v not in graph_nodes:
                off_graph.append(v)

            exp_dv = expected_distances[v]
            got_dv = d_stu.get(v, float("nan"))
            got_iwv = iw_stu.get(v, float("nan"))

            # Distance check
            if isinf(exp_dv) and isinf(got_dv):
                pass
            elif abs(float(got_dv) - float(exp_dv)) > EPS:
                dist_errors.append((v, _fmt_num(got_dv), _fmt_num(exp_dv)))

            # Implied weighted must equal expected distances as well
            if isinf(exp_dv) and isinf(got_iwv):
                pass
            elif abs(float(got_iwv) - float(exp_dv)) > EPS:
                iw_errors.append((v, _fmt_num(got_iwv), _fmt_num(exp_dv)))

        for v in sorted(expected_unweighted.keys()):
            exp_hops = expected_unweighted[v]
            got_hops = iu_stu.get(v, float("nan"))
            if isinf(exp_hops) and isinf(got_hops):
                continue
            if (not isinf(exp_hops)) and (not isinf(got_hops)):
                if int(got_hops) != int(exp_hops):
                    iu_errors.append((v, str(got_hops), str(exp_hops)))
            else:
                # one is inf, the other not
                iu_errors.append((v, _fmt_num(got_hops), _fmt_num(exp_hops)))

        # Report
        student_time = (t1 - t0)
        print(f"  source: {repr(s)}")
        print(f"  nodes in graph: {len(graph_nodes)}")
        if off_graph:
            print(f"  ⚠️  Expected listed nodes not present in graph: {sorted(off_graph)}")

        any_fail = (not ok_keys) or dist_errors or iw_errors or iu_errors

        if not any_fail:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
            if dist_errors:
                print("    • Distance mismatches (student_distances vs expected_distances):")
                for v, got, expv in dist_errors[:20]:
                    print(f"       {v}: got {got}, expected {expv}")
                if len(dist_errors) > 20:
                    print(f"       ... and {len(dist_errors) - 20} more")
            if iw_errors:
                print("    • Implied weighted mismatches (from parents vs expected_distances):")
                for v, got, expv in iw_errors[:20]:
                    print(f"       {v}: got {got}, expected {expv}")
                if len(iw_errors) > 20:
                    print(f"       ... and {len(iw_errors) - 20} more")
            if iu_errors:
                print("    • Implied unweighted (hop count) mismatches:")
                for v, got, expv in iu_errors[:20]:
                    print(f"       {v}: got {got}, expected {expv}")
                if len(iu_errors) > 20:
                    print(f"       ... and {len(iu_errors) - 20} more")

        # Optional timing comparison
        if time_ref > 0.0:
            if student_time <= 10.0 * time_ref:
                print(f"    Time check OK: {student_time:.6f}s ≤ 10× ref {time_ref:.6f}s")
            else:
                print(f"    ⚠️  Time check FAIL: {student_time:.6f}s > 10× ref {time_ref:.6f}s")
        print()

    print(f"=== Summary: {passed}/{total} tests passed. ===")


if __name__ == "__main__":
    run_local_tests()
