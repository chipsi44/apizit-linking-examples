# Linking YAML reference

The versioned contract that maps HTTP routes and request values to ordinary Python function parameters.

This reference describes the contract supported by **APIZIT Linking 0.5.0**. Unknown fields and unknown versions are blocking validation errors.

## Editor validation {#editor-schema}

The canonical Draft 2020-12 schema is available as [raw JSON Schema]({{docs}}/schema/apizit-linking-v1.schema.json). Editors can use it for completion, field documentation, and immediate structural validation.

### VS Code and YAML Language Server {#vscode-schema}

With the Red Hat YAML extension or another YAML Language Server client, add this directive as the first line:

apizit_linking.yaml

```text
# yaml-language-server: $schema=https://chipsi44.github.io/apizit-linking-examples/schema/apizit-linking-v1.schema.json
version: 1
```

### PyCharm {#pycharm-schema}

Open **Settings | Languages & Frameworks | Schemas and DTDs | JSON Schema Mappings**, create a mapping that uses the schema URL above, and apply it to `apizit_linking.yaml`, `apizit_linking.yml`, and `apizit_linking.json`.

The schema describes canonical files. Run `apizit-linking validate .` as well: only the compiler can check the referenced Python files, function signatures, bindings, and route collisions.

## Manifest discovery {#file-discovery}

When a target is a directory, APIZIT Linking searches its root in this compatibility order:

1. `apizit_linking.yaml`
2. `apizit_linking.yml`
3. `apizit_linking.json`

YAML is the canonical documentation format. The manifest is named `apizit_linking`, not `linking_apizit`.

## Root contract {#root-contract}

apizit_linking.yaml

```yaml
version: 1

runtime:
  language: python
  version: "3.12"

routes:
  - path: /customers/{customer_id}
    method: PATCH
    function: customer_service:update_customer
    parameters:
      customer_id:
        source:
          location: path
          name: customer_id
      display_name:
        source:
          location: body
          name: name
```

| Field | Required | V1 rule |
| --- | --- | --- |
| `version` | Yes | Must be the integer `1`. |
| `runtime` | No | Optional Python runtime metadata. |
| `routes` | Yes | A non-empty list of closed route objects. |

### Runtime metadata {#runtime}

`runtime.language` is `python`. `runtime.version` is an optional quoted Python minor version in `major.minor` form, such as `"3.12"`.

The standalone compiler validates the syntax but does not select infrastructure. A deployment platform must decide which runtimes it supports. APIZIT currently accepts Python 3.12 and uses 3.12 when the field is omitted.

## Route objects {#routes}

| Field | Meaning | Example |
| --- | --- | --- |
| `path` | Absolute HTTP path. Placeholders use matching `{parameter_name}` segments. | `/customers/{customer_id}` |
| `method` | `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, or `HEAD`. | `PATCH` |
| `function` | Canonical dotted `module:function` target relative to the project root. | `catalog.service:quote` |
| `parameters` | Optional mapping from Python parameter name to request binding. | `customer_id: …` |

Methods are canonical in uppercase. The compiler accepts legacy lowercase methods and normalizes them. Linked functions must be top-level functions in a Python module or package inside the project root.

A canonical path starts with `/`, contains no whitespace, query string, or fragment, and uses balanced placeholders such as `{customer_id}`. Each placeholder is a unique, non-keyword portable Python identifier. A canonical function target uses portable Python identifiers separated by dots, contains exactly one colon, and cannot point into the reserved top-level `apizit_linking` module.

### Collisions and route ordering {#route-ordering}

Static paths are more specific than placeholders. For example, `/customers/search` wins over `/customers/{customer_id}`, regardless of declaration order. Duplicate routes and overlapping patterns with no safe specificity order are rejected during validation.

## Explicit parameter sources {#explicit-sources}

The canonical binding object maps one external request value to one Python parameter:

Explicit body binding

```text
parameters:
  customer_name:
    source:
      location: body
      name: name
```

Here, JSON body field `name` becomes Python argument `customer_name`. When a source is explicit, only that source is inspected; there is no fallback. Canonical external names are non-empty, single-line strings without leading or trailing whitespace.

| Location | Reads from | Name matching |
| --- | --- | --- |
| `path` | Route placeholder | Exact |
| `query` | URL query string | Exact |
| `header` | HTTP request header | Case-insensitive |
| `body` | Top-level JSON object field | Exact |
| `form` | Form field | Exact |
| `file` | Multipart file field | Exact |

One route cannot require a JSON `body` parameter together with `form` or `file`. Those request encodings are incompatible, so validation reports `INCOMPATIBLE_REQUEST_SOURCES`.

## Automatic parameter resolution {#automatic-mode}

If a Python parameter has no explicit source, V1 searches for its Python name in this deterministic order:

```text
path > query > header > body > form > file
```

The first present value wins. Explicit bindings are recommended for public contracts because they document intent and do not depend on precedence.

## Missing values, defaults, and null {#defaults-and-null}

- A missing required parameter produces `PARAMETER_NOT_FOUND`, or `PARAMETER_NOT_FOUND_IN_SOURCE` for an explicit binding.
- If the Python function defines a default, an absent input is omitted from the call so Python applies that default.
- `T | None` is still required unless the function also defines a default.
- Missing, JSON `null`, and an empty string are distinct.
- JSON `null` is accepted only for a nullable annotation.

## Built-in conversion {#types}

V1 converts common request representations according to the Python annotation:

- `str`, `int`, `float`, and `bool`;
- nullable unions such as `str | None`;
- JSON lists, including typed `list[T]` items;
- JSON objects, including typed `dict[K, V]` entries.

Invalid present values produce `INVALID_PARAMETER`. Unknown or custom annotations currently receive the adapter-provided value unchanged.

## Supported function signatures {#signatures}

Normal positional-or-keyword parameters and keyword-only parameters are supported. Python defaults and sync or async functions are supported. Positional-only parameters, `*args`, and `**kwargs` are rejected because HTTP inputs are resolved by name.

## What static validation checks {#validation}

Validation parses source code and aggregates diagnostics for the document, route, module file, top-level function, signature, configured parameters, sources, path bindings, and route collisions. Customer modules are not imported or executed.

Runtime module loading uses a project-private namespace to prevent same-named modules from different projects colliding. This is import isolation, not a security sandbox.

## Compatibility behavior {#compatibility}

The official schema accepts canonical authoring forms only. For migration, the compiler currently interprets a missing version as V1 and emits `IMPLICIT_VERSION`, normalizes method case and selected surrounding whitespace, and accepts historical extensionless slash targets with `LEGACY_FUNCTION_REFERENCE`. New files always use explicit `version: 1`, uppercase methods, trimmed values, and dotted `module:function` targets.

- [Validate this contract from the CLI]({{docs}}/reference/cli/)
- [See each request source in runnable projects]({{docs}}/examples/)
- [Review V1 response and runtime boundaries]({{docs}}/limits/)
- [Read the package, schema, diagnostics, and artifact compatibility policy]({{docs}}/reference/compatibility/)
