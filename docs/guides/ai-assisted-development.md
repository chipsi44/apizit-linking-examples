# Build a Python API with an AI assistant

APIZIT Linking gives an assistant two explicit jobs: implement ordinary Python behavior, then bind it to HTTP in a manifest. Keep those jobs reviewable, supply focused context and verify the generated result yourself.

You need Python 3.10–3.14, a terminal and an editor. The assistant is optional: a developer can follow the same steps. All Linking commands here use stable 1.0.1.

## Start with precise behavior

Specify that quantity is a positive integer, unit price is non-negative and the result contains a subtotal rounded to two decimal places. HTTP methods and request bodies are a later decision.

A focused prompt can be:

```text
Implement calculate_subtotal(unit_price: float, quantity: int) in pricing.py.
Return {"subtotal": ...}, rounded to two decimal places.
Reject a negative unit_price or quantity below 1 with ValueError.
Keep this module ordinary Python, with no framework imports.
Write direct unittest tests for successful and rejected inputs.
```

An assistant still needs your project conventions and domain rules. Separating HTTP does not make arithmetic, permissions or business requirements disappear. Floating-point rounding suffices for this demonstration; select an appropriate money representation for a real billing system.

## Implement and test the Python function

Create `pricing.py`:

```python
def calculate_subtotal(unit_price: float, quantity: int) -> dict[str, float]:
    if unit_price < 0 or quantity < 1:
        raise ValueError("Price must be non-negative and quantity at least one.")
    return {"subtotal": round(unit_price * quantity, 2)}
```

Create `test_pricing.py`:

```python
import unittest
from pricing import calculate_subtotal

class PricingTests(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(calculate_subtotal(12.5, 2), {"subtotal": 25.0})

    def test_rejects_invalid_quantity(self):
        with self.assertRaises(ValueError):
            calculate_subtotal(12.5, 0)

    def test_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            calculate_subtotal(-1.0, 2)
```

Run:

```text
python -m unittest test_pricing
```

Three passing tests establish this narrow behavior. Review the function and keep the tests as a reference while adding the API.

## Give the assistant the HTTP task

Supply the tested signature, intended route and [parameter-source reference]({{docs}}/reference/linking-yaml/#explicit-sources):

```text
Create a version: 1 apizit_linking.yaml.
Expose pricing:calculate_subtotal as POST /quotes.
Bind unit_price and quantity explicitly from top-level JSON body fields.
Keep pricing.py unchanged. Use the documented Linking 1.0 stable release contract.
Leave legacy conversion enabled for this first operation; add HTTP policies explicitly.
```

The manifest becomes:

```yaml
version: 1
routes:
  - path: /quotes
    method: POST
    function: pricing:calculate_subtotal
    parameters:
      unit_price:
        source:
          location: body
          name: unit_price
      quantity:
        source:
          location: body
          name: quantity
```

The separate diff makes the method, exposed function and sources easy to inspect. It helps you notice accidental exposure of another function. Your project may still need access control; a manifest is not authorization.

## Validate the proposed contract

```text
python -m pip install "apizit-linking[preview,models]==1.0.1"
apizit-linking validate .
apizit-linking validate . --json
```

Expect `valid: true` and one route for `POST /quotes`. The JSON route record includes the target and compiled signature. Diagnostics include a code and, where applicable, route index, field and parameter.

If validation fails, give the relevant diagnostic and entry to the assistant and rerun after correction. Static validation does not import `pricing.py`, but it does not replace its tests or a security review.

## Exercise real HTTP behavior

```text
apizit-linking preview . --port 8080
```

In another terminal:

```python
import json
from urllib.request import Request, urlopen

request = Request(
    "http://127.0.0.1:8080/quotes",
    data=json.dumps({"unit_price": 12.5, "quantity": 2}).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request) as response:
    assert response.status == 200
    assert json.load(response) == {"subtotal": 25.0}
```

Also send `quantity: "many"`. Linking should return HTTP 400 with `INVALID_PARAMETER` before invoking the function. Sending `quantity: 0` passes integer conversion and reaches the business exception, which becomes a generic HTTP 500 in preview. This first manifest deliberately leaves the exception unmapped. Add an explicit errors policy when ValueError should represent a client-domain error.

Primitive conversion and domain validation are separate concerns. Check that distinction when reviewing an assistant's claim that validation is complete.

## Review at both levels

Review the function and direct tests, then the manifest's exposure and sources, then observed HTTP results. Rerun both levels after changing a signature or binding. Stop preview with Ctrl+C.

The workflow gives people and assistants clear checkpoints and a smaller relevant contract for each task. It does not guarantee lower token usage, faster generation or fewer bugs; those outcomes need project-specific measurement.

Continue with [route diagnosis]({{docs}}/guides/trace-route-to-python/), [examples]({{docs}}/examples/) and [V1 limits]({{docs}}/limits/). Compare [Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/) before selecting a framework.

## Check a controlled modification

Take an exported baseline before asking the assistant to change behavior:

```text
apizit-linking export . --output before.json
```

Give the assistant the affected function, its tests and the matching route. Ask it to preserve the HTTP contract, update the direct tests for the intended behavior and run validation. Then:

```text
python -m unittest test_pricing
apizit-linking validate . --json
apizit-linking export . --output after.json
apizit-linking diff before.json after.json --json
```

An unchanged HTTP contract passes; changing a declared status, binding or required signature is a review gate. Exit 1 indicates a changed/removed contract; exit 2 indicates invalid exports or unresolved typed model changes. For typed routes take both snapshots with --resolve-models, which imports project code in a controlled environment. A compatible contract does not prove correct calculations or permissions.

For the next operation, use [nested models]({{docs}}/reference/models/), [explicit HTTP errors]({{docs}}/reference/responses/) or [the persistent API]({{docs}}/guides/persistent-api/). Keep the three jobs visible: Python behavior, HTTP policy and verification.
