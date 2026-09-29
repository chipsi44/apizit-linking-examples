# Keep Python business logic independent from FastAPI

A web framework should not have to own your domain function. With APIZIT Linking, the Python module calculates a result using ordinary values, while YAML declares how HTTP path, query, header, or body fields become function arguments.

<a id="boundary"></a>

## The boundary to preserve

Framework coupling usually starts when a business function accepts a request object, raises `HTTPException`, returns a framework response, or carries a route decorator. Those choices make the same logic harder to call from a script, a worker, a test, or another adapter.

For this guide, the project remains only two files:

```text
pricing-api/
├── apizit_linking.yaml
└── pricing.py
```

APIZIT Linking uses FastAPI only in its optional preview adapter. Your business module does not import FastAPI or APIZIT Linking.

<a id="business-function"></a>

## 1. Write and test the business function

Create `pricing.py`:

```python
def calculate_total(
    unit_price: float,
    quantity: int,
    tax_rate: float = 0.21,
) -> dict[str, float | int]:
    subtotal = round(unit_price * quantity, 2)
    tax = round(subtotal * tax_rate, 2)
    return {
        "quantity": quantity,
        "unit_price": unit_price,
        "subtotal": subtotal,
        "tax": tax,
        "total": round(subtotal + tax, 2),
    }
```

This function knows about prices, quantities, and tax. It does not know about HTTP. Test it directly before adding any route:

```text
python -c "from pricing import calculate_total; assert calculate_total(12.5, 2)['total'] == 30.25"
```

That same import remains valid in a unit test, command-line job, notebook, or queue worker. HTTP is a caller, not the center of the module.

<a id="http-binding"></a>

## 2. Add HTTP binding outside the code

Create `apizit_linking.yaml`. Each body field maps explicitly to one Python parameter:

```yaml
version: 1

runtime:
  language: python
  version: "3.12"

routes:
  - path: /quotes
    method: POST
    function: pricing:calculate_total
    parameters:
      unit_price:
        source:
          location: body
          name: unit_price
      quantity:
        source:
          location: body
          name: quantity
      tax_rate:
        source:
          location: body
          name: tax_rate
```

`unit_price` and `quantity` are required because the Python signature has no defaults. `tax_rate` is optional: when the JSON field is absent, APIZIT Linking omits the keyword and Python applies `0.21`.

Type hints drive the supported primitive conversions. For example, the JSON string `"2"` can become an integer, but a non-integer value produces a structured request error before the function is invoked.

<a id="run"></a>

## 3. Validate and run the API

Install the 0.5.0 preview extra, validate the static contract, then start the local server:

```text
python -m pip install "apizit-linking[preview]==0.5.0"
apizit-linking validate .
apizit-linking preview . --port 8080
```

Validation should report one compiled route. In another terminal, send a JSON object:

```text
curl -X POST "http://127.0.0.1:8080/quotes" \
  -H "Content-Type: application/json" \
  -d '{"unit_price":12.5,"quantity":2}'
```

Expected response (`200 OK`):

```json
{
  "quantity": 2,
  "unit_price": 12.5,
  "subtotal": 25.0,
  "tax": 5.25,
  "total": 30.25
}
```

Send `{"unit_price":12.5,"quantity":"many"}` and the adapter returns `400 Bad Request` with error code `INVALID_PARAMETER`. The pricing function is not called.

<a id="why"></a>

## Why the separation matters

| Concern | Python module | Linking YAML / adapter |
| --- | --- | --- |
| Business calculation | Owns it | Does not duplicate it |
| Route and HTTP method | Unaware | Declares it |
| Request source | Receives ordinary values | Maps body, query, path, header, form, or file |
| Local server | No server dependency | Optional preview extra |
| Unit testing | Direct function call | Separate integration tests |

This design also keeps deployment choices open. APIZIT can consume the compiled linking contract, while another platform can use the standalone package and optional FastAPI adapter. Neither choice requires a decorator in `pricing.py`.

<a id="v1-limits"></a>

## Where V1 stops

Keeping business exceptions framework-independent is good architecture, but V1 does not yet map them to HTTP responses. Do not return an `{"error": ...}` dictionary and describe it as a 4xx response: without response-status support, it is still an HTTP 200.

- V1 cannot declare `201`, `204`, `404`, custom headers, or a configurable response schema. The minimal schema inferred for OpenAPI is documentary and is not enforced at runtime.
- An unhandled domain exception becomes a generic `500` in preview; stable business-exception mapping is future work.
- JSON input must be an object and bindings address top-level fields. Nested selectors and rich constraints are not available.
- Unknown custom annotations are passed through rather than instantiated as domain or validation models.
- The preview is for development. Authentication, metering, and production isolation belong to a platform adapter.

Keep domain errors as ordinary Python exceptions or result types, test them directly, and consult the [V1 limits]({{docs}}/limits/) before exposing operations that require precise HTTP semantics.

## Related resources {#related-resources}

- [Runnable examples]({{docs}}/examples/), including JSON body and request-error projects.
- [YAML reference]({{docs}}/reference/linking-yaml/) for explicit and automatic parameter sources.
- [CLI reference]({{docs}}/reference/cli/) for `validate` and `preview`.
- [APIZIT Linking on PyPI](https://pypi.org/project/apizit-linking/).
- [Source for the public examples](https://github.com/chipsi44/apizit-linking-examples).

## Use this boundary with an AI assistant

Ask your assistant to work on the Python behavior first: inputs, return value and domain cases. Review or run those function tests before adding an HTTP route. Then provide the function signature and the intended method, path and parameter sources as a separate task. This keeps the business decision and the HTTP mapping explicit for both the assistant and the reviewer.

Validate the proposed manifest with JSON diagnostics, inspect the affected module:function targets and preview the request cases. Static validation checks supported contracts; it does not prove business correctness or execute the function. Preview imports the project and must only run code you trust. The architecture makes these boundaries inspectable, but lower token usage, faster work and fewer mistakes would need measurement for your own workflow.

Follow the [AI-assisted development guide]({{docs}}/guides/ai-assisted-development/) for the complete sequence. For debugging, [trace a route back to Python]({{docs}}/guides/trace-route-to-python/). Compare [Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/) when you need a different HTTP contract.
