# Trace an HTTP route back to Python

A Linking manifest maps HTTP methods and route patterns to Python functions. Use it to find the declared target before searching the rest of the project. An AI assistant and a human investigator can follow the same process.

This guide uses version 1.0.0rc1 and the [multi-module example](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/multi-module-api). You need Python 3.10–3.14 and a checkout of the example. No APIZIT account is required.

## Begin with the right evidence

Suppose an access log or bug report contains:

```text
GET /products/42/quote?discount=0.1
```

This line is illustrative. Linking does not promise a structured logging format or attach a Python file to every log. Collect method, path, relevant status or error and the application version that handled the request.

Use that release's manifest and source. A newer branch can point to code that did not run. Remove tokens, personal data and unnecessary request values before sharing logs with an assistant.

## Find the declared route

The example declares:

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

The actual path matches `/products/{product_id}/quote`. Match the method too: `POST` on the same path is a different operation. The query string supplies parameters rather than changing the pattern.

Check static siblings and the validator's ordering rules before assuming the first similar text match is selected. A specific `/products/search` can coexist with `/products/{product_id}`. Overlaps without a safe specificity order are rejected by the compiler.

## Follow the target into the project

`catalog.service:quote` names module `catalog.service` and top-level function `quote`. Here the module is `catalog/service.py`:

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

The function imports `catalog/pricing.py`, so that is the next relevant file. The map locates the entry point; it is not a complete call graph and does not establish a defect's cause.

Elsewhere a module can be a package with an `__init__.py`. Follow the actual layout and compiler resolution rather than assuming every dotted name ends in a module file.

## Inspect the request bindings

`product_id` comes from the path and `discount` from the query. The signature requires the ID and defaults discount to `0.0`.

Supported conversion produces integer `42` and float `0.1`. This example expresses discount as a percentage: `0.1` means 0.1%, and `10` means 10%. When discount is absent, Python applies its default. An explicit query binding does not fall back to a same-named body field.

For `INVALID_PARAMETER`, check the reported source, external name and expected type. If the function ran but returned an unexpected result, inspect the calculation and dependencies. Distinguish binding failures from domain behavior.

## Give an assistant a focused investigation

Provide the request, release identifier, matching entry, function and dependencies:

```text
Investigate GET /products/42/quote?discount=0.1 in this release.
The manifest maps it to catalog.service:quote.
Inspect that function, catalog/pricing.py and their relevant tests.
Explain whether the issue is input binding or the price calculation.
Reproduce it before proposing a change; preserve the HTTP contract unless needed.
```

The assistant may still need more imports, configuration or data. Let evidence determine that expansion.

## Reproduce before changing anything

From the cloned examples repository:

```text
python -m pip install "apizit-linking[preview,models]==1.0.0rc1"
apizit-linking validate examples/multi-module-api --json
apizit-linking preview examples/multi-module-api --port 8080
```

In another terminal:

```python
import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:8080/products/42/quote?discount=0.1") as response:
    assert response.status == 200
    result = json.load(response)
    assert result["product_id"] == 42
    assert result["discount"] == 0.1
    assert result["final_price"] == round(result["base_price"] * 0.999, 2)
```

Call the function directly from the example root too. Comparing direct and HTTP behavior helps isolate a binding issue from a calculation issue. Include missing optional values and invalid types where relevant.

## Verify the correction

Rerun direct tests, validation and the original request after a fix. Check neighboring routes if you changed a pattern. Record the tested version and stop preview.

Flask and FastAPI also expose route information and support organized service layers. Linking's particular convention keeps declared customer routes and Python targets together in a manifest before application startup.

Continue with [YAML]({{docs}}/reference/linking-yaml/), [CLI diagnostics]({{docs}}/reference/cli/), [AI-assisted development]({{docs}}/guides/ai-assisted-development/) and [fit and limits]({{docs}}/limits/#choose).

## Use an observed route event

Configure logger `apizit_linking.requests` at INFO to collect JSON events. A successful matched request includes request_id, method, route pattern, function, route_id, status, duration_ms and source_fingerprint. X-Request-ID carries the same generated ID. Input values, headers, query strings and concrete URLs are absent.

```text
apizit-linking explain examples/multi-module-api --method GET --path /products/42/quote --json
apizit-linking routes examples/multi-module-api --json
```

Expect `catalog.service:quote`, `catalog/service.py` and a one-based function line. Compare the export's source_fingerprint with the observed event and inspect the correct source snapshot. A path and function reference identify an entry point, not the entire failure cause. Investigate dependencies and data through controlled tests.

Export the contract before a correction, run direct business and HTTP tests, export again and run diff. A response-contract change is rejected automatically; an internal correction still needs its behavior tests. See [the AI workflow]({{docs}}/guides/ai-assisted-development/) and [CLI reference]({{docs}}/reference/cli/).
