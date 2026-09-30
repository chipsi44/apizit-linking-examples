# APIZIT Linking — Python APIs with clear context for AI

[Documentation](https://chipsi44.github.io/apizit-linking-examples/) ·
[PyPI release](https://pypi.org/project/apizit-linking/1.0.1/) ·
[Fork the examples](https://github.com/chipsi44/apizit-linking-examples/fork)

Write and test ordinary Python, define the HTTP contract separately, and follow
routes straight back to source. This public repository is the single editable
source for English documentation and runnable examples. Its root is a Hello World
API usable without an APIZIT account.

```python
# hello.py — ordinary Python, unchanged by HTTP exposure
def hello():
    return {"message": "Hello from APIZIT Linking!"}
```

```yaml
version: 1
routes:
  - path: /hello
    method: GET
    function: hello:hello
```

## Run the quickstart

Use Python 3.10–3.14 and a virtual environment. Current stable gallery pin: 1.0.1.
Verify the documented limits and your application before deploying; 0.5.0 is historical.

```text
git clone https://github.com/chipsi44/apizit-linking-examples.git
cd apizit-linking-examples
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -r requirements.txt
apizit-linking validate . --json
apizit-linking preview . --port 8080
```

GET http://127.0.0.1:8080/hello returns 200 and the message above.
Preview exposes /docs, /redoc and /openapi.json and imports trusted code.

## Choose an example

The [gallery](examples/README.md) covers path/query, JSON, errors, packages and
process-local CRUD. Original business files import neither Linking nor a web
framework. The [persistent API](examples/persistent-api/README.md) adds nested
models, SQLite transactions, writer/reader and owner permissions, 201/204 and
domain errors. Stop/restart the server to verify local persistence without APIZIT.

Three V1 demonstrations are tested: an unchanged library exposed through YAML;
a persistent protected API; and an HTTP event traced to code followed by tests
and a contract-diff gate. This is evidence for the declared workflow, not a
universal token, speed or reliability advantage over Flask or FastAPI.

## Test and maintain the documentation

```text
python -m pip install -r requirements-test.txt
node scripts/build-docs.cjs
node --test tests/*.test.cjs
python -m unittest discover -s tests -p "test_*.py"
```

Edit `docs/*.md` and the ordered `docs/catalog.json`; preserve slugs and anchors.
The offline renderer builds 30 pages, metadata, sitemap, search, Markdown downloads,
catalogue and llms.txt. `node scripts/export-apizit-docs.cjs --website PATH`
exports the same content, renderer, schema, source commit and hashes to APIZIT.
Use `--check` to verify parity. Both builds are autonomous and need no download.
The website reads `/linking/`; `/docs/linking/` remains its SaaS integration guide.
GitHub Pages stays public; protected APIZIT dev retains noindex during transition.

[Limits](https://chipsi44.github.io/apizit-linking-examples/limits/#choose),
[compatibility](https://chipsi44.github.io/apizit-linking-examples/reference/compatibility/),
[migration](https://chipsi44.github.io/apizit-linking-examples/migrations/),
[releases](https://chipsi44.github.io/apizit-linking-examples/releases/) and
[security](SECURITY.md) describe the supported boundary. Historical publication
evidence remains in CHANGELOG.md. Linking is Apache-2.0; APIZIT is optional hosting.
