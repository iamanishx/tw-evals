#!/usr/bin/env python3
"""Execute one solution file against one problem's tests. Prints a JSON verdict.

Run as a subprocess (see benchmark.py) so a bad solution cannot take down the
benchmark loop:  python -m harness.runner --problem-dir problems/001-sum-of-digits --solution-file sol.py
"""
import argparse, json, math, sys
from pathlib import Path


def approx_equal(got, expected, tol=1e-6):
    if isinstance(expected, bool) or isinstance(got, bool):
        return got == expected
    if isinstance(expected, float) or isinstance(got, float):
        try:
            return math.isclose(float(got), float(expected), rel_tol=tol, abs_tol=tol)
        except (TypeError, ValueError):
            return False
    if isinstance(expected, list):
        return (isinstance(got, list) and len(got) == len(expected)
                and all(approx_equal(g, e) for g, e in zip(got, expected)))
    return got == expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem-dir", required=True)
    ap.add_argument("--solution-file", required=True)
    args = ap.parse_args()

    prob = json.loads((Path(args.problem_dir) / "problem.json").read_text())
    code = Path(args.solution_file).read_text()
    fname = prob["function"]["name"]
    total = len(prob["tests"])

    ns = {"__name__": "__tw_solution__"}  # so `if __name__ == "__main__"` blocks don't fire
    try:
        exec(compile(code, args.solution_file, "exec"), ns)
    except Exception as e:
        print(json.dumps({"passed": 0, "total": total, "error": f"import error: {type(e).__name__}: {e}"}))
        return
    fn = ns.get(fname)
    if not callable(fn):
        print(json.dumps({"passed": 0, "total": total, "error": f"function `{fname}` not defined"}))
        return

    passed, failures = 0, []
    for i, t in enumerate(prob["tests"]):
        try:
            got = fn(*t["args"])
            ok = approx_equal(got, t["expected"])
        except Exception as e:
            got, ok = f"<raised {type(e).__name__}: {e}>", False
        if ok:
            passed += 1
        else:
            failures.append({"test": i, "args": t["args"], "expected": t["expected"], "got": got})
    print(json.dumps({"passed": passed, "total": total, "failures": failures[:5]}))


if __name__ == "__main__":
    main()
