def linear_search(xs: list, target: int) -> int:
    for i, x in enumerate(xs):
        if x == target:
            return i
    return -1
