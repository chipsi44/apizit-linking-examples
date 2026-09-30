# Expose a Python function as an HTTP API without decorators

Put the HTTP route in YAML and leave the Python function alone. APIZIT Linking validates the connection, converts request values from type hints, and can run a local preview—without adding a FastAPI decorator, request object, or infrastructure import to your business code.

<a id="what-you-will-build"></a>

## What you will build

This two-file project exposes `hello:hello` as `GET /hello`. The optional `name` query parameter is passed to the ordinary Python function.

```text
hello-api/
├── apizit_linking.yaml
└── hello.py
```

The commands below use only the V1 contract retained by the Linking 1.0 stable release. For a reproducible deployment, pin the exact version you have tested.

<a id="plain-python"></a>

## 1. Write the plain Python function

Create `hello.py`. There is no APIZIT Linking or web-framework import:

```python
def hello(name: str = "world") -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
```

You can still import and test this function normally. It remains useful as Python code even when no HTTP server is running.

<a id="linking-yaml"></a>

## 2. Link the function with YAML

Create `apizit_linking.yaml` beside the module. The `module:function` target is `hello:hello`, and the YAML maps the external query field `name` to the function parameter of the same name.

```yaml
version: 1

runtime:
  language: python
  version: "3.12"

routes:
  - path: /hello
    method: GET
    function: hello:hello
    parameters:
      name:
        source:
          location: query
          name: name
```

Because `name` has a Python default, omitting it from the request leaves it out of the generated keyword arguments and Python applies `"world"`.

See the full [Linking YAML reference]({{docs}}/reference/linking-yaml/) for path, query, header, body, form, and file sources.

<a id="validate-preview"></a>

## 3. Validate and preview

From inside `hello-api`, use an activated Python environment and install the preview:

```text
python -m pip install "apizit-linking[preview,models]==1.0.1"
```

Then validate the project:

```text
apizit-linking validate .
```

The successful output ends with:

```text
APIZIT linking definition is valid: …/apizit_linking.yaml
Compiled routes: 1
```

Start the development preview on the loopback interface:

```text
apizit-linking preview . --port 8080
```

In another terminal, call the route:

```text
curl "http://127.0.0.1:8080/hello?name=Ada"
```

Expected response (`200 OK`):

```json
{"message":"Hello, Ada!"}
```

Calling `/hello` without the query string returns `{"message":"Hello, world!"}`.

<a id="how-it-works"></a>

## What happens at runtime

1. **Validation is static.** The compiler parses the YAML and Python AST, checks the route, module, top-level function, signature, and parameter binding, and does not import your module.
2. **Preview loads trusted code.** Only after validation succeeds does the preview import `hello.py` into an isolated project namespace.
3. **The adapter resolves inputs.** It reads `name` from the query string, converts supported annotated values, and invokes `hello(name=...)`.
4. **The return value is serialized.** The optional FastAPI adapter serializes the ordinary dictionary as JSON.

The HTTP framework is an adapter around the function, not a dependency inside it. That is the core separation APIZIT Linking provides.

<a id="v1-limits"></a>

## V1 limits you should know

This initial manifest uses legacy conversion and default 200. The 1.0 release can explicitly declare success statuses/headers, domain-error mappings, typed models and permission guards; each is a separate policy choice. Unmapped business errors return a generic JSON 500.

- The preview is a local development tool, not a production security boundary.
- Customer modules are trusted Python code; import isolation is not a sandbox.
- A binding without a pointer selects a top-level JSON field. Opt into JSON pointers and typed models when the input needs a nested contract.
- Legacy return schemas remain documentary. validation: typed prepares runtime input/output adapters and their OpenAPI schemas explicitly.

Read the complete [V1 limits]({{docs}}/limits/) before choosing a production adapter.

## Next steps {#next-steps}

- Install the package from [PyPI](https://pypi.org/project/apizit-linking/).
- Browse the [runnable examples]({{docs}}/examples/).
- Learn every command in the [CLI reference]({{docs}}/reference/cli/).
- Inspect or fork the [examples repository](https://github.com/chipsi44/apizit-linking-examples).

## Use this boundary with an AI assistant

Ask your assistant to work on the Python behavior first: inputs, return value and domain cases. Review or run those function tests before adding an HTTP route. Then provide the function signature and the intended method, path and parameter sources as a separate task. This keeps the business decision and the HTTP mapping explicit for both the assistant and the reviewer.

Validate the proposed manifest with JSON diagnostics, inspect the affected module:function targets and preview the request cases. Static validation checks supported contracts; it does not prove business correctness or execute the function. Preview imports the project and must only run code you trust. The architecture makes these boundaries inspectable, but lower token usage, faster work and fewer mistakes would need measurement for your own workflow.

Follow the [AI-assisted development guide]({{docs}}/guides/ai-assisted-development/) for the complete sequence. For debugging, [trace a route back to Python]({{docs}}/guides/trace-route-to-python/). Compare [Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/) when you need a different HTTP contract.
