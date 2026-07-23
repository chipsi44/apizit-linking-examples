# JSON body validation

This project maps top-level fields from a JSON object to typed Python
parameters. APIZIT Linking checks required fields and converts values using the
function annotations.

## Route

| Method | Path | Python function |
| --- | --- | --- |
| `POST` | `/products` | `products:create_product` |

## Validate, test, and run

From the repository root:

```text
apizit-linking validate examples/json-body
apizit-linking preview examples/json-body --port 8080
python -m unittest tests.test_examples.ExampleProjectHttpTests.test_json_body_defaults_and_validation -v
```

Create a product:

```text
curl -X POST http://127.0.0.1:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook","price":12.5,"in_stock":true,"tags":["paper","office"]}'
```

Expected response (`200 OK`):

```json
{
  "name": "Notebook",
  "price": 12.5,
  "in_stock": true,
  "tags": ["paper", "office"]
}
```

`in_stock` and `tags` are optional because the Python function defines
defaults:

```text
curl -X POST http://127.0.0.1:8080/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Pen","price":"2.75"}'
```

Expected response (`200 OK`):

```json
{"name":"Pen","price":2.75,"in_stock":true,"tags":[]}
```

An invalid value such as `"price":"free"` returns `400 Bad Request` with error
code `INVALID_PARAMETER`.

## Limitation

V1 binds fields at the top level of a JSON object. It supports primitive
values, lists, dictionaries, and nullable unions, but it is not a nested model
validation system and does not apply constraints such as minimum prices or
string lengths.
