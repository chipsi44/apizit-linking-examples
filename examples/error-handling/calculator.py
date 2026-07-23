def divide(dividend: float, divisor: float) -> dict[str, float]:
    if divisor == 0:
        raise ValueError("divisor must not be zero")
    return {
        "dividend": dividend,
        "divisor": divisor,
        "result": dividend / divisor,
    }
