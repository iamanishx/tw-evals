def decimal_to_binary(n: int) -> str:
    if n == 0:
        return '0'
    s = ''
    while n > 0:
        s = str(n % 2) + s
        n //= 2
    return s
