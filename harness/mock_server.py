#!/usr/bin/env python3
"""Local mock OpenAI-compatible endpoint for verifying the benchmark harness.

NOT a model. It returns canned completions so the full benchmark loop (prompt ->
completion -> extraction -> test execution -> metrics) can be checked without
GPU or network. Modes:
  canonical  - returns the problem's reference solution (should score 100%)
  wrong      - returns a syntactically valid but wrong function (should score 0%)
  mixed      - canonical on even problem ids, wrong on odd ones (should score ~50%)

Usage: python -m harness.mock_server --port 8090 --mode canonical
"""
import argparse, json, re, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_canonical(problems_dir):
    sols = {}
    for d in sorted(Path(problems_dir).iterdir()):
        cj, cs = d / "problem.json", d / "canonical.py"
        if cj.exists() and cs.exists():
            sols[json.loads(cj.read_text())["id"]] = (
                json.loads(cj.read_text())["function"]["name"], cs.read_text())
    return sols


def make_handler(sols, mode, delay):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            if not self.path.endswith("/chat/completions"):
                self.send_error(404)
                return
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            prompt = body["messages"][-1]["content"]
            m = re.search(r"Problem ID: (\d+)", prompt)
            pid = m.group(1) if m else "?"
            fname, canonical = sols.get(pid, ("solve", "def solve(*a):\n    return None\n"))
            use_canonical = mode == "canonical" or (mode == "mixed" and int(pid) % 2 == 0)
            code = canonical if use_canonical else f"def {fname}(*args):\n    return None\n"
            time.sleep(delay)
            content = f"```python\n{code}```\n"
            resp = {
                "id": "chatcmpl-mock", "object": "chat.completion", "created": int(time.time()),
                "model": body.get("model", "mock"),
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": len(prompt) // 4,
                          "completion_tokens": len(content) // 4,
                          "total_tokens": (len(prompt) + len(content)) // 4},
                "timings": {"predicted_per_second": 42.0, "mock": True},
            }
            out = json.dumps(resp).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--mode", choices=["canonical", "wrong", "mixed"], default="canonical")
    ap.add_argument("--delay", type=float, default=0.05)
    ap.add_argument("--problems-dir", default=str(ROOT / "problems"))
    args = ap.parse_args()
    sols = load_canonical(args.problems_dir)
    print(f"mock server on :{args.port} mode={args.mode} with {len(sols)} canonical solutions")
    HTTPServer(("127.0.0.1", args.port), make_handler(sols, args.mode, args.delay)).serve_forever()


if __name__ == "__main__":
    main()
