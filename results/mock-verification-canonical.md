# Benchmark run mock-verification-canonical

- endpoint: `http://127.0.0.1:8090/v1`
- problems: 30, samples/problem: 1
- temperature: 0.2, max_tokens: 512

| model | pass@1 | tests passed | mean latency (s) | p50 latency (s) | mean tok/s | peak VRAM (MB) |
|---|---|---|---|---|---|---|
| mock-canonical | 100.0% (30/30) | 100.0% | 0.051 | 0.051 | 624.68 | None |
