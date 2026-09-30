# V1 limits and boundaries

Linking 1.0 is a focused JSON API framework for ordinary Python functions. Its separate manifest, route inspection and explicit runtime policy help humans and agents review an API. This page describes the candidate; historical [0.5 behavior]({{docs}}/releases/0.5.0/) remains documented for existing users.

## Declare successful responses {#response-control}

`response` declares a 2xx status and safe headers. `201` can include `Location`; `204`, `205` and HEAD omit a body. Header templates accept flat returned field names. Missing fields and unsafe values fail with a generic 500. Named response adapters live in the runtime registry and must honor the declared status. There is no declarative cookie/session policy or streaming response contract. See [responses]({{docs}}/reference/responses/).

## Request errors remain structured {#request-errors}

Missing bindings and invalid legacy conversions return 400 with stable error codes. Typed field errors return `INVALID_MODEL`, field paths and error types, with generic messages and no input values. No automatic fallback occurs for an explicitly selected source or JSON pointer. Unmatched URLs return a real 404; unsupported methods return 405.

## Business errors have explicit mappings {#business-errors}

Map named exceptions to constant public 4xx/5xx codes and messages. Runtime startup resolves exceptions in the linked function's module; it rejects unknown mappings. Unmapped errors and invalid typed outputs return a generic JSON 500. A mapping does not prove that the business rule or authorization is correct.

## Typed bodies are opt-in {#body-models}

Legacy routes retain primitive/list/dictionary conversion. `validation: typed` uses the optional Pydantic extra for nested models, dataclasses, unions, dates, UUIDs, aliases and field constraints. Body bindings support RFC 6901 pointers, including `pointer: ""` for a whole JSON value. Typed routes require annotations for each HTTP parameter and the return; missing annotations prevent preparation. Explicit Any permits unrestricted data and provides no response filtering. Legacy return annotations remain documentary. Mutable model instances follow Pydantic's `revalidate_instances` policy; configure `always` when constraints must be rechecked. See [models]({{docs}}/reference/models/).

## Supported function signatures {#signatures}

The 1.0.0rc1 candidate requires module-level aliases for constrained Annotated function parameters/returns when inline Field factories trigger a false signature mismatch. The public persistent example uses this supported form. See [current release findings]({{docs}}/releases/1.0.0/#candidate-findings-and-publication-status); the prepared correction remains unpublished.

Top-level sync and async functions support positional-or-keyword and keyword-only arguments with defaults. Positional-only arguments, variadic arguments, synchronous generators and async generators are rejected. Function decorators that change the runtime signature can prevent startup.

## OpenAPI and runtime validation {#openapi}

Static compilation never imports code and cannot prove custom model schemas. Resolved OpenAPI requires explicit runtime imports and uses the same prepared adapters as typed validation. Legacy response annotations remain documentary. Nested pointers are exposed through `x-apizit-body-pointers`; their general JSON request shape is left unconstrained rather than claiming an inaccurate schema. Reusable factories disable documentation routes unless `docs=True`.

## Preview and bounded execution {#preview-boundary}

Preview binds to loopback unless `--allow-network` is supplied. `--reload` uses fresh workers; static errors retain the preceding worker, while runtime preparation failures can interrupt availability. Windows restarts cannot guarantee application lifespan cleanup. Preview provides no TLS, network isolation or production deployment.

Opt in to `RuntimeExtensions(limits=RequestLimits(...))` for received-body, query-pair, collection, nesting and concurrency limits. Async deadlines cover only the async business function. Synchronous cancellation waits for thread completion before closing its resources; arbitrary Python threads cannot be forcibly stopped. Custom validators, providers and guards own their execution behavior. See [standalone serving]({{docs}}/guides/standalone-serving/).

## Trusted runtime code {#trusted-code}

Private import namespaces prevent module-name collisions; they are not a sandbox. Factories, imports, validators, guards and business functions run with the process's permissions. Serve immutable source directories and isolate untrusted execution outside the engine. A security scheme in OpenAPI describes a guard; it does not implement authentication.

## Deployment remains a separate decision {#deployment}

Use the standalone ASGI adapter with your own server and database. Linking requires no APIZIT account or backend. APIZIT can adapt and pin a qualified package for managed launches; platform availability, metering, runtime storage and commercial terms are separate.

## Persistence belongs to resources {#example-state}

The legacy task gallery uses process-local state. The new [persistent API]({{docs}}/guides/persistent-api/) uses owner-scoped SQLite transactions and survives an actual local process restart. SQLite requires a durable local filesystem; the example does not establish durability on an ephemeral managed runtime. Applications own schema migrations, backups and connection budgets.

## When should you choose Linking? {#choose}

Choose Linking for an existing Python library, domain services or a JSON API whose HTTP policy benefits from a separate inspectable map. Functions remain independently testable; providers inject resources and principals at the boundary. Agents can locate a route and check a proposed contract using the same tools as maintainers.

Choose direct Flask or FastAPI when their native routing, dependency model or mature plugin ecosystem better matches your application. Direct frameworks also support service layers and route inventories. WebSockets, streaming, a built-in ORM, automatic migrations, an identity provider and non-Python business code are outside this release. Compare [Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/).
