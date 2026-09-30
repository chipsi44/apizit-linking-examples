# Example gallery

Every subdirectory is an independent APIZIT Linking project with its own Python
business code, `apizit_linking.yaml`, routes, requests, responses, and
limitations.

The repository root contains Hello World; six additional projects cover legacy and typed APIs.

## Projects

| Project | Routes | Sources and behavior |
| --- | ---: | --- |
| [Path and query parameters](path-and-query-parameters/README.md) | 1 | `path`, `query`, `int`, `bool`, default |
| [JSON body](json-body/README.md) | 1 | top-level `body`, required/default/nullable values |
| [Error handling](error-handling/README.md) | 1 | request `400`, business `500` |
| [Multi-module API](multi-module-api/README.md) | 1 | dotted target, package, relative import |
| [Task API](task-api/README.md) | 5 | GET/POST/PATCH/DELETE, path/query/body, state |
| [Persistent API](persistent-api/README.md) | 4 | nested models, SQLite transactions, owner permissions, 201/204/domain errors |

## Validate or run one project

From the repository root:

```text
apizit-linking validate examples/json-body
apizit-linking preview examples/json-body --port 8080
```

Replace `json-body` with any project name in the table.

## Validate every project

The public CI validates the root project and every manifest under `examples/`.
Locally, the integration suite compiles and invokes them all:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

All projects are qualified against the exact Linking 1.0.0rc1 candidate pin.


## Linking 1.0 candidate

The current gallery evaluates 1.0.0rc1. Original business files retain their legacy contract; the new [persistent API](persistent-api/README.md) adds nested models, SQLite resources, owner permissions and explicit HTTP responses without APIZIT. Route inspection and contract diff support controlled changes. See the current public documentation and migration guide; preceding 0.5 release evidence below is historical.
