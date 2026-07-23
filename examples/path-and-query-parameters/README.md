# Path and query parameters

This project binds two HTTP sources explicitly to an ordinary Python function:

- `user_id` comes from the route path and is converted to `int`;
- `verbose` comes from the query string and is converted to `bool`.

The Python default `False` is used when `verbose` is absent.

## Route

| Method | Path | Python function |
| --- | --- | --- |
| `GET` | `/users/{user_id}/greeting` | `greetings:get_greeting` |

## Validate, test, and run

From the repository root:

```text
apizit-linking validate examples/path-and-query-parameters
apizit-linking preview examples/path-and-query-parameters --port 8080
python -m unittest tests.test_examples.ExampleProjectHttpTests.test_path_and_query_conversions_and_default -v
```

Request using the Python default:

```text
curl http://127.0.0.1:8080/users/42/greeting
```

Expected response (`200 OK`):

```json
{"user_id":42,"message":"Hello, user 42!"}
```

Request with the optional query parameter:

```text
curl "http://127.0.0.1:8080/users/42/greeting?verbose=true"
```

Expected response (`200 OK`):

```json
{
  "user_id": 42,
  "message": "Hello, user 42!",
  "details": "The verbose query parameter is enabled."
}
```

## Limitation

V1 converts primitive annotations and generates useful OpenAPI request and
minimal response documentation. Return schemas remain documentary and are not
enforced at runtime. An invalid integer or boolean produces a structured APIZIT
Linking `400` response.
