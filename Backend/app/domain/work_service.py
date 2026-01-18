

#Processing work that will be performed by both sync and async endpoints


def fibonacci_mod(n: int, mod: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % mod
    return a


def perform_work(payload: dict) -> dict:
    MAX_STORE_VALUE = 10**7

    number = payload["number"]

    result = fibonacci_mod(number, MAX_STORE_VALUE)

    return {
        "input": number,
        "output": result
    }