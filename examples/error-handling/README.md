# Request and business errors

This project shows the error behavior APIZIT Linking currently guarantees:
request-resolution errors are structured `400` responses, while an unhandled
business exception becomes a generic `500` response.

## Route

| Method | Path | Python function |
| --- | --- | --- |
| `GET` | `/divide` | `calculator:divide` |

## Validate, test, and run

From the repository root:

```text
apizit-linking validate examples/error-handling
apizit-linking preview examples/error-handling --port 8080
python -m unittest tests.test_examples.ExampleProjectHttpTests.test_request_errors_and_generic_business_failure -v
```

Successful request:

```text
curl "http://127.0.0.1:8080/divide?dividend=10&divisor=4"
```

Expected response (`200 OK`):

```json
{"dividend":10.0,"divisor":4.0,"result":2.5}
```

Missing `divisor`:

```text
curl "http://127.0.0.1:8080/divide?dividend=10"
```

Expected response (`400 Bad Request`):

```json
{
  "error": {
    "code": "PARAMETER_NOT_FOUND_IN_SOURCE",
    "message": "Required field 'divisor' was not found in request source 'query'.",
    "parameter": "divisor",
    "external_name": "divisor",
    "source": "query"
  }
}
```

An invalid number such as `divisor=many` returns `400 Bad Request` with error
code `INVALID_PARAMETER`.

For division by zero, the business function raises `ValueError`. Preview
returns a generic `500 Internal Server Error` and does not expose the exception
message.

## Limitation

V1 cannot yet declare response status codes, headers, response schemas, or map
business exceptions to HTTP responses. Business code intentionally does not
import `HTTPException`, FastAPI, or APIZIT Linking.
