def max_of_list(xs: list) -> float:
    m = xs[0]
    for x in xs[1:]:
        if x > m:
            m = x
    return m
