# Validate and preview projects

Check the linking contract statically, emit machine-readable results, or run a local development server.

## Installation {#installation}

Install only the compiler and runtime engine:

```text
python -m pip install "apizit-linking==0.5.0"
```

Include the FastAPI adapter and Uvicorn local server for preview:

```text
python -m pip install "apizit-linking[preview]==0.5.0"
```

## The `validate` command {#validate}

Synopsis

```text
apizit-linking validate [TARGET] [--project-root DIRECTORY] [--json]
```

`TARGET` defaults to the current directory. It may be a project directory or a specific `apizit_linking.yaml`, `.yml`, or `.json` file.

| Argument | Default | Purpose |
| --- | --- | --- |
| `TARGET` | `.` | Project directory or a linking manifest file. |
| `--project-root DIRECTORY` | Resolved from target | Root used to resolve `module:function` references. |
| `--json` | Off | Write a machine-readable compilation result to standard output. |

### Examples {#validate-examples}

```text
# Discover a manifest in the current directory
apizit-linking validate .

# Validate an independent example directory
apizit-linking validate examples/task-api

# Resolve a specific manifest against an explicit project root
apizit-linking validate config/apizit_linking.yaml --project-root .

# Emit JSON for CI or another tool
apizit-linking validate . --json
```

### JSON result {#json-output}

JSON mode includes the resolved file and project root, manifest version, compiled runtime routes, and aggregated diagnostics:

```json
{
  "valid": true,
  "file": "/project/apizit_linking.yaml",
  "project_root": "/project",
  "version": 1,
  "routes": [
    {
      "index": 0,
      "path": "/hello",
      "method": "GET",
      "function": "hello:hello",
      "module": "hello",
      "function_name": "hello",
      "parameters": {}
    }
  ],
  "diagnostics": []
}
```

Validation exits with status `0` when the definition is valid and `1` when blocking diagnostics are present.

## The `preview` command {#preview}

Synopsis

```text
apizit-linking preview [TARGET]
  [--project-root DIRECTORY]
  [--host HOST]
  [--port PORT]
  [--allow-network]
```

Preview validates first, then imports the customer modules and serves the compiled routes through the optional FastAPI adapter.

| Argument | Default | Purpose |
| --- | --- | --- |
| `TARGET` | `.` | Project directory or linking manifest file. |
| `--project-root DIRECTORY` | Resolved from target | Root used for local function imports. |
| `--host HOST` | `127.0.0.1` | Network interface for the development server. |
| `--port PORT` | `8000` | TCP port from `1` through `65535`. |
| `--allow-network` | Off | Explicitly permit binding to a non-loopback interface. |

### Examples {#preview-examples}

```text
# Local loopback preview
apizit-linking preview . --port 8080

# Preview one project in the gallery
apizit-linking preview examples/json-body --port 8080

# Deliberately expose the development server on the local network
apizit-linking preview . --host 0.0.0.0 --port 8080 --allow-network
```

**Network safety:** preview refuses a non-loopback `--host` unless `--allow-network` is also present. That flag only acknowledges exposure; it does not add authentication, encryption, sandboxing, or production hardening.

## Exit behavior {#exit-behavior}

| Status | Meaning |
| --- | --- |
| `0` | Validation succeeded, or preview stopped normally. |
| `1` | Invalid linking definition or failure while loading/starting the linked project. |
| `2` | Invalid CLI usage, missing preview dependencies, invalid port, or non-loopback binding without `--allow-network`. |

## Use in CI {#ci}

Pin the beta version, validate each independent project, and let the non-zero exit status fail the job:

```text
python -m pip install "apizit-linking==0.5.0"
apizit-linking validate .

for manifest in examples/*/apizit_linking.yaml; do
  apizit-linking validate "$(dirname "$manifest")"
done
```

- [Read the manifest contract]({{docs}}/reference/linking-yaml/)
- [Run validate and preview end to end]({{docs}}/quickstart/)
- [Understand preview and runtime boundaries]({{docs}}/limits/)
