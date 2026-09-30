# From plain Python to local HTTP

Fork or clone a complete project, validate it without importing the business module, then start the local preview.

**Prerequisite:** Python 3.10 or newer. The example pins `apizit-linking[preview,models]==1.0.0rc1` for repeatable behavior.

## 1. Get the project {#get-the-project}

[Fork the public repository](https://github.com/chipsi44/apizit-linking-examples/fork) to experiment in your own GitHub account, or clone it directly:

Terminal

```text
git clone https://github.com/chipsi44/apizit-linking-examples.git
cd apizit-linking-examples
python -m venv .venv
```

### Activate the virtual environment {#activate}

Windows PowerShell

```text
.venv\Scripts\Activate.ps1
```

macOS or Linux

```text
source .venv/bin/activate
```

## 2. Install the local preview {#install}

The repository dependency installs the standalone binding engine, FastAPI adapter, multipart support, and Uvicorn development server:

Terminal

```text
python -m pip install -r requirements.txt
```

For validation without preview, the smaller core installation is sufficient:

Core only

```text
python -m pip install "apizit-linking==1.0.0rc1"
```

## 3. Inspect the complete project {#inspect}

The runnable root project has one business file and one HTTP contract.

hello.py

```python
def hello() -> dict[str, str]:
    return {"message": "Hello from APIZIT Linking!"}
```

apizit_linking.yaml

```yaml
version: 1

runtime:
  language: python
  version: "3.12"

routes:
  - path: /hello
    method: GET
    function: hello:hello
```

The Python module has no APIZIT Linking or web-framework import. The `function` value names the module and top-level function as `module:function`.

## 4. Validate without executing business code {#validate}

Terminal

```text
apizit-linking validate .
```

A successful result reports that the definition is valid and compiled one route.

Expected output

```text
APIZIT linking definition is valid: .../apizit_linking.yaml
Compiled routes: 1
```

Validation parses the Python source with the AST. It checks the route, function, signature, parameter bindings, and collisions without importing or calling `hello.py`.

## 5. Preview and call the route {#preview}

Terminal 1

```text
apizit-linking preview . --port 8080
```

Keep that process running. From another terminal:

Terminal 2

```text
curl http://127.0.0.1:8080/hello
```

Response · 200 OK

```json
{"message":"Hello from APIZIT Linking!"}
```

Stop the preview with Ctrl+C.

**Local development only.** Preview binds to `127.0.0.1` by default. It is not a production server, authentication layer, or sandbox. Starting it imports and executes trusted customer code in the server process.

## Where to go next {#next}

- [Exercise path, query, body, package, and CRUD examples]({{docs}}/examples/)
- [Learn the complete V1 linking contract]({{docs}}/reference/linking-yaml/)
- [See every validate and preview option]({{docs}}/reference/cli/)
