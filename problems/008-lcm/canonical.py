def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    x, y = a, b
    while y:
        x, y = y, x % y
    return a * b // x
