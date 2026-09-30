# APIZIT Linking vs Flask: choose your HTTP boundary

Choose APIZIT Linking when you want to expose ordinary Python functions through a separate, versioned HTTP manifest. Choose Flask when you want its general web application model and need its HTTP features.

Both can support a clean service layer. This comparison concerns where you declare the interface and what the Linking 1.0 candidate covers, rather than which framework is universally better.

## Compare the same operation

Keep the business behavior in `greeting.py`:

```python
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
```

With Linking, the mapping lives in `apizit_linking.yaml`:

```yaml
version: 1
routes:
  - path: /hello/{name}
    method: GET
    function: greeting:hello
    parameters:
      name:
        source:
          location: path
          name: name
```

Install `apizit-linking[preview,models]==1.0.0rc1`, run `apizit-linking validate .` and start `apizit-linking preview . --port 8080`. `GET /hello/Ada` returns HTTP 200 and `{"message": "Hello, Ada!"}`.

With Flask, a separate `app.py` adapts the same function:

```python
from flask import Flask
from greeting import hello

app = Flask(__name__)

@app.get("/hello/<name>")
def hello_route(name):
    return hello(name)
```

The business module is equally reusable. Flask's registration is Python; Linking's is an external manifest. Neither example puts HTTP inside `hello`.

## Compare maintenance decisions

| Decision | APIZIT Linking 1.0 candidate | Flask |
| --- | --- | --- |
| Business functions | Linked directly from a manifest | Can be called from separate handlers |
| Route declaration | Versioned YAML or JSON | Decorators or Python registration |
| Route investigation | Manifest method, pattern and `module:function` | Registered route map, endpoint and project layout |
| Static Linking validation | Checks targets and bindings without imports | Depends on project tools and tests |
| Response flexibility | Explicit success status/headers and domain-error mappings; optional typed output | Application code can choose statuses, headers and response behavior |
| Broader application needs | Focused Python-to-HTTP scope | Templates, sessions, hooks and extensions |

Flask supports [blueprints](https://flask.palletsprojects.com/en/stable/blueprints/) and an inspectable route map. Its [API reference](https://flask.palletsprojects.com/en/stable/api/) documents registration and responses. Calling Flask impossible to navigate would be inaccurate.

## What changes for an AI workflow?

An assistant using Linking can implement and test `hello`, then receive a separate task to declare its mapping. When a request identifies a route, the manifest points to its intended function.

An assistant using Flask can work on a service module and handler with the same separation. Good conventions, blueprints and tests can make that workflow clear. Linking supplies one convention by default: the external binding map.

This is an architectural reason to consider it, not evidence that an assistant writes faster or uses fewer tokens. Measure those effects on representative tasks if they matter.

## Choose Linking for a function-centered project

It is a candidate when you maintain tested library, calculation or domain functions and want HTTP to remain one way of calling them. Exposure and source changes can be reviewed separately.

Run the [quickstart]({{docs}}/quickstart/) and [examples]({{docs}}/examples/). Verify your required statuses, input types and security layer before adopting it.

## Choose Flask for a broader application

Use Flask directly when templates, sessions, extensions, request hooks or flexible HTTP responses are central. An established Flask app does not need rewriting merely because a manifest is convenient.

Linking preview uses FastAPI internally and does not implement every Flask feature. Named guards and injected principals implement an application-defined authentication/authorization boundary. Linking supplies lifecycle hooks; production operations and identity services still belong to the application or hosting adapter.

## Verify one representative route

Keep the operation's direct Python tests and compare the interfaces. Exercise normal responses, invalid inputs, domain failures and required response statuses. If V1 lacks an essential requirement, that is useful evidence for choosing Flask.

Continue with [the AI workflow]({{docs}}/guides/ai-assisted-development/), [route diagnosis]({{docs}}/guides/trace-route-to-python/), [FastAPI]({{docs}}/comparisons/fastapi/) and [fit and limits]({{docs}}/limits/#choose).

## Compare a protected persistent operation

The [SQLite guide]({{docs}}/guides/persistent-api/) demonstrates nested models, request resources, owner permissions and 201/204/404/409. Flask can implement the same behavior with handlers, application extensions and a service layer. Keep the successful operation equivalent and compare the declared boundary, tests and maintenance effort. No universal token, reliability or speed gain is established by the architectural difference.
