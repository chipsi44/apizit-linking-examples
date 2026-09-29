# V1 limits and boundaries

APIZIT Linking has a deliberately focused contract. These are the current limits to consider before choosing it for a project.

**The key distinction:** Linking keeps business code independent from a web framework. It does not claim that the preview runtime itself has no framework or that every HTTP concern is already supported.

## Successful responses use HTTP 200 {#response-control}

V1 serializes normal returned values as successful HTTP `200 OK` responses. A linking manifest cannot yet declare custom success statuses such as `201 Created` or `204 No Content`, custom response headers, cookies, or a typed response envelope.

The Task API therefore returns a created task with status 200 and represents a missing task as an application-level JSON object with status 200. The examples do not import FastAPI response classes to hide this boundary.

## Request errors are structured 400 responses {#request-errors}

Missing or invalid request parameters are resolved before the function is invoked and become structured `400` responses:

```json
{
  "error": {
    "code": "PARAMETER_NOT_FOUND_IN_SOURCE",
    "message": "Required field 'name' was not found in request source 'body'.",
    "parameter": "customer_name",
    "external_name": "name",
    "source": "body"
  }
}
```

V1 exposes stable codes including `PARAMETER_NOT_FOUND`, `PARAMETER_NOT_FOUND_IN_SOURCE`, and `INVALID_PARAMETER`. Minor beta releases may add diagnostic codes or metadata fields.

## Unhandled business exceptions become generic 500 responses {#business-errors}

The core engine does not map arbitrary business exceptions to HTTP statuses. In the FastAPI adapter, an unhandled exception crosses the application boundary as a generic `500 Internal Server Error`. Its private message is not returned to the HTTP caller.

Declarative mappings such as `TaskNotFound → 404` are not part of V1.

## Body bindings target top-level fields {#body-models}

A `body` source selects a top-level property from a JSON object. V1 does not define nested JSON selectors, Pydantic-style object models, discriminated unions, field constraints, aliases beyond the external source name, or response-model validation.

It converts primitive annotations, nullable unions, lists, and dictionaries. Custom annotations receive the adapter-provided value unchanged.

## Some Python signatures are intentionally unsupported {#signatures}

HTTP values are bound by parameter name, so positional-only parameters, `*args`, and `**kwargs` are rejected. Normal positional-or-keyword parameters, keyword-only parameters, Python defaults, and sync or async functions are supported.

## OpenAPI is useful documentation, not response enforcement {#openapi}

Version 0.5.0 generates OpenAPI 3.1 operations statically from the compiled route contract. It describes explicit and automatic request bindings, repeated values, defaults, nullability, and minimal `200`, `400`, and `500` responses. Preview exposes Swagger UI, ReDoc, and `/openapi.json`, relocating those URLs if a linked route would shadow them.

Reusable FastAPI factories keep documentation routes disabled by default; adapter users must opt in with `docs=True`. Return annotations produce documentary schemas only: Linking does not install a FastAPI response model and does not validate, transform, reject, or reshape customer return values. There is no response block in manifest v1.

## Preview is local development infrastructure {#preview-boundary}

`apizit-linking preview` validates, imports, and serves customer code in one local process. It binds to `127.0.0.1` by default and requires `--allow-network` before accepting a non-loopback host.

Preview is not an authentication layer, TLS endpoint, hardened production server, tenant boundary, resource sandbox, or safe runner for untrusted code.

## Import isolation is not a security sandbox {#trusted-code}

Runtime loading isolates each project beneath a private Python module namespace. This prevents same-named modules from separate projects colliding and preserves normal package imports.

Imported modules remain ordinary trusted Python. Their top-level code and linked functions can perform any operation allowed to the preview process.

## The standalone package does not deploy infrastructure {#deployment}

APIZIT Linking owns manifest discovery, static compilation, argument resolution, type conversion, function loading, invocation, and an optional FastAPI adapter. It does not itself own API Gateway, Lambda packaging, authentication, metering, or production deployment.

APIZIT is one platform that can consume the compiled contract, but the Linking package does not depend on APIZIT.

## Example state is not persistence {#example-state}

The Task API stores records in a process-local dictionary. Restarting preview resets the data, and the example is not designed for concurrent or durable production storage.

## When should you choose something else? {#choose}

Use a full web framework directly when HTTP is the core of the application and you need its complete response model, middleware, security, dependency injection, WebSockets, or OpenAPI ecosystem today.

Use APIZIT Linking when the important constraint is that existing domain, computation, data, or library functions remain transport-independent and the current V1 HTTP contract is sufficient.

- [See these boundaries exercised honestly]({{docs}}/examples/)
- [Review the exact supported manifest]({{docs}}/reference/linking-yaml/)
- [Report a use case or limitation on GitHub](https://github.com/chipsi44/apizit-linking-examples/issues)
