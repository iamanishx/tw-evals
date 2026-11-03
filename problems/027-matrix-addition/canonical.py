def matrix_add(a: list, b: list) -> list:
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]
