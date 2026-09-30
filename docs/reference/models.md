# Typed request and response models

Add `validation: typed` when annotations should enforce the request and response contract. The optional `models` extra prepares Pydantic adapters at startup; static validation still never imports your project.

## Prerequisites

Install `apizit-linking[preview,models]==1.0.0rc1` with Python 3.10–3.14. Save this business module as `service.py`:

```python
from pydantic import BaseModel, Field

class Details(BaseModel):
    label: str = Field(min_length=2, max_length=40)

class TaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    details: Details

class TaskOutput(BaseModel):
    id: int
    title: str
    details: Details

def create(payload: TaskInput) -> TaskOutput:
    return {"id": 1, **payload.model_dump(), "internal_owner": "private"}
```

## Bind a whole JSON body

```yaml
version: 1
routes:
  - path: /tasks
    method: POST
    function: service:create
    validation: typed
    parameters:
      payload:
        source: {location: body, name: payload, pointer: ""}
    response: {status: 201, headers: {Location: "/tasks/{id}"}}
```

Run `apizit-linking validate . --json`, then `apizit-linking preview . --port 8080`. Validation warns that models require runtime preparation; it does not instantiate them. POST `{"title":"Read docs","details":{"label":"Work"}}` to `/tasks`. Expect 201, `Location: /tasks/1`, and JSON containing id, title and details. The undeclared `internal_owner` field is filtered by TaskOutput. A one-character label returns 400 with `INVALID_MODEL` and a path such as `payload.details.label`.

## Pointers and supported annotations

`pointer: /task/details` selects a nested value; `/items/0` selects an array element. Escape `~` as `~0` and `/` as `~1`. Missing values follow required/default rules; they never fall back to a query or header. Empty pointer selects the root, including arrays or null. A whole-body `list[TaskInput]` can therefore validate a batch.

Pydantic models, stdlib dataclasses, collections, unions, Optional, Literal, UUID, date and datetime use the installed Pydantic version's validation and serialization rules. This is an adapter choice, not a promise that an arbitrary annotation is portable to every future backend. Imports and unresolved annotations fail preparation before serving.

## Response and schema guarantees

The declared return annotation prepares output validation, JSON serialization and OpenAPI's serialization schema. Any or a missing annotation supplies no filtering guarantee. Dataclass and model fields can contain their own constraints. Pydantic configuration controls aliases, extra fields, coercion, serializers and trusted-instance revalidation. For mutable returned model instances, set `revalidate_instances="always"` when constraints must be rechecked. Invalid outputs become a generic 500; their content is not returned.

Use `export --resolve-models` for a contract containing prepared OpenAPI. Static `validate` cannot establish the behavior of custom validators. Nested pointers appear in an OpenAPI extension, and their outer JSON shape is left unconstrained. See [HTTP responses]({{docs}}/reference/responses/), [the persistent example]({{docs}}/guides/persistent-api/) and [controlled AI changes]({{docs}}/guides/ai-assisted-development/).
