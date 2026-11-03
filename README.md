# tw-eval

Eval set + benchmark harness for the TW / BTP project: **a cost-effective local AI assistant for a university programming course** (Manish Biswal B523035, Arpita Ghadai B523010, Arpita Nayak B523011; guide: Prof. Anjali Mohapatra, IIIT Bhubaneswar).

Everything the harness reports is measured by running code. No estimated or invented numbers.

## What is here

- `problems/` - 30 introductory programming problems, each with a statement, a required function signature, executable tests (5-7 per problem, 166 total), and a reference solution (`canonical.py`). Topics: basics, loops/number work, strings, lists, matrices, recursion. Difficulty: 19 easy, 11 medium.
- `harness/runner.py` - executes one solution file against one problem's tests in a subprocess and prints a JSON verdict.
- `harness/benchmark.py` - benchmarks any **OpenAI-compatible endpoint** (`/v1/chat/completions`): prompts the model per problem, extracts the code, runs the tests, and records pass rate, latency, tokens/s (from the server's `usage`; llama.cpp `timings` captured verbatim when present), and optionally peak VRAM via `nvidia-smi` sampling. Pure Python stdlib, no dependencies.
- `harness/mock_server.py` - a fake endpoint for verifying the harness itself. Not a model.
- `results/` - run outputs. Currently only **mock-server verification runs** (see below).

## Status and honest limits

- **Target course is not yet pinned down.** The proposal says "one university programming course" without naming it. The set is a generic first-year intro set in Python; swap or translate (e.g. to C) once the course is confirmed. Problem schema is language-agnostic; a C runner (gcc) plugs into the same `problem.json` format.
- **Engine-agnostic by design.** Anything that serves `/v1/chat/completions` can be benchmarked: llama.cpp (`llama-server`), vLLM, or our own engine behind an adapter. llama.cpp is the reference baseline.
- **Our engine (flashlet / FreeToken) currently supports Qwen2.5 dense only.** LFM2.5 MoE weight loading/offloading is the project's own kernel work and is not benchmarked here yet. No engine numbers exist until it serves an OpenAI-compatible endpoint.
- **No real model numbers yet.** `results/mock-verification-*.json` are pipeline checks against a mock server, not model results.

## Running the real benchmark

Serve a model with llama.cpp (reference baseline), e.g. LFM2.5 1B or 8B-A1B GGUF:

```bash
llama-server -m <model>.gguf --port 8080 -ngl 99
```

Then:

```bash
python -m harness.benchmark --base-url http://localhost:8080/v1 \
    --model <model-id> --measure-vram --out results/lfm2.5-<tag>.json
```

Useful flags: `--samples N` (completions per problem), `--temperature` (default 0.2), `--only <ids>` (subset), `--test-timeout`, `--request-timeout`.

Notes:
- `--measure-vram` samples **local** `nvidia-smi` while each generation runs. For remote GPUs (Vast.ai, Modal) run the sampler on that host or read the server's `/metrics`; this flag does nothing without a local GPU (fields come out null, with a warning).
- Pass/fail is result-based: tests check outputs, not which algorithm the model used.
- Generated code is executed locally. Run inside a venv or container; the tests do not need network.

## Verification done so far (2026-11-03)

- All 30 reference solutions pass all of their own tests (166/166).
- Mock end-to-end, `canonical` mode: pass@1 = 100% (30/30), as expected.
- Mock end-to-end, `mixed` mode: pass@1 = 50% (15/30), as designed.
- `--measure-vram` fallback path exercised on a GPU-less machine (null + warning, no crash).

These verify the pipeline only. First real numbers come from llama.cpp serving LFM2.5 on the RTX 4050 laptop.

## Regenerating the problem set

`gen_problems.py` is the one-off generator used to write `problems/`; kept for provenance. Edit the definitions there and rerun it to regenerate (it deletes and rewrites `problems/`).
