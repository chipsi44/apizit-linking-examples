from sqlite3 import Connection, IntegrityError
from pydantic import BaseModel, Field


class Details(BaseModel):
    label: str = Field(min_length=2, max_length=40)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    details: Details


class TaskOut(BaseModel):
    id: int
    title: str
    details: Details


class Missing(Exception):
    pass


class Conflict(Exception):
    pass


def create(payload: TaskIn, database: Connection, user: str) -> TaskOut:
    try:
        cursor = database.execute(
            "INSERT INTO tasks(owner,title,label) VALUES (?,?,?)",
            (user, payload.title, payload.details.label),
        )
    except IntegrityError as error:
        raise Conflict("duplicate private database value") from error
    return {
        "id": cursor.lastrowid,
        "title": payload.title,
        "details": payload.details,
        "owner": user,
    }


def read(task_id: int, database: Connection, user: str) -> TaskOut:
    row = database.execute(
        "SELECT id,title,label,owner FROM tasks WHERE id=? AND owner=?", (task_id, user)
    ).fetchone()
    if row is None:
        raise Missing("private object information")
    return {"id": row[0], "title": row[1], "details": {"label": row[2]}, "owner": row[3]}


def update(task_id: int, payload: TaskIn, database: Connection, user: str) -> TaskOut:
    read(task_id, database, user)
    try:
        database.execute(
            "UPDATE tasks SET title=?,label=? WHERE id=? AND owner=?",
            (payload.title, payload.details.label, task_id, user),
        )
    except IntegrityError as error:
        raise Conflict("private SQL detail") from error
    return read(task_id, database, user)


def remove(task_id: int, database: Connection, user: str) -> None:
    read(task_id, database, user)
    database.execute("DELETE FROM tasks WHERE id=? AND owner=?", (task_id, user))
