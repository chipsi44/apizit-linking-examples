# Example gallery

Every subdirectory is an independent APIZIT Linking project with its own Python
business code, `apizit_linking.yaml`, routes, requests, responses, and
limitations.

The repository root contains the sixth project, Hello World.

## Projects

| Project | Routes | Sources and behavior |
| --- | ---: | --- |
| [Path and query parameters](path-and-query-parameters/README.md) | 1 | `path`, `query`, `int`, `bool`, default |
| [JSON body](json-body/README.md) | 1 | top-level `body`, required/default/nullable values |
| [Error handling](error-handling/README.md) | 1 | request `400`, business `500` |
| [Multi-module API](multi-module-api/README.md) | 1 | dotted target, package, relative import |
| [Task API](task-api/README.md) | 5 | GET/POST/PATCH/DELETE, path/query/body, state |

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

All projects target the capabilities available in APIZIT Linking 0.5.0.
