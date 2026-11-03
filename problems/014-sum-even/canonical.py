def sum_even(xs: list) -> int:
    return sum(x for x in xs if x % 2 == 0)
