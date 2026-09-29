# Forkable example APIs

Every project has its own manifest and framework-independent Python code. Copy one, run it as-is, or pin it as an APIZIT integration fixture.

All examples target **APIZIT Linking 0.5.0**. Their business modules import neither APIZIT Linking, FastAPI, nor Flask.

## Project catalogue {#catalogue}

Repository root · 1 route

### Hello World

The smallest complete function-to-route project.

- GET
- module:function
- preview

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples)

examples/path-and-query-parameters · 1 route

### Path and query parameters

Explicit request sources, `int`/`bool` conversion, and a Python default.

- path
- query
- defaults

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/path-and-query-parameters)

examples/json-body · 1 route

### JSON body

Required and optional top-level body fields with typed conversion, nullable values, and defaults.

- POST
- body
- list[str]

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/json-body)

examples/error-handling · 1 route

### Error handling

Structured request-resolution failures and the generic boundary for an unhandled business exception.

- 400
- 500
- conversion

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/error-handling)

examples/multi-module-api · 1 route

### Multi-module API

A dotted target inside a Python package, with a package-relative import performed by the linked function.

- package
- dotted target
- relative import

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/multi-module-api)

examples/task-api · 5 routes

### Task API

A realistic CRUD-style service using path, query, and body inputs with process-local state.

- GET
- POST
- PATCH
- DELETE

[View project on GitHub](https://github.com/chipsi44/apizit-linking-examples/tree/main/examples/task-api)

## Route matrix {#routes}

| Project | Method | Path | Linked function |
| --- | --- | --- |
| Hello World | GET | `/hello` | `hello:hello` |
| Path and query | GET | `/users/{user_id}/greeting` | `greetings:get_greeting` |
| JSON body | POST | `/products` | `products:create_product` |
| Error handling | GET | `/divide` | `calculator:divide` |
| Multi-module API | GET | `/products/{product_id}/quote` | `catalog.service:quote` |
| Task API | GET | `/tasks` | `tasks:list_tasks` |
| POST | `/tasks` | `tasks:create_task` |
| GET | `/tasks/{task_id}` | `tasks:get_task` |
| PATCH | `/tasks/{task_id}` | `tasks:update_task` |
| DELETE | `/tasks/{task_id}` | `tasks:delete_task` |

## Validate or run any project {#run}

```text
python -m pip install -r requirements.txt

apizit-linking validate examples/task-api
apizit-linking preview examples/task-api --port 8080
```

Replace `task-api` with any directory name in the catalogue. Each project README includes its routes, request examples, expected responses, tests, and specific limitations.

### Use the whole repository as a test fixture

The integration suite compiles every manifest, rejects framework imports in business files, invokes all routes through the actual ASGI adapter, and runs the complete task lifecycle.

 [Fork on GitHub](https://github.com/chipsi44/apizit-linking-examples)
