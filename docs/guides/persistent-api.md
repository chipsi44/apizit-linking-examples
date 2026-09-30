# Build a persistent API with models and permissions


Evaluate the exact `1.0.0rc1` candidate installed by the repository requirements.
The persistent example demonstrates a complete local JSON API without an APIZIT account: nested input/output models, SQLite transactions, bounded pagination, writer/reader permissions, owner-scoped lookup and meaningful HTTP statuses.

## Prerequisites and files

Use Python 3.10–3.14 and a durable local filesystem. Clone or fork [the examples](https://github.com/chipsi44/apizit-linking-examples), create a virtual environment and install the root requirements. Open `examples/persistent-api/`: service.py contains business operations/models, bootstrap.py contains credentials/resources/guards, and apizit_linking.yaml contains HTTP policy. The business module imports neither Linking nor FastAPI.

## Configure local development credentials

Choose distinct development keys, keep them in your shell environment and use a disposable database. PowerShell:

```powershell
$env:LINKING_DEMO_DATABASE = Join-Path (Get-Location) "tasks.sqlite"
$env:LINKING_DEMO_WRITER_KEY = "replace-with-local-writer-key"
$env:LINKING_DEMO_READER_KEY = "replace-with-local-reader-key"
```

POSIX shell:

```sh
export LINKING_DEMO_DATABASE="$PWD/tasks.sqlite"
export LINKING_DEMO_WRITER_KEY="replace-with-local-writer-key"
export LINKING_DEMO_READER_KEY="replace-with-local-reader-key"
```

Values above are placeholders, not deployed credentials. The factory rejects empty or equal keys. An optional distinct LINKING_DEMO_OTHER_KEY exercises a second owner. Start the server from the example directory:

```text
apizit-linking validate . --json
apizit-linking preview . --port 8080
```

Static validation does not need these environment values; runtime factory preparation does.

## Create and retrieve a task

```python
import json
import os
from urllib.request import Request, urlopen

request = Request(
    "http://127.0.0.1:8080/tasks",
    data=json.dumps({"title": "Read docs", "details": {"label": "Work"}}).encode(),
    headers={"Content-Type": "application/json", "X-API-Key": os.environ["LINKING_DEMO_WRITER_KEY"]},
    method="POST",
)
with urlopen(request) as response:
    assert response.status == 201
    task = json.load(response)
    assert response.headers["Location"] == f"/tasks/{task['id']}"
    assert "owner" not in task
print(task)
```

Expect id, title and nested details. GET `/tasks/{id}` with the reader key returns 200. Stop the entire server and start it again with the same database path: the task remains. Request-scoped connections commit on success, roll back on error and close after each request. The unique owner/title constraint becomes 409 through an explicit domain exception mapping.

## List tasks with bounded pagination

GET `/tasks?limit=20&offset=0` with the reader key returns an array of that owner's tasks ordered by id. The Python signature sets defaults and Pydantic constraints: limit is 1–100 and offset is 0–1,000,000. The manifest binds both parameters to query values. Invalid numbers return 400 before the business query executes; another owner receives only their own rows. Output models filter private fields from every item.

```python
from urllib.request import Request, urlopen
import json
import os

request = Request(
    "http://127.0.0.1:8080/tasks?limit=20&offset=0",
    headers={"X-API-Key": os.environ["LINKING_DEMO_READER_KEY"]},
)
with urlopen(request) as response:
    assert response.status == 200
    tasks = json.load(response)
    assert len(tasks) <= 20
    assert all("owner" not in task for task in tasks)
print(tasks)
```

Offset pagination is suitable for this small example. For large or frequently changing datasets, choose an indexed cursor strategy and an application-level query budget.

## Exercise permission and error boundaries

| Request | Expected outcome |
| --- | --- |
| Missing/wrong key | 401 |
| Reader key on POST/PATCH/DELETE | 403 |
| Another owner's key on an existing task | 404 |
| Duplicate title for the same owner | 409 |
| A one-character nested label | 400 with a field error |
| limit=0, limit=101 or negative offset | 400 with a field error |
| Valid POST | 201 and Location |
| Valid PATCH | 200 |
| Valid DELETE | 204, empty body |
| GET after deletion | 404 |
| Unknown URL / unsupported method | Real 404 / 405 |

Run `python -m unittest discover -s tests` at the examples root for automated checks. The release qualification additionally exercises an actual TCP server and process restart, not only app reconstruction.

## Limits and next steps

This demonstration uses development keys, a simple SQLite schema and a local durable filesystem. It provides no production identity provider, schema migration system, backup policy or managed durable volume. Do not infer APIZIT storage guarantees from it. Select database and deployment controls for your environment. Continue with [resource lifecycle]({{docs}}/reference/resources-and-permissions/), [models]({{docs}}/reference/models/), [HTTP errors]({{docs}}/reference/responses/) and [standalone serving]({{docs}}/guides/standalone-serving/).
