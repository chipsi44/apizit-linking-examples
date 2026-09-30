# Resources, permissions and application lifecycle

Register resource acquisition and permission policy in a Python composition module, then reference their names from the manifest. Ordinary business functions receive ordinary values and remain independent from Linking and APIZIT.

## Register a runtime factory

`runtime.factory: bootstrap:configure` references a synchronous zero-argument function returning RuntimeExtensions. Static compilation checks its signature without importing it; application preparation explicitly executes it. A caller can instead pass `extensions=` to create_app; supplying both is rejected.

```python
from apizit_linking.extensions import AccessDenied, Provider, RuntimeExtensions
from apizit_linking.limits import RequestLimits

def authenticated(context):
    found, token = context.request.lookup("header", "X-API-Key")
    principal = verify_key(token) if found else None
    if principal is None:
        raise AccessDenied(401, "UNAUTHENTICATED", "Valid API key required")
    context.state["principal"] = principal

def writer(context):
    if not context.state["principal"].can_write:
        raise AccessDenied(403)

def principal(context):
    return context.state["principal"]

def configure():
    return RuntimeExtensions(
        providers={"principal": Provider(principal)},
        guards={"authenticated": authenticated, "writer": writer},
        security_schemes={"authenticated": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
        limits=RequestLimits(),
    )
```

`verify_key` and the principal policy are application functions in this illustrative fragment. For a complete runnable implementation with environment keys and SQLite, use [the persistent guide]({{docs}}/guides/persistent-api/).

```yaml
runtime:
  factory: bootstrap:configure
```

On each protected route declare `security: [authenticated, writer]` and `dependencies: {user: principal}`. Guards run in order before providers/business code. Each must return None on success or raise AccessDenied; another return value fails closed. All guards must succeed. Security schemes describe authentication in OpenAPI; guard code implements it. Never infer ownership from an email, HTTP body or role alone.

## Providers and cleanup

A Provider callback receives ExecutionContext first. It can return a value, a decorated context manager, or an async context manager. Request scope is default and caches one value per provider per invocation. `requires=("other",)` resolves dependencies and passes them by name. Bare generator callbacks are rejected; use contextmanager/asynccontextmanager.

Context managers close in reverse order on success, error and cancellation. Mapped business errors reach them before an HTTP response is formed. Synchronous callbacks use worker threads; cancellation waits for their completion before cleanup. Ensure database connections permit this thread usage. `scope="application"` starts at ASGI lifespan and closes on shutdown; shared values must support concurrent requests. Application providers cannot depend on request providers. Unknown names and cycles prevent startup.

Injected parameters must exist in the signature and cannot also declare an HTTP source. They are excluded from client input models and OpenAPI parameters. Query/body values cannot replace an injected database or principal.

## ASGI customization

RuntimeExtensions accepts an async lifespan context manager, ASGI middleware tuples and named response adapters. Keep transport policy in this module. RequestLimits is optional: its defaults, when enabled, are 1 MiB body, 1,000 query pairs, 10,000 JSON collection items, depth 64 and 100 concurrent requests per app instance. `async_timeout` bounds only async business execution, not imports, validators, guards, providers or threads.

Applications own identity verification, key rotation, role/ownership rules, database migrations, backups and connection budgets. This release provides integration points, not an identity provider or ORM. Read [HTTP errors]({{docs}}/reference/responses/) and [standalone serving]({{docs}}/guides/standalone-serving/).
