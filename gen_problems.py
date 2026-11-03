#!/usr/bin/env python3
"""Generates the problems/ tree. One-off scaffolding tool; committed for provenance."""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

P = []
def add(slug, title, topic, difficulty, signature, statement, canonical, tests):
    P.append(dict(slug=slug, title=title, topic=topic, difficulty=difficulty,
                  signature=signature, statement=statement, canonical=canonical,
                  tests=[{"args": a, "expected": e} for a, e in tests]))

add("sum-of-digits", "Sum of digits", "basics", "easy",
    "def sum_of_digits(n: int) -> int:",
    "Given a non-negative integer n, return the sum of its decimal digits.",
    "def sum_of_digits(n: int) -> int:\n    s = 0\n    while n > 0:\n        s += n % 10\n        n //= 10\n    return s\n",
    [([123], 6), ([0], 0), ([5], 5), ([9999], 36), ([1000000], 1), ([7], 7)])

add("reverse-number", "Reverse a number", "loops", "easy",
    "def reverse_number(n: int) -> int:",
    "Given a non-negative integer n, return the integer formed by reversing its decimal digits. Leading zeros after reversal are dropped (e.g. 1000 becomes 1).",
    "def reverse_number(n: int) -> int:\n    r = 0\n    while n > 0:\n        r = r * 10 + n % 10\n        n //= 10\n    return r\n",
    [([123], 321), ([1000], 1), ([0], 0), ([7], 7), ([120045], 540021), ([987654321], 123456789)])

add("palindrome-number", "Palindrome number", "loops", "easy",
    "def is_palindrome_number(n: int) -> bool:",
    "Given a non-negative integer n, return True if its decimal representation reads the same forwards and backwards, else False.",
    "def is_palindrome_number(n: int) -> bool:\n    s = str(n)\n    return s == s[::-1]\n",
    [([121], True), ([123], False), ([0], True), ([11], True), ([12321], True), ([10], False)])

add("factorial", "Factorial", "basics", "easy",
    "def factorial(n: int) -> int:",
    "Given a non-negative integer n, return n! (0! = 1).",
    "def factorial(n: int) -> int:\n    r = 1\n    for i in range(2, n + 1):\n        r *= i\n    return r\n",
    [([0], 1), ([1], 1), ([5], 120), ([10], 3628800), ([3], 6), ([7], 5040)])

add("fibonacci", "Fibonacci number", "loops", "easy",
    "def fib(n: int) -> int:",
    "Return the n-th Fibonacci number with fib(0) = 0 and fib(1) = 1.",
    "def fib(n: int) -> int:\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n",
    [([0], 0), ([1], 1), ([2], 1), ([6], 8), ([10], 55), ([15], 610), ([20], 6765)])

add("is-prime", "Primality test", "loops", "easy",
    "def is_prime(n: int) -> bool:",
    "Return True if n is a prime number, else False. Numbers below 2 are not prime.",
    "def is_prime(n: int) -> bool:\n    if n < 2:\n        return False\n    i = 2\n    while i * i <= n:\n        if n % i == 0:\n            return False\n        i += 1\n    return True\n",
    [([2], True), ([1], False), ([17], True), ([18], False), ([97], True), ([91], False), ([0], False)])

add("gcd", "Greatest common divisor", "loops", "easy",
    "def gcd(a: int, b: int) -> int:",
    "Return the greatest common divisor of non-negative integers a and b (not both zero). gcd(0, x) = x.",
    "def gcd(a: int, b: int) -> int:\n    while b:\n        a, b = b, a % b\n    return a\n",
    [([12, 18], 6), ([7, 13], 1), ([0, 5], 5), ([100, 75], 25), ([17, 17], 17), ([48, 36], 12)])

add("lcm", "Least common multiple", "loops", "easy",
    "def lcm(a: int, b: int) -> int:",
    "Return the least common multiple of non-negative integers a and b. If either is 0, return 0.",
    "def lcm(a: int, b: int) -> int:\n    if a == 0 or b == 0:\n        return 0\n    x, y = a, b\n    while y:\n        x, y = y, x % y\n    return a * b // x\n",
    [([4, 6], 12), ([7, 13], 91), ([0, 5], 0), ([12, 18], 36), ([5, 5], 5), ([100, 75], 300)])

add("count-vowels", "Count vowels", "strings", "easy",
    "def count_vowels(s: str) -> int:",
    "Return the number of vowels (a, e, i, o, u, either case) in the string s.",
    "def count_vowels(s: str) -> int:\n    return sum(1 for c in s if c in 'aeiouAEIOU')\n",
    [(["hello"], 2), (["xyz"], 0), (["AEIOU"], 5), (["Programming"], 3), ([""], 0), (["bcdfg"], 0)])

add("reverse-string", "Reverse a string", "strings", "easy",
    "def reverse_string(s: str) -> str:",
    "Return the string s reversed.",
    "def reverse_string(s: str) -> str:\n    return s[::-1]\n",
    [(["hello"], "olleh"), ([""], ""), (["a"], "a"), (["ab cd"], "dc ba"), (["12321"], "12321")])

add("palindrome-string", "Palindrome string", "strings", "easy",
    "def is_palindrome_string(s: str) -> bool:",
    "Return True if s reads the same forwards and backwards (case-sensitive, exactly as given), else False.",
    "def is_palindrome_string(s: str) -> bool:\n    return s == s[::-1]\n",
    [(["madam"], True), (["racecar"], True), (["hello"], False), ([""], True), (["a"], True), (["ab"], False)])

add("max-of-list", "Maximum of a list", "lists", "easy",
    "def max_of_list(xs: list) -> float:",
    "Return the largest element of the non-empty list of numbers xs, without using the built-in max().",
    "def max_of_list(xs: list) -> float:\n    m = xs[0]\n    for x in xs[1:]:\n        if x > m:\n            m = x\n    return m\n",
    [([[1, 2, 3]], 3), ([[-5, -2, -9]], -2), ([[42]], 42), ([[0, 0, 0]], 0), ([[3.5, 2.1, 9.9]], 9.9)])

add("second-largest", "Second largest element", "lists", "medium",
    "def second_largest(xs: list) -> int:",
    "Return the second largest DISTINCT value in the list of numbers xs. The list always contains at least two distinct values.",
    "def second_largest(xs: list) -> int:\n    return sorted(set(xs))[-2]\n",
    [([[1, 2, 3]], 2), ([[10, 5, 8]], 8), ([[5, 5, 4]], 4), ([[100, 99]], 99), ([[7, 3, 7, 2]], 3)])

add("sum-even", "Sum of even numbers", "lists", "easy",
    "def sum_even(xs: list) -> int:",
    "Return the sum of the even numbers in the list xs. Return 0 for an empty list or one with no even numbers.",
    "def sum_even(xs: list) -> int:\n    return sum(x for x in xs if x % 2 == 0)\n",
    [([[1, 2, 3, 4]], 6), ([[]], 0), ([[1, 3, 5]], 0), ([[2, 4, 6]], 12), ([[-2, 3]], -2)])

add("celsius-to-fahrenheit", "Celsius to Fahrenheit", "basics", "easy",
    "def celsius_to_fahrenheit(c: float) -> float:",
    "Convert a temperature from Celsius to Fahrenheit: F = C * 9/5 + 32.",
    "def celsius_to_fahrenheit(c: float) -> float:\n    return c * 9 / 5 + 32\n",
    [([0], 32.0), ([100], 212.0), ([-40], -40.0), ([37], 98.6), ([25], 77.0)])

add("simple-interest", "Simple interest", "basics", "easy",
    "def simple_interest(p: float, r: float, t: float) -> float:",
    "Return the simple interest on principal p at rate r percent per year for t years: SI = p * r * t / 100.",
    "def simple_interest(p: float, r: float, t: float) -> float:\n    return p * r * t / 100\n",
    [([1000, 5, 2], 100.0), ([1500, 4.5, 3], 202.5), ([0, 10, 5], 0.0), ([2500, 6, 1], 150.0), ([10000, 7.25, 2], 1450.0)])

add("area-of-circle", "Area of a circle", "basics", "easy",
    "def area_of_circle(r: float) -> float:",
    "Return the area of a circle of radius r, using pi = 3.141592653589793.",
    "def area_of_circle(r: float) -> float:\n    return 3.141592653589793 * r * r\n",
    [([1], 3.141592653589793), ([0], 0.0), ([2.5], 19.634954084936208), ([10], 314.1592653589793)])

add("leap-year", "Leap year", "basics", "easy",
    "def is_leap_year(year: int) -> bool:",
    "Return True if year is a leap year in the Gregorian calendar: divisible by 4, except century years unless divisible by 400.",
    "def is_leap_year(year: int) -> bool:\n    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)\n",
    [([2000], True), ([1900], False), ([2024], True), ([2023], False), ([2100], False), ([2026], False)])

add("count-digits", "Count digits", "basics", "easy",
    "def count_digits(n: int) -> int:",
    "Return the number of decimal digits of a non-negative integer n. count_digits(0) = 1.",
    "def count_digits(n: int) -> int:\n    if n == 0:\n        return 1\n    c = 0\n    while n > 0:\n        c += 1\n        n //= 10\n    return c\n",
    [([12345], 5), ([0], 1), ([9], 1), ([1000000], 7), ([987654321], 9)])

add("armstrong-number", "Armstrong number", "loops", "medium",
    "def is_armstrong(n: int) -> bool:",
    "Return True if n equals the sum of its own digits each raised to the power of the number of digits (e.g. 153 = 1^3 + 5^3 + 3^3).",
    "def is_armstrong(n: int) -> bool:\n    s = str(n)\n    k = len(s)\n    return sum(int(d) ** k for d in s) == n\n",
    [([153], True), ([370], True), ([9474], True), ([123], False), ([0], True), ([9], True), ([10], False)])

add("prime-factors", "Prime factorization", "loops", "medium",
    "def prime_factors(n: int) -> list:",
    "Return the prime factors of an integer n >= 2 as a sorted list with repetition (e.g. 12 -> [2, 2, 3]).",
    "def prime_factors(n: int) -> list:\n    f = []\n    d = 2\n    while d * d <= n:\n        while n % d == 0:\n            f.append(d)\n            n //= d\n        d += 1\n    if n > 1:\n        f.append(n)\n    return f\n",
    [([12], [2, 2, 3]), ([13], [13]), ([100], [2, 2, 5, 5]), ([84], [2, 2, 3, 7]), ([2], [2]), ([360], [2, 2, 2, 3, 3, 5])])

add("binary-to-decimal", "Binary to decimal", "strings", "medium",
    "def binary_to_decimal(s: str) -> int:",
    "Convert a binary string s (only '0' and '1') to its decimal integer value, without using int(s, 2).",
    "def binary_to_decimal(s: str) -> int:\n    v = 0\n    for c in s:\n        v = v * 2 + (1 if c == '1' else 0)\n    return v\n",
    [(["1010"], 10), (["0"], 0), (["1111"], 15), (["100000"], 32), (["1101101"], 109)])

add("decimal-to-binary", "Decimal to binary", "strings", "medium",
    "def decimal_to_binary(n: int) -> str:",
    "Convert a non-negative integer n to its binary string without leading zeros, without using bin(). decimal_to_binary(0) = '0'.",
    "def decimal_to_binary(n: int) -> str:\n    if n == 0:\n        return '0'\n    s = ''\n    while n > 0:\n        s = str(n % 2) + s\n        n //= 2\n    return s\n",
    [([10], "1010"), ([0], "0"), ([1], "1"), ([15], "1111"), ([109], "1101101"), ([255], "11111111")])

add("bubble-sort", "Bubble sort", "lists", "medium",
    "def bubble_sort(xs: list) -> list:",
    "Sort the list of numbers xs in ascending order using the bubble sort algorithm and return the sorted list. Do not use sorted() or list.sort().",
    "def bubble_sort(xs: list) -> list:\n    a = list(xs)\n    n = len(a)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if a[j] > a[j + 1]:\n                a[j], a[j + 1] = a[j + 1], a[j]\n    return a\n",
    [([[5, 1, 4, 2, 8]], [1, 2, 4, 5, 8]), ([[]], []), ([[1]], [1]), ([[3, 2, 1]], [1, 2, 3]), ([[1, 1, 1]], [1, 1, 1]), ([[-1, -5, 3]], [-5, -1, 3])])

add("linear-search", "Linear search", "lists", "easy",
    "def linear_search(xs: list, target: int) -> int:",
    "Return the index of the first occurrence of target in the list xs, or -1 if it is not present.",
    "def linear_search(xs: list, target: int) -> int:\n    for i, x in enumerate(xs):\n        if x == target:\n            return i\n    return -1\n",
    [([[1, 2, 3], 2], 1), ([[5, 7, 9], 4], -1), ([[], 1], -1), ([[9], 9], 0), ([[1, 3, 5, 7], 7], 3)])

add("binary-search", "Binary search", "lists", "medium",
    "def binary_search(xs: list, target: int) -> int:",
    "The list xs is sorted in ascending order. Return the index of target using binary search, or -1 if it is not present.",
    "def binary_search(xs: list, target: int) -> int:\n    lo, hi = 0, len(xs) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if xs[mid] == target:\n            return mid\n        if xs[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n",
    [([[1, 3, 5, 7, 9], 7], 3), ([[1, 3, 5, 7, 9], 4], -1), ([[2], 2], 0), ([[], 1], -1), ([[1, 2, 3, 4, 5, 6], 1], 0)])

add("matrix-addition", "Matrix addition", "matrices", "medium",
    "def matrix_add(a: list, b: list) -> list:",
    "Given two matrices (lists of lists of numbers) with the same dimensions, return their element-wise sum.",
    "def matrix_add(a: list, b: list) -> list:\n    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]\n",
    [([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], [[6, 8], [10, 12]]), ([[[0]], [[0]]], [[0]]),
     ([[[-1, 2]], [[1, -2]]], [[0, 0]]), ([[[1, 2, 3]], [[4, 5, 6]]], [[5, 7, 9]])])

add("transpose", "Matrix transpose", "matrices", "medium",
    "def transpose(m: list) -> list:",
    "Return the transpose of the matrix m (a list of lists of numbers).",
    "def transpose(m: list) -> list:\n    return [list(row) for row in zip(*m)]\n",
    [([[[1, 2, 3], [4, 5, 6]]], [[1, 4], [2, 5], [3, 6]]), ([[[1]]], [[1]]),
     ([[[1, 2], [3, 4]]], [[1, 3], [2, 4]])])

add("word-count", "Word count", "strings", "easy",
    "def word_count(s: str) -> int:",
    "Return the number of whitespace-separated words in s. Empty or all-whitespace strings have 0 words.",
    "def word_count(s: str) -> int:\n    return len(s.split())\n",
    [(["hello world"], 2), (["  a  b c "], 3), ([""], 0), (["one"], 1), (["the quick brown fox"], 4)])

add("power", "Power (repeated multiplication)", "recursion", "medium",
    "def power(x: float, n: int) -> float:",
    "Return x raised to the non-negative integer power n, without using ** or pow().",
    "def power(x: float, n: int) -> float:\n    r = 1\n    for _ in range(n):\n        r *= x\n    return r\n",
    [([2, 10], 1024), ([5, 0], 1), ([3, 3], 27), ([2, 1], 2), ([7, 2], 49), ([1.5, 2], 2.25)])

def main():
    out = ROOT / "problems"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    for i, p in enumerate(P, 1):
        pid = f"{i:03d}"
        d = out / f"{pid}-{p['slug']}"
        d.mkdir()
        fn = p["signature"].split("(")[0].replace("def ", "").strip()
        (d / "problem.json").write_text(json.dumps({
            "id": pid, "slug": p["slug"], "title": p["title"], "topic": p["topic"],
            "difficulty": p["difficulty"], "language": "python",
            "function": {"name": fn, "signature": p["signature"]},
            "statement": p["statement"], "tests": p["tests"],
        }, indent=2) + "\n")
        (d / "canonical.py").write_text(p["canonical"])
    print(f"wrote {len(P)} problems")

if __name__ == "__main__":
    main()
