# Multi-module API

This project proves that a linked function can live in a normal Python package
and collaborate with another business module through a relative import.

## Route

| Method | Path | Python function |
| --- | --- | --- |
| `GET` | `/products/{product_id}/quote` | `catalog.service:quote` |

## Files

- `catalog/service.py` exposes the linked function.
- `catalog/pricing.py` contains reusable pricing rules.
- `catalog/__init__.py` makes `catalog` a regular package.
- `apizit_linking.yaml` uses the dotted target `catalog.service:quote`.

The relative pricing import occurs inside `quote`. Static validation can
therefore inspect the linked function without importing or executing the
package.

## Validate, test, and run

From the repository root:

```text
apizit-linking validate examples/multi-module-api
apizit-linking preview examples/multi-module-api --port 8080
python -m unittest tests.test_examples.ExampleProjectHttpTests.test_multi_module_package -v
```

Request a quote with a 25 percent discount:

```text
curl "http://127.0.0.1:8080/products/4/quote?discount=25"
```

Expected response (`200 OK`):

```json
{
  "product_id": 4,
  "base_price": 16.0,
  "discount": 25.0,
  "final_price": 12.0
}
```

Without `discount`, the Python default `0.0` applies.

## Limitation

This pricing formula is intentionally simplistic. A discount outside `0..100`
raises a business exception and therefore becomes a generic `500` response in
V1; declarative business-error mapping is not supported yet.
