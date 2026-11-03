def binary_to_decimal(s: str) -> int:
    v = 0
    for c in s:
        v = v * 2 + (1 if c == '1' else 0)
    return v
