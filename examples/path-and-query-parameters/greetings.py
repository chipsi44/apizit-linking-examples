def get_greeting(user_id: int, verbose: bool = False) -> dict[str, object]:
    result: dict[str, object] = {
        "user_id": user_id,
        "message": f"Hello, user {user_id}!",
    }
    if verbose:
        result["details"] = "The verbose query parameter is enabled."
    return result
