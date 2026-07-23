def base_price_for(product_id: int) -> float:
    return round(10.0 + product_id * 1.5, 2)


def apply_discount(price: float, discount: float) -> float:
    if not 0 <= discount <= 100:
        raise ValueError("discount must be between 0 and 100")
    return round(price * (1 - discount / 100), 2)
