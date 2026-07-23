_tasks: dict[int, dict[str, object]] = {}
_next_id = 1


def list_tasks(completed: bool | None = None) -> list[dict[str, object]]:
    return [
        dict(task)
        for task in _tasks.values()
        if completed is None or task["completed"] is completed
    ]


def create_task(title: str, description: str = "") -> dict[str, object]:
    global _next_id

    task: dict[str, object] = {
        "id": _next_id,
        "title": title,
        "description": description,
        "completed": False,
    }
    _tasks[_next_id] = task
    _next_id += 1
    return dict(task)


def get_task(task_id: int) -> dict[str, object]:
    task = _tasks.get(task_id)
    if task is None:
        return _not_found(task_id)
    return dict(task)


def update_task(task_id: int, completed: bool) -> dict[str, object]:
    task = _tasks.get(task_id)
    if task is None:
        return _not_found(task_id)
    task["completed"] = completed
    return dict(task)


def delete_task(task_id: int) -> dict[str, object]:
    task = _tasks.pop(task_id, None)
    if task is None:
        return _not_found(task_id)
    return {"deleted": True, "task": dict(task)}


def _not_found(task_id: int) -> dict[str, object]:
    return {
        "error": {
            "code": "TASK_NOT_FOUND",
            "message": f"Task {task_id} does not exist.",
        }
    }
