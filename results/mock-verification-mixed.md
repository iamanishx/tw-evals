# Benchmark run mock-verification-mixed

- endpoint: `http://127.0.0.1:8091/v1`
- problems: 30, samples/problem: 1
- temperature: 0.2, max_tokens: 512

| model | pass@1 | tests passed | mean latency (s) | p50 latency (s) | mean tok/s | peak VRAM (MB) |
|---|---|---|---|---|---|---|
| mock-mixed | 50.0% (15/30) | 50.3% | 0.051 | 0.051 | 473.73 | None |
