def quote(product_id: int, discount: float = 0.0) -> dict[str, float | int]:
    from .pricing import apply_discount, base_price_for

    base_price = base_price_for(product_id)
    return {
        "product_id": product_id,
        "base_price": base_price,
        "discount": discount,
        "final_price": apply_discount(base_price, discount),
    }
