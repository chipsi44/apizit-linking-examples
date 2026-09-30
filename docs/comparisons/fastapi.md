# APIZIT Linking vs FastAPI: choose your API contract

Choose APIZIT Linking when a separate manifest should adapt ordinary Python functions to HTTP. Choose FastAPI directly when its request models, dependencies, security integration and response contracts belong in your application architecture.

The Linking 1.0 stable release offers an optional FastAPI adapter. The distinction is between a declarative binding contract and direct use of FastAPI's features.

## Compare the same business function

Save this independent function in `greeting.py`:

```python
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
```

Linking declares HTTP outside that module:

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

Install `apizit-linking[preview,models]==1.0.1`, validate and start preview. `GET /hello/Ada` returns HTTP 200 with `{"message": "Hello, Ada!"}`.

A direct FastAPI adapter lives in `app.py`:

```python
from fastapi import FastAPI
from greeting import hello

app = FastAPI()

@app.get("/hello/{name}")
def hello_route(name: str) -> dict[str, str]:
    return hello(name)
```

Both service layers remain plain Python. Linking changes where the mapping is declared and which component owns input resolution.

## Compare the contracts

| Decision | APIZIT Linking 1.0 stable release | Direct FastAPI |
| --- | --- | --- |
| HTTP interface | YAML or JSON referencing `module:function` | Python path-operation registration |
| Business imports | No Linking or framework import required | Separate service modules need no framework import |
| Request input | Legacy conversion or opt-in nested typed models and explicit sources | Models, constraints and dependency injection |
| OpenAPI | Generated 3.1 document from the compiled Linking contract | Generated from operations and models |
| Return annotations | Documentary by default; explicit typed validation can serialize and filter | Response models can validate, serialize and filter |
| Binding errors | Documented structured 400 errors | Framework validation commonly returns 422 |
| Scope | Focused binding layer and optional adapter | Broader HTTP application features |

FastAPI documents [APIRouter for modular applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) and [response models](https://fastapi.tiangolo.com/tutorial/response-model/). Both can make projects and contracts easier to inspect.

## What can an assistant inspect?

Linking supplies the manifest, signatures, diagnostics and compiled route records. An assistant can work on behavior first and binding second, then run `validate --json`.

FastAPI supplies Python declarations, models, router registration and OpenAPI. An assistant can inspect these alongside conventions and tests. Neither approach guarantees correct code or that a model selects the right files.

Use separation when it matches your workflow. Context or speed improvements require measurement rather than general claims about AI.

## Choose Linking when reuse leads the design

A function can remain callable from a script, job, test and adapter without receiving a request object or returning a framework response. The manifest makes that boundary explicit.

The [validator]({{docs}}/reference/cli/) checks supported targets and signatures before imports. Preview imports and runs the project; review code before executing it.

## Choose FastAPI when its features matter

Direct FastAPI fits teams that prefer its Python operations, native dependency/security system, model integration and mature ecosystem. A well-organized existing app can already offer a clear service boundary.

Linking 1.0 supplies explicit typed models, providers, guards, response statuses/headers and domain-error mappings through its manifest and composition module. Its native boundary remains different from FastAPI's decorators and Depends. Legacy return schemas remain documentary; typed routes enforce their declared model. Streaming and WebSockets have no portable Linking contract in this release.

## Try one real operation

Compare successful inputs, missing values, unsupported types, domain exceptions and output contracts. Include an operation that needs more than a greeting if your project does.

The [business logic guide]({{docs}}/guides/keep-python-business-logic-independent-from-fastapi/) demonstrates tests and explicit JSON body binding. Follow [AI-assisted development]({{docs}}/guides/ai-assisted-development/) and [fit and limits]({{docs}}/limits/#choose) before deciding.

## Evaluate more than a greeting

Try [the same persistent operation]({{docs}}/guides/persistent-api/) with both designs: nested input, declared output, owner-scoped lookup, a transaction and domain errors. Compare organization, migration effort and the checks your team needs. The release microbenchmark is a local ASGI scalar test, not evidence of a speed advantage. Linking's reason to choose it is the separate inspectable contract, not a claim that FastAPI is hard for an agent to understand.
