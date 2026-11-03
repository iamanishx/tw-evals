def is_palindrome_number(n: int) -> bool:
    s = str(n)
    return s == s[::-1]
