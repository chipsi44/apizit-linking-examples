def create_product(
    name: str,
    price: float,
    in_stock: bool = True,
    tags: list[str] | None = None,
) -> dict[str, object]:
    return {
        "name": name,
        "price": price,
        "in_stock": in_stock,
        "tags": [] if tags is None else tags,
    }
