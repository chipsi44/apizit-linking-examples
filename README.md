# APIZIT Linking examples

[![CI](https://github.com/chipsi44/apizit-linking-examples/actions/workflows/ci.yml/badge.svg)](https://github.com/chipsi44/apizit-linking-examples/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-2357c6)](https://chipsi44.github.io/apizit-linking-examples/)
[![APIZIT Linking](https://img.shields.io/badge/APIZIT%20Linking-0.4.0-blue)](https://pypi.org/project/apizit-linking/)

Public, forkable API projects for
[APIZIT Linking](https://pypi.org/project/apizit-linking/). The repository root
is itself a complete Hello World project: fork or clone it, install the public
package, then validate and preview it without changing the Python business
code.

The business modules contain no APIZIT Linking, FastAPI, or Flask imports.
Routes and request bindings live only in `apizit_linking.yaml`.

Read the [public documentation](https://chipsi44.github.io/apizit-linking-examples/)
for the quickstart, complete Linking YAML and CLI references, runnable example
catalogue, architecture guides, and documented V1 boundaries.

The canonical editor schema is published as
[raw JSON Schema](https://chipsi44.github.io/apizit-linking-examples/schema/apizit-linking-v1.schema.json).
The public
[compatibility policy](https://chipsi44.github.io/apizit-linking-examples/reference/compatibility/)
separates package, manifest, diagnostics, and runtime-artifact guarantees.
See the canonical
[release notes](https://chipsi44.github.io/apizit-linking-examples/releases/),
[migration index](https://chipsi44.github.io/apizit-linking-examples/migrations/),
and [security policy](https://chipsi44.github.io/apizit-linking-examples/security/)
before updating an integration pin.

## Fork and run

[Fork this repository](https://github.com/chipsi44/apizit-linking-examples/fork)
or clone it:

```text
git clone https://github.com/chipsi44/apizit-linking-examples.git
cd apizit-linking-examples
python -m venv .venv
```

Activate the environment:

```text
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

Install and run the root example:

```text
python -m pip install -r requirements.txt
apizit-linking validate .
apizit-linking preview . --port 8080
```

In another terminal:

```text
curl http://127.0.0.1:8080/hello
```

Expected response (`200 OK`):

```json
{"message":"Hello from APIZIT Linking!"}
```

The complete root project is only:

- `hello.py`: an ordinary Python function;
- `apizit_linking.yaml`: the declarative HTTP route;
- `requirements.txt`: the pinned public preview dependency.

## Example catalogue

| Project | Location | Routes | Main concepts |
| --- | --- | ---: | --- |
| Hello World | repository root | 1 | Minimal function-to-route project |
| [Path and query parameters](examples/path-and-query-parameters/README.md) | `examples/path-and-query-parameters` | 1 | Explicit sources, conversion, Python defaults |
| [JSON body](examples/json-body/README.md) | `examples/json-body` | 1 | Required/optional body fields and typed conversion |
| [Error handling](examples/error-handling/README.md) | `examples/error-handling` | 1 | Structured request errors and generic business failures |
| [Multi-module API](examples/multi-module-api/README.md) | `examples/multi-module-api` | 1 | Dotted targets, packages, relative imports |
| [Task API](examples/task-api/README.md) | `examples/task-api` | 5 | CRUD-style methods, path/query/body, in-memory state |

Run another project by passing its directory:

```text
apizit-linking validate examples/task-api
apizit-linking preview examples/task-api --port 8080
```

See [the gallery guide](examples/README.md) for the complete feature matrix.

## Use these projects with APIZIT

Each directory is an independent project that APIZIT can scan as realistic
customer code. A fork can therefore serve as:

- a starter project for a user;
- a stable input repository for APIZIT scan and deployment tests;
- an integration fixture for a new APIZIT Linking release;
- a regression suite for supported route, parameter, body, and module patterns.

Pin a commit or compatibility tag when a repeatable external test fixture is
required.

## Test the collection

After installing `requirements.txt`, install the test-only dependency and run:

```text
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -p "test_*.py" -v
```

The suite:

- compiles every manifest and checks all 10 routes;
- rejects web/linking imports in business modules;
- invokes every project through the real ASGI adapter;
- verifies typed path, query, and JSON body conversion;
- verifies structured `400` errors and generic `500` failures;
- runs the complete task CRUD lifecycle.

CI performs the same checks against the published `apizit-linking==0.4.0` on
Python 3.10 through 3.14.

## Releases and migrations

PyPI is the canonical source for installable `apizit-linking` wheels and source
distributions. GitHub Pages contains the human-readable release notes and
version-by-version migration guides. This examples repository does not create
GitHub Releases for the engine because its generated source archives would
contain the examples repository, not the canonical package.

The [0.4.0 retrospective](https://chipsi44.github.io/apizit-linking-examples/releases/0.4.0/)
documents the current stable beta. The
[0.5.0rc1 release-candidate page](https://chipsi44.github.io/apizit-linking-examples/releases/0.5.0/)
documents the published evaluation candidate and links to its canonical
[PyPI files](https://pypi.org/project/apizit-linking/0.5.0rc1/).

Evaluate the candidate only in a separate environment:

```text
python -m pip install "apizit-linking[preview]==0.5.0rc1"
```

The final 0.5.0 package is not published. Requirements, runnable examples,
guides, CI, and production integrations remain pinned to 0.4.0. APIZIT has not
yet been promoted to the candidate.

## Security

Do not disclose vulnerabilities in public issues. Read
[SECURITY.md](SECURITY.md) or the
[published security page](https://chipsi44.github.io/apizit-linking-examples/security/)
for supported versions, the private-reporting channel, scope, and the safe
fallback if GitHub Private Vulnerability Reporting is temporarily unavailable.

## Current V1 boundaries

- Successful returned values use HTTP `200`; custom `201`, `204`, or `404`
  responses and response headers cannot yet be declared.
- APIZIT Linking request-resolution failures are structured `400` responses.
- Unhandled business exceptions become generic `500` responses.
- Body bindings select top-level JSON fields rather than nested models.
- The Task API store is process-local and not production persistence.
- Preview is a local development server, not a deployment, authentication, or
  sandbox boundary.

The examples expose these boundaries honestly instead of importing a web
framework into the business code.

## Contributing

Fork the repository, keep each project minimal and infrastructure-independent,
add or update its HTTP integration test, then open a pull request.

Licensed under Apache-2.0.
