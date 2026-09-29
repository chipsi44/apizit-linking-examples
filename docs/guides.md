# Keep HTTP outside the business code

Apply the declarative linking boundary to existing functions, layered Python services, and reusable libraries.

## Guides {#guides}

[Start from one function ### Expose a Python function as an HTTP API without decorators Map an unchanged typed function to a route, validate the manifest, and call it through local preview.]({{docs}}/guides/expose-python-function-as-http-api-without-decorators/) [Separate domain and transport ### Keep Python business logic independent from FastAPI Decide when route decorators belong in the application and when HTTP should remain an external adapter.]({{docs}}/guides/keep-python-business-logic-independent-from-fastapi/) [Start from a package ### Turn a Python library into an API with YAML Link functions in a multi-module package while preserving normal absolute, relative, and lazy imports.]({{docs}}/guides/turn-python-library-into-api-with-yaml/)

## Need the exact contract? {#reference}

The guides explain architectural choices. Use the reference when you need field-level rules or complete command options.

- [Linking YAML reference]({{docs}}/reference/linking-yaml/)
- [Validate and preview CLI reference]({{docs}}/reference/cli/)
- [Runnable example catalogue]({{docs}}/examples/)

## Build and diagnose with clear context

[Build with an AI assistant]({{docs}}/guides/ai-assisted-development/) takes you from a tested function to a validated manifest and a local HTTP request. [Trace a route back to Python]({{docs}}/guides/trace-route-to-python/) follows an HTTP log through the manifest into a multi-module project.

## Choose the right framework

Compare [Linking and Flask]({{docs}}/comparisons/flask/) for explicit handlers and extension points, or [Linking and FastAPI]({{docs}}/comparisons/fastapi/) for rich request and response models. The [FAQ]({{docs}}/faq/) covers installation and independence from APIZIT hosting.
