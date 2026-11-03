#!/usr/bin/env python3
"""Benchmark an OpenAI-compatible endpoint on the TW course eval set.

Measures per problem: pass rate (executable tests), latency, tokens/s (from the
server's `usage` field; llama.cpp `timings` are captured verbatim when present)
and, with --measure-vram, peak local GPU memory via nvidia-smi sampling.

Only real measurements are written to the results file. Nothing is estimated
except where a field is explicitly named an estimate.

Example (llama.cpp serving LFM2.5 locally):
    llama-server -m <model>.gguf --port 8080 -ngl 99
    python -m harness.benchmark --base-url http://localhost:8080/v1 \
        --model lfm2.5-local --measure-vram --out results/run.json
"""
import argparse, json, re, shutil, statistics, subprocess, sys, tempfile, threading, time
from datetime import datetime, timezone
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent.parent

PROMPT_TEMPLATE = """You are helping a first-year university programming student.
Problem ID: {id}
Write a Python function with EXACTLY this signature:

{signature}

{statement}

Rules:
- Return only the Python code for the function: no explanation, no test code, no prints.
- Do not read from stdin and do not print anything.
"""


def load_problems(problems_dir, only=None):
    probs = []
    for d in sorted(Path(problems_dir).iterdir()):
        pj = d / "problem.json"
        if not pj.exists():
            continue
        p = json.loads(pj.read_text())
        p["_dir"] = str(d)
        if only and p["id"] not in only and p["slug"] not in only:
            continue
        probs.append(p)
    return probs


def extract_code(text):
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    return (m[0] if m else text).strip()


def chat_completion(base_url, api_key, model, prompt, temperature, max_tokens, timeout):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        payload = json.loads(r.read())
    return payload, time.perf_counter() - t0


class VRamSampler:
    """Peak local GPU memory while a generation runs. Inactive without nvidia-smi."""

    def __init__(self, enabled):
        self.enabled = enabled and shutil.which("nvidia-smi") is not None
        self._stop = threading.Event()
        self._thread = None
        self.samples = []

    def _poll(self):
        while not self._stop.is_set():
            try:
                out = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5).stdout
                self.samples.append(max(int(x.strip()) for x in out.splitlines() if x.strip()))
            except Exception:
                pass
            self._stop.wait(0.25)

    def __enter__(self):
        if self.enabled:
            self.samples = []
            self._stop.clear()
            self._thread = threading.Thread(target=self._poll, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, *exc):
        if self.enabled:
            self._stop.set()
            self._thread.join()

    @property
    def peak_mb(self):
        return max(self.samples) if self.samples else None


def run_solution(problem_dir, solution_path, timeout):
    try:
        cp = subprocess.run(
            [sys.executable, "-m", "harness.runner",
             "--problem-dir", problem_dir, "--solution-file", str(solution_path)],
            capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return {"passed": 0, "total": None, "error": f"test execution timed out after {timeout}s"}
    try:
        return json.loads(cp.stdout)
    except json.JSONDecodeError:
        return {"passed": 0, "total": None, "error": f"runner failed: {cp.stderr[-300:]}"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default="http://localhost:8080/v1")
    ap.add_argument("--api-key", default="none")
    ap.add_argument("--model", action="append", required=True,
                    help="Model id as the server expects it. Repeat for several models.")
    ap.add_argument("--problems-dir", default=str(ROOT / "problems"))
    ap.add_argument("--only", nargs="*", default=None, help="Problem ids/slugs to run (default: all)")
    ap.add_argument("--samples", type=int, default=1, help="Completions per problem (for pass@1 spread)")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--request-timeout", type=int, default=180)
    ap.add_argument("--test-timeout", type=int, default=10)
    ap.add_argument("--measure-vram", action="store_true", help="Sample local nvidia-smi during generation")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    problems = load_problems(args.problems_dir, args.only)
    if not problems:
        sys.exit("no problems found")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out or ROOT / "results" / f"run-{ts}.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    vram = VRamSampler(args.measure_vram)
    if args.measure_vram and not vram.enabled:
        print("warning: --measure-vram given but nvidia-smi not found; vram fields will be null", file=sys.stderr)

    report = {
        "run_id": out.stem, "started_at": ts,
        "config": {k: getattr(args, k) for k in
                   ("base_url", "model", "samples", "temperature", "max_tokens",
                    "request_timeout", "test_timeout", "measure_vram")},
        "n_problems": len(problems), "models": {},
    }

    for model in args.model:
        records = []
        for p in problems:
            for s in range(args.samples):
                prompt = PROMPT_TEMPLATE.format(id=p["id"], signature=p["function"]["signature"],
                                                statement=p["statement"])
                rec = {"id": p["id"], "slug": p["slug"], "topic": p["topic"],
                       "difficulty": p["difficulty"], "sample": s}
                try:
                    with vram:
                        payload, latency = chat_completion(args.base_url, args.api_key, model,
                                                           prompt, args.temperature, args.max_tokens,
                                                           args.request_timeout)
                except Exception as e:
                    rec["error"] = f"request failed: {type(e).__name__}: {e}"
                    records.append(rec)
                    continue
                rec["latency_s"] = round(latency, 3)
                rec["peak_vram_mb"] = vram.peak_mb
                usage = payload.get("usage") or {}
                rec["prompt_tokens"] = usage.get("prompt_tokens")
                rec["completion_tokens"] = usage.get("completion_tokens")
                if "timings" in payload:  # llama.cpp extension, captured verbatim
                    rec["server_timings"] = payload["timings"]
                ct = rec["completion_tokens"]
                rec["tokens_per_s"] = round(ct / latency, 2) if ct and latency > 0 else None

                text = payload["choices"][0]["message"]["content"]
                code = extract_code(text)
                with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                    f.write(code)
                    sol_path = f.name
                verdict = run_solution(p["_dir"], sol_path, args.test_timeout)
                Path(sol_path).unlink()
                rec.update({"passed": verdict.get("passed"), "total": verdict.get("total"),
                            "all_passed": verdict.get("passed") == verdict.get("total") is not None
                            and verdict.get("total") is not None and verdict.get("passed") == verdict.get("total")})
                if verdict.get("error"):
                    rec["verdict_error"] = verdict["error"]
                records.append(rec)
                status = "PASS" if rec["all_passed"] else "fail"
                print(f"[{model}] {p['id']} {p['slug']} sample{s}: {status} "
                      f"({rec.get('passed')}/{rec.get('total')} tests, {latency:.2f}s)", flush=True)

        lat = [r["latency_s"] for r in records if "latency_s" in r]
        tps = [r["tokens_per_s"] for r in records if r.get("tokens_per_s")]
        vrm = [r["peak_vram_mb"] for r in records if r.get("peak_vram_mb")]
        passed = [r for r in records if r.get("all_passed")]
        tpass = sum(r.get("passed") or 0 for r in records)
        ttotal = sum(r.get("total") or 0 for r in records)
        report["models"][model] = {
            "summary": {
                "pass_at_1": round(len(passed) / len(records), 4) if records else None,
                "problems_fully_passed": len(passed), "records": len(records),
                "per_test_pass_rate": round(tpass / ttotal, 4) if ttotal else None,
                "mean_latency_s": round(statistics.mean(lat), 3) if lat else None,
                "p50_latency_s": round(statistics.median(lat), 3) if lat else None,
                "mean_tokens_per_s": round(statistics.mean(tps), 2) if tps else None,
                "peak_vram_mb": max(vrm) if vrm else None,
            },
            "records": records,
        }

    out.write_text(json.dumps(report, indent=2) + "\n")
    md = out.with_suffix(".md")
    lines = [f"# Benchmark run {report['run_id']}", "",
             f"- endpoint: `{args.base_url}`", f"- problems: {len(problems)}, samples/problem: {args.samples}",
             f"- temperature: {args.temperature}, max_tokens: {args.max_tokens}", "",
             "| model | pass@1 | tests passed | mean latency (s) | p50 latency (s) | mean tok/s | peak VRAM (MB) |",
             "|---|---|---|---|---|---|---|"]
    for m, d in report["models"].items():
        s = d["summary"]
        tpr = f"{s['per_test_pass_rate']:.1%}" if s["per_test_pass_rate"] is not None else "n/a"
        lines.append(f"| {m} | {s['pass_at_1']:.1%} ({s['problems_fully_passed']}/{s['records']}) | {tpr} | "
                     f"{s['mean_latency_s']} | {s['p50_latency_s']} | {s['mean_tokens_per_s']} | {s['peak_vram_mb']} |")
    md.write_text("\n".join(lines) + "\n")
    print(f"\nwrote {out}\nwrote {md}")


if __name__ == "__main__":
    main()
