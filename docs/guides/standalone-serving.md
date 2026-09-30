# Serve Linking independently of APIZIT

Linking is independently usable as an ASGI application. APIZIT hosting is optional and requires separate qualification. Use a reviewed project, an exact package pin and a server appropriate for your infrastructure.

## Prepare the application

Install `apizit-linking[preview,models]==1.0.0rc1` for this candidate. Save `asgi.py` outside your linked business modules:

```python
from pathlib import Path
from apizit_linking.fastapi import create_app

app = create_app(Path(__file__).parent, docs=False)
```

Run `apizit-linking validate . --json`, business tests and a resolved contract export before serving. For a local process:

```text
python -m uvicorn asgi:app --host 127.0.0.1 --port 8080
```

The app imports functions, executes the optional factory, prepares typed models and fails before serving on an invalid runtime contract. ASGI lifespan initializes application providers and closes them on graceful shutdown. Use a persistent database supplied by your application; Linking does not provision it.

## Explicit controls

Enable RequestLimits in RuntimeExtensions when desired. Defaults bound received body, JSON collection size/depth, query count and active requests per app instance. An async business deadline returns 504 after cancellation cleanup. Sync calls run in a bounded server thread pool; cancellation waits for completion and cannot stop arbitrary Python. Multiple server workers each have their own application resources and concurrency budget.

Your server or reverse proxy must provide TLS, connection/header/slow-client limits and deployment isolation. Your application provides authentication, authorization, migrations, backups and secrets. Serve an immutable source snapshot and retain its source fingerprint and exported contract with logs. Keep runtime code out of untrusted scan processes.

## Check a release and roll back

Probe health, models, permissions, intended error statuses and resource cleanup. Use `export --resolve-models` and `diff` against the preceding release; review conservative failures rather than silently bypassing them. Keep the exact environment lock, engine version, runtime artifact and source snapshot together. A runtime artifact compiled by 0.5 must be regenerated for 1.0's format v2.

Preview and `--reload` are development tools. Invalid static edits retain a preceding worker, runtime preparation failures can interrupt availability, and Windows reload termination does not guarantee lifespan cleanup. A managed release/rollback mechanism is a separate hosting concern. See [compatibility]({{docs}}/reference/compatibility/), [limits]({{docs}}/limits/) and [the persistent example]({{docs}}/guides/persistent-api/).
