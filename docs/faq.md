# APIZIT Linking questions, answered

These answers describe the verified Linking 1.0.1 stable release; 0.5.0 remains historical migration evidence. Linking maps ordinary Python functions to HTTP through a versioned configuration file.

## Is Linking a Python API framework?

It provides routing, request binding, supported type conversion and function invocation through a declarative layer. Its focused scope differs from a general web framework. The optional preview adapter uses FastAPI internally.

Read [Flask]({{docs}}/comparisons/flask/), [FastAPI]({{docs}}/comparisons/fastapi/) and [V1 limits]({{docs}}/limits/#choose) for the decision boundary.

## Why is it useful with an AI assistant?

The assistant can implement and test Python first, then configure HTTP separately. The manifest maps methods and route patterns to functions. Human reviewers can inspect the same boundaries.

Linking does not manage a model's context or guarantee lower token usage. The [AI guide]({{docs}}/guides/ai-assisted-development/) demonstrates the workflow.

## Do I need an AI service or API key?

No. Linking needs no language model, AI service or AI credential. You can write and maintain the entire project yourself.

## Does Python need Linking imports or decorators?

No. The manifest references a top-level function using dotted `module:function` syntax. Arguments, defaults and supported annotations must agree with its bindings.

## Can I find code from an HTTP log?

Use the method, path and correct release's manifest to identify the target. Its dependencies, tests and data may be needed to explain a failure. The requests logger emits JSON events with a request ID, matched pattern, route ID and source fingerprint. `explain` locates the Python file and line; it does not reconstruct a complete call graph or prove the cause of an error.

Follow [route diagnosis]({{docs}}/guides/trace-route-to-python/).

## How do I install and check a project?

```text
python -m pip install "apizit-linking[preview,models]==1.0.1"
apizit-linking validate .
apizit-linking validate . --json
apizit-linking preview . --port 8080
```

Use Python 3.10–3.14 and exact pins. Core requires PyYAML; preview is an optional extra. The [quickstart]({{docs}}/quickstart/) covers environment setup.

## Does validation execute my code?

Static validation parses syntax without importing customer modules. Preview imports and runs the project in the server process. Neither validation nor import namespacing is a security sandbox.

## Can I return 201 or map an exception to 404?

Yes. response declares success status/headers; errors maps named domain exceptions to constant public 4xx/5xx errors. 204/205/HEAD omit a body. Unmapped failures become a generic JSON 500.

Legacy return schemas remain documentary; explicit typed routes validate and serialize their output. Read [the limits]({{docs}}/limits/) before adopting it.

## Do I need an APIZIT account or paid plan?

No. The package and examples are independent of APIZIT. APIZIT is one platform that consumes Linking for managed launches; its access and commercial terms are separate.

The Apache-2.0 package is on [PyPI](https://pypi.org/project/apizit-linking/1.0.1/). APIZIT remains prelaunch with protected technical environments.

## Where are examples and support?

Use [YAML]({{docs}}/reference/linking-yaml/), [CLI]({{docs}}/reference/cli/), [compatibility]({{docs}}/reference/compatibility/) and [examples]({{docs}}/examples/).

Ask public questions in [GitHub issues](https://github.com/chipsi44/apizit-linking-examples/issues). Follow [security]({{docs}}/security/) for vulnerabilities, and [releases]({{docs}}/releases/) and [migrations]({{docs}}/migrations/) before changing pins.

## Does Linking provide persistence and permissions?

Providers inject application-owned resources and principals; ordered guards enforce application policy and fail closed on missing configuration. The [standalone persistent API]({{docs}}/guides/persistent-api/) uses nested models, SQLite transactions and owner permissions without APIZIT. Linking does not provision a database, identity provider, ORM, backups or migrations.

## Can an agent check its change automatically?

Yes: validate, export the route/HTTP contract, run business tests and compare with diff. Resolved exports prepare typed models explicitly. The comparison gates changed contracts conservatively and reports unresolved model changes; it does not prove business behavior, absence of vulnerabilities or improved AI efficiency.
