# Turn a Python library into an API with YAML

If a library already exposes top-level functions with supported signatures, APIZIT Linking can connect them to HTTP routes by dotted module name. The package remains ordinary Python; YAML owns the method, path, and request-field mapping.

<a id="fit"></a>

## When a library is a good fit

The simplest target is a top-level function that accepts ordinary keyword arguments and returns JSON-serializable data. The function can live in a dotted package, call sibling modules, and perform imports lazily during invocation.

This guide exposes a small catalogue package:

```text
catalog-api/
├── apizit_linking.yaml
└── catalog/
    ├── __init__.py
    ├── pricing.py
    └── service.py
```

No module imports FastAPI, Starlette, or APIZIT Linking. The same package remains importable by Python tools that never start an HTTP server.

<a id="library"></a>

## 1. Create the Python package

Add an empty `catalog/__init__.py`, then create `catalog/pricing.py`:

```python
def base_price_for(product_id: int) -> float:
    return round(10.0 + product_id * 1.5, 2)

def apply_discount(price: float, discount: float) -> float:
    if not 0 <= discount <= 100:
        raise ValueError("discount must be between 0 and 100")
    return round(price * (1 - discount / 100), 2)
```

Create `catalog/service.py`:

```python
def quote(product_id: int, discount: float = 0.0) -> dict[str, float | int]:
    from .pricing import apply_discount, base_price_for

    base_price = base_price_for(product_id)
    return {
        "product_id": product_id,
        "base_price": base_price,
        "discount": discount,
        "final_price": apply_discount(base_price, discount),
    }
```

The relative import occurs inside `quote`. APIZIT Linking 0.5.0 keeps a project-private import namespace available during invocation, so this normal lazy package import resolves without placing the project root permanently on `sys.path`.

Before adding HTTP, check the library directly:

```text
python -c "from catalog.service import quote; assert quote(7, 10)['final_price'] == 18.45"
```

<a id="manifest"></a>

## 2. Declare the HTTP route in YAML

Create `apizit_linking.yaml` at the project root. The function target uses canonical `module:function` syntax:

```yaml
version: 1

runtime:
  language: python
  version: "3.12"

routes:
  - path: /products/{product_id}/quote
    method: GET
    function: catalog.service:quote
    parameters:
      product_id:
        source:
          location: path
          name: product_id
      discount:
        source:
          location: query
          name: discount
```

The path value is converted to `int`, and the query value is converted to `float` using the function annotations. Because `discount` defaults to `0.0`, the query field can be omitted.

`runtime.version` validates the declared Python minor-version syntax; the local preview does not install or switch Python interpreters for you.

<a id="verify"></a>

## 3. Validate and call the API

Install the preview extra and run the static compiler:

```text
python -m pip install "apizit-linking[preview]==0.5.0"
apizit-linking validate .
```

Validation resolves `catalog/service.py` inside the project root and checks the top-level `quote` signature using the Python AST. It does not execute `catalog`.

Start the local server:

```text
apizit-linking preview . --port 8080
```

Request a ten-percent discount for product 7:

```text
curl "http://127.0.0.1:8080/products/7/quote?discount=10"
```

Expected response (`200 OK`):

```json
{
  "product_id": 7,
  "base_price": 20.5,
  "discount": 10.0,
  "final_price": 18.45
}
```

The complete public gallery includes this same pattern as a [runnable multi-module example]({{docs}}/examples/).

<a id="requirements"></a>

## Library compatibility checklist

A V1 target must satisfy these constraints:

- The target uses canonical `module:function` syntax and resolves to a file or package inside the project root.
- The linked function is defined at module scope and is callable at runtime.
- Parameters may be positional-or-keyword or keyword-only. Positional-only, `*args`, and `**kwargs` signatures are rejected.
- Request conversion is built in for strings, integers, finite floats, booleans, nullable unions, lists, and dictionaries.
- The optional HTTP adapter must be able to serialize the returned value. Ordinary dictionaries, lists, strings, numbers, booleans, and `None` are the clearest portable choices.
- Third-party dependencies used by the library must already be installed in the runtime environment. Linking does not install a project’s dependencies.

If an existing function has an incompatible signature or returns a domain-specific object, add a thin plain Python adapter function in your own package. That adapter can translate values without importing a web framework or modifying the underlying library.

<a id="limits"></a>

## V1 limits and the production boundary

The discount guard in this example raises `ValueError` for values outside 0–100. V1 does not map that business exception to a stable HTTP 4xx response; the local preview returns a generic 500. Only missing or invalid request bindings have a guaranteed structured 400 response.

- No declarative response status, response headers, or typed response contract.
- No nested JSON selector or rich domain-model validation.
- No authentication, authorization, rate limiting, metering, or deployment.
- Import namespaces prevent project-name collisions but do not sandbox trusted Python code.
- The preview binds to loopback by default and is a development tool, not a production server recommendation.

Review the [complete V1 limits]({{docs}}/limits/) and use a platform adapter when you need production infrastructure or policy.

## Continue learning {#continue}

- [YAML reference]({{docs}}/reference/linking-yaml/) for route and parameter-source rules.
- [CLI reference]({{docs}}/reference/cli/) for validation and preview options.
- [Example gallery]({{docs}}/examples/) for JSON body, errors, CRUD, and multi-module projects.
- [Install APIZIT Linking from PyPI](https://pypi.org/project/apizit-linking/).
- [Fork the public examples repository](https://github.com/chipsi44/apizit-linking-examples/fork).

## Use this boundary with an AI assistant

Ask your assistant to work on the Python behavior first: inputs, return value and domain cases. Review or run those function tests before adding an HTTP route. Then provide the function signature and the intended method, path and parameter sources as a separate task. This keeps the business decision and the HTTP mapping explicit for both the assistant and the reviewer.

Validate the proposed manifest with JSON diagnostics, inspect the affected module:function targets and preview the request cases. Static validation checks supported contracts; it does not prove business correctness or execute the function. Preview imports the project and must only run code you trust. The architecture makes these boundaries inspectable, but lower token usage, faster work and fewer mistakes would need measurement for your own workflow.

Follow the [AI-assisted development guide]({{docs}}/guides/ai-assisted-development/) for the complete sequence. For debugging, [trace a route back to Python]({{docs}}/guides/trace-route-to-python/). Compare [Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/) when you need a different HTTP contract.
