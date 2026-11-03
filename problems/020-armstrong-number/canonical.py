def is_armstrong(n: int) -> bool:
    s = str(n)
    k = len(s)
    return sum(int(d) ** k for d in s) == n
