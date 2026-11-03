def power(x: float, n: int) -> float:
    r = 1
    for _ in range(n):
        r *= x
    return r
