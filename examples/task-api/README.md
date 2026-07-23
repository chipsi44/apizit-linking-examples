# Task API

A small but realistic CRUD-style API. Its business functions know nothing
about HTTP frameworks: the linking file exposes the same Python module through
five routes.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/tasks` | List tasks, optionally filtered by `completed` |
| `POST` | `/tasks` | Create a task from a JSON body |
| `GET` | `/tasks/{task_id}` | Fetch one task |
| `PATCH` | `/tasks/{task_id}` | Update the `completed` field |
| `DELETE` | `/tasks/{task_id}` | Delete one task |

## Validate, test, and run

From the repository root:

```text
apizit-linking validate examples/task-api
apizit-linking preview examples/task-api --port 8080
python -m unittest tests.test_examples.ExampleProjectHttpTests.test_task_crud_lifecycle -v
```

Create a task:

```text
curl -X POST http://127.0.0.1:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write examples","description":"Cover the V1 features"}'
```

Expected response in a fresh process (`200 OK`):

```json
{
  "id": 1,
  "title": "Write examples",
  "description": "Cover the V1 features",
  "completed": false
}
```

List incomplete tasks:

```text
curl "http://127.0.0.1:8080/tasks?completed=false"
```

Update, fetch, then delete the task:

```text
curl -X PATCH http://127.0.0.1:8080/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
curl http://127.0.0.1:8080/tasks/1
curl -X DELETE http://127.0.0.1:8080/tasks/1
```

The delete response is:

```json
{
  "deleted": true,
  "task": {
    "id": 1,
    "title": "Write examples",
    "description": "Cover the V1 features",
    "completed": true
  }
}
```

## Limitations

The store is process-local memory. It resets when preview restarts and is not
safe persistence for concurrent or production use.

V1 returns `200` for every successful business result and cannot yet declare
`201`, `204`, or map a missing task to HTTP `404` without coupling business
code to a web framework. A missing task is therefore an application-level
error object transported with HTTP `200`.
