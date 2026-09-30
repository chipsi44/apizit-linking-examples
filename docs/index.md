# Python APIs with clear context for AI

**Keep the code. Add the API.** APIZIT Linking maps ordinary Python functions to HTTP routes through one versioned YAML or JSON file. Give your AI assistant a clear place to inspect the HTTP contract, while keeping the Python understandable to the people who maintain it.

Write and test your Python functions. Define the HTTP contract separately. Follow routes straight back to your code.

[Run the quickstart]({{docs}}/quickstart/) · [Install Linking](#install) · [Fork the examples](https://github.com/chipsi44/apizit-linking-examples/fork)

## Your function, then its API {#workflow-title}

Keep ordinary Python in `customer_service.py`:

```python
def create_customer(customer_name: str, age: int) -> dict[str, str | int]:
    return {"name": customer_name, "age": age}
```

Describe HTTP in `apizit_linking.yaml`:

```yaml
version: 1
routes:
  - path: /customers
    method: POST
    function: customer_service:create_customer
    parameters:
      customer_name:
        source:
          location: body
          name: name
      age:
        source:
          location: body
          name: age
```

The JSON field `name` becomes the Python argument `customer_name`. The function imports neither Linking nor a web framework. It remains callable from a unit test, script, notebook or another adapter.

## Give an AI a focused next step {#designed-for-title}

### Write Python, then wire HTTP

Ask an assistant to implement and test business behavior first. Once the signature is clear, ask it to declare the route and request sources. A reviewer can check the calculation separately from its exposure.

This separation can reduce the material an agent needs for a specific change. Its actual effect on context size, tokens, time and accuracy depends on the project and assistant. Linking does not impose a model or automatically manage its context.

### Follow the route to the function

```text
GET /products/42/quote
  → /products/{product_id}/quote in apizit_linking.yaml
  → catalog.service:quote
  → catalog/service.py
```

The declared routes share one map. An assistant or developer can inspect it before opening the relevant function and dependencies. Use the method and the manifest belonging to the running release; a URL alone does not establish a bug's cause.

### Check the proposed contract

Static validation inspects Python syntax and supported signatures without importing customer modules. It detects missing targets, incompatible bindings and route collisions. Structured diagnostics give a human or agent a concrete correction to make.

Export the effective route map, locate a function with `explain`, and compare a proposed contract with `diff`. Explicit `validation: typed` prepares request and response validators from the same Pydantic adapters used by OpenAPI. Legacy routes retain their existing conversion behavior.

## Install a reproducible version {#install}

Current documented package: **1.0.1, stable release**. Its wheel and source distribution are verified on PyPI; 0.5.0 remains historical migration evidence. Supported Python: **3.10–3.14**. License: **Apache-2.0**.

```text
python -m pip install "apizit-linking[preview,models]==1.0.1"
apizit-linking validate .
apizit-linking validate . --json
apizit-linking preview . --port 8080
```

The core requires PyYAML; preview adds the optional FastAPI adapter and local server, and the optional `models` extra enables typed contracts. Preview imports and executes the project. Run it on reviewed code with development data.

## Choose your next step {#learn-title}

| Your starting point | Read next |
| --- | --- |
| Tested Python functions | [Turn a library into an API]({{docs}}/guides/turn-python-library-into-api-with-yaml/) |
| An assistant is helping write a new API | [AI-assisted development]({{docs}}/guides/ai-assisted-development/) |
| A request failed | [Trace a route to Python]({{docs}}/guides/trace-route-to-python/) |
| You are choosing an HTTP architecture | [Compare Flask]({{docs}}/comparisons/flask/) and [FastAPI]({{docs}}/comparisons/fastapi/) |
| You need a persistent, protected API | [Standalone SQLite API]({{docs}}/guides/persistent-api/) |
| You need exact configuration behavior | [YAML reference]({{docs}}/reference/linking-yaml/) |

## Know where Linking fits

Choose Linking when keeping Python independent from HTTP matters and its V1 contract covers your needs. Full web frameworks can also have excellent service layers and route maps; Linking makes the external manifest the default binding boundary.

V1 supports declared response statuses and headers, safe business-exception mappings, optional typed models, injected resources and permissions. Streaming and WebSockets remain outside its JSON API contract. Read [fit and limits]({{docs}}/limits/#choose), [HTTP responses]({{docs}}/reference/responses/) and [typed models]({{docs}}/reference/models/) before choosing a validation mode.

## Run independently, explore hosting separately

The package and local examples need no APIZIT account or subscription. APIZIT is one platform that consumes the compiled contract for managed API launches. The platform remains prelaunch with protected technical environments; its access and availability are separate from the publicly installable package.

[Explore APIZIT](https://apizit.com/) · [Browse examples]({{docs}}/examples/) · [Read the FAQ]({{docs}}/faq/)

See [compatibility]({{docs}}/reference/compatibility/), [releases]({{docs}}/releases/), [migrations]({{docs}}/migrations/) and [security]({{docs}}/security/) before changing a version pin.
