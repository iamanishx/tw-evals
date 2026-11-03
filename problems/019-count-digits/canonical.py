def count_digits(n: int) -> int:
    if n == 0:
        return 1
    c = 0
    while n > 0:
        c += 1
        n //= 10
    return c
