# HTTP responses and business errors

Declare status, headers and public business errors in the route manifest. Keep the function callable directly; the adapter translates its result or exception at the HTTP boundary.

## An executable creation route

Save `service.py`:

```python
class Conflict(Exception):
    pass

def create(title: str) -> dict[str, str | int]:
    if title == "existing":
        raise Conflict("Private database detail")
    return {"id": 1, "title": title}
```

```yaml
version: 1
routes:
  - path: /tasks
    method: POST
    function: service:create
    parameters:
      title:
        source: {location: body, name: title}
    response: {status: 201, headers: {Location: "/tasks/{id}"}}
    errors:
      - exception: Conflict
        status: 409
        code: TASK_EXISTS
        message: A task with that title already exists
```

Validate and preview after installing the candidate. POST `{"title":"Read docs"}` and expect 201 with `Location: /tasks/1`. POST `{"title":"existing"}` and expect 409 with an `error` object containing the declared code and message. The private exception text is absent. An unconfigured exception becomes a generic JSON 500.

## Status and headers

Success status must be an integer from 200 to 299. Default is 200. `204`, `205` and HEAD omit the response body. A headers object maps valid header names to strings. Templates accept only flat returned fields such as `{id}`; attribute/index traversal, format conversions and CR/LF/NUL are rejected. Missing fields fail safely. Encode URL components in your application when needed; formatting is not URL escaping.

## Exception mapping and custom responses

An exception must name an Exception subclass visible in the function module or builtins. Startup rejects unknown exceptions; duplicate names and unknown policy fields fail static validation. Mappings execute in listed order, so place specific subclasses before broad classes. Public status must be 400–599, and code/message are constant strings. Resource context managers receive the original error before it is mapped, allowing rollback.

For ASGI-specific behavior, declare `response.adapter: name` and register a callback in RuntimeExtensions.responses. It receives `(result, context)`, must return an ASGI Response with the declared status, and owns serialization and content-specific documentation. Typed output validation happens before the adapter. Cookies, streaming and content negotiation have no portable declarative policy in this release.

Missing/invalid inputs use 400; guards use 401 or 403; opt-in request limits use 413/503/504. Framework 404/405 and the declared domain mappings preserve their HTTP meaning. See [models]({{docs}}/reference/models/) and [resources and permissions]({{docs}}/reference/resources-and-permissions/).
