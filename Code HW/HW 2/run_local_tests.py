# run_local_tests_hw2.py
# CS 330 — Fall 2025
# Runner for Homework 2 JSON tests (SCC of a Source)
#
# Looks for JSON test pairs in either:
#   - test_inputs/ and expected_outputs/
#   - input_tests/ and output_tests/   (legacy naming)
#
# Each input file expects a JSON of the form:
#   {
#     "graph": { "u": { "v": true, ... }, ... },
#     "source": "u",
#     "meta": { ... }   # optional
#   }
# And matching expected file:
#   {
#     "expected_scc": ["u", "v", ...],   # list of node IDs (strings or numbers)
#     "time_seconds": 0.0123,            # optional, reference time
#     "meta": { ... }                     # optional
#   }

import os
import json
import time
from typing import Tuple, List

# Import student's code
try:
    from homework2 import scc_of_source
except Exception as e:
    raise ImportError(
        "Could not import 'scc_of_source' from homework2.py. "
        "Ensure homework2.py is in the same directory and defines scc_of_source(g, s)."
    ) from e


def _pick_dirs() -> Tuple[str, str]:
    """
    Prefer the new names (test_inputs/expected_outputs). If they don't exist,
    fall back to the legacy names (input_tests/output_tests).
    """
    candidates = [
        ("test_inputs", "expected_outputs"),
        ("input_tests", "output_tests"),
    ]
    for inp, out in candidates:
        if os.path.isdir(inp) and os.path.isdir(out):
            return inp, out
    # If neither pair exists, default to new names (will error nicely later)
    return "test_inputs", "expected_outputs"


def _list_json_inputs(input_dir: str) -> List[str]:
    return sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith(".json")
    )


def _matching_output_name(input_filename: str) -> str:
    """
    Map 'test_input_XXX.json' -> 'test_output_XXX.json'.
    If the name pattern differs, this still works as long as
    you used 'input' and 'output' in symmetrical positions.
    """
    base, _ = os.path.splitext(input_filename)
    # Try the canonical replacement
    guess = base.replace("input", "output") + ".json"
    return guess


def _as_set(iterable):
    """
    Convert a list-like of node IDs to a set. Handles strings or numbers.
    """
    return set(iterable)


def run_local_tests():
    input_dir, output_dir = _pick_dirs()
    all_inputs = _list_json_inputs(input_dir)

    if not all_inputs:
        print(f"No JSON files found in '{input_dir}'. "
              f"Ensure your tests are in '{input_dir}/' and expected results in '{output_dir}/'.")
        return

    total = len(all_inputs)
    passed = 0
    print(f"\n--- Running HW2 JSON-based tests ---")
    print(f"Using input dir:    {input_dir}")
    print(f"Using expected dir: {output_dir}")
    print(f"Discovered {total} input file(s).\n")

    for fname in all_inputs:
        in_path = os.path.join(input_dir, fname)
        out_fname = _matching_output_name(fname)
        out_path = os.path.join(output_dir, out_fname)

        print(f"=== Test: {in_path} ===")
        if not os.path.exists(out_path):
            print(f"  ❌ No matching expected file found: {out_path}")
            continue

        # --- Load input
        try:
            with open(in_path, "r") as f:
                inp = json.load(f)
        except Exception as e:
            print(f"  ❌ Failed to read/parse input JSON:\n    {type(e).__name__}: {e}")
            continue

        G = inp.get("graph", {})
        s = inp.get("source", None)

        if s is None:
            print("  ❌ Input JSON missing 'source' key.")
            continue

        # --- Load expected
        try:
            with open(out_path, "r") as f:
                exp = json.load(f)
        except Exception as e:
            print(f"  ❌ Failed to read/parse expected JSON:\n    {type(e).__name__}: {e}")
            continue

        expected_list = exp.get("expected_scc", None)
        official_time = exp.get("time_seconds", None)

        if expected_list is None:
            print("  ❌ 'expected_scc' missing in expected JSON.")
            continue

        expected_set = _as_set(expected_list)

        # --- Run student's function
        try:
            t0 = time.perf_counter()
            got_set = scc_of_source(G, s)
            t1 = time.perf_counter()
        except Exception as e:
            print(f"  ❌ scc_of_source raised exception:\n    {type(e).__name__}: {e}")
            continue

        # Validate return type
        if not isinstance(got_set, set):
            print(f"  ❌ Expected a set from scc_of_source, got {type(got_set).__name__}.")
            continue

        # --- Compare
        ok = (got_set == expected_set)
        missing = expected_set - got_set
        extra   = got_set - expected_set

        print(f"  source: {repr(s)}")
        print(f"  expected: {sorted(expected_set)}")
        print(f"  got:      {sorted(got_set)}")

        if ok:
            print("PASS")
            passed += 1
        else:
            print("FAIL")
            if missing:
                print(f"    • Missing:    {sorted(missing)}")
            if extra:
                print(f"    • Unexpected: {sorted(extra)}")

        # Optional timing comparison if a reference time exists
        student_time = t1 - t0
        if official_time is not None:
            if student_time <= 10.0 * float(official_time):
                print(f"    Time check OK: {student_time:.6f}s <= 10× official {official_time:.6f}s")
            else:
                print(f"    Time check FAIL: {student_time:.6f}s > 10× official {official_time:.6f}s")

        print()

    print(f"=== Summary: {passed}/{total} tests passed. ===")


if __name__ == "__main__":
    run_local_tests()
