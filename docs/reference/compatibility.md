# Compatibility policy

APIZIT Linking versions its package, manifest, and generated runtime artifact independently. This page defines which parts integrations can safely depend on.

The 1.0 candidate evaluates the stable API described here; the 1.x guarantees take effect with the final 1.0 release. The preceding 0.5 line remains a beta contract.

## Four separate contracts {#four-contracts}

| Contract | Version source | Purpose |
| --- | --- | --- |
| Python package | PyPI and `apizit_linking.__version__` | Implementation and public integration API |
| Linking manifest | Root `version` | User-authored route and binding contract |
| Runtime artifact | Closed artifact envelope | Compiled build input consumed by an HTTP adapter |
| Diagnostics | Package release and stable diagnostic codes | Machine-readable validation and request failures |

Package `0.4.x` can continue to consume a manifest declaring `version: 1`. Neither number implies the other.

## Supported Python adapter API {#python-api}

The supported compiler/adapter surface includes:

- `apizit_linking.discover_linking_file`
- `apizit_linking.compile_linking_file`
- `apizit_linking.CompilationResult` and its documented runtime artifact serialization
- `RUNTIME_ARTIFACT_FORMAT`, `RUNTIME_ARTIFACT_VERSION`, and `runtime_routes_from_dict`
- `apizit_linking.fastapi.create_app_from_runtime_artifact`

Deployment adapters use this flow to discover a manifest, compile once, serialize a closed artifact, and build the HTTP app from that artifact. They must depend on a released APIZIT Linking package instead of vendoring its source code.

Other importable models, loaders, and conversion helpers are advanced implementation surfaces unless this policy explicitly lists them. A name in `__all__` is not by itself a stability promise. Names beginning with an underscore are private.

`create_app_from_runtime_routes` supports the old unversioned list only as a migration bridge. New adapters use `create_app_from_runtime_artifact`.

## Manifest schema guarantees {#manifest}

The [canonical schema v1]({{docs}}/schema/apizit-linking-v1.schema.json) becomes a closed authoring contract with the 0.4 line. Existing valid canonical v1 documents remain valid and keep their meaning. Removing a field, changing an existing field's meaning, or invalidating an existing canonical document requires a new root manifest version.

The compiler retains selected migration inputs that the canonical schema rejects: an omitted root version, case-normalized methods, and historical slash module references. Migration acceptance does not redefine the canonical schema. New manifests should pass both the schema and `apizit-linking validate`.

## Diagnostic guarantees {#diagnostics}

Integrations can branch on `code` and inspect `severity`, `route_index`, `field`, `parameter`, and `details`. Existing codes keep their broad meaning and severity within a compatible package line.

- Feature releases can add new diagnostic codes.
- `details` can gain keys; consumers ignore unknown keys.
- Human-readable `message` text can improve and is not parsed.
- Removing or incompatibly redefining a code follows deprecation rules.

## Runtime artifact guarantees {#artifacts}

Runtime artifacts are generated build outputs, not manifests. Their closed envelope requires `format`, `version`, `engine_version`, `manifest_version`, and `routes`. Unsupported versions, unknown fields, malformed routes, and Python signatures that drift after compilation are rejected instead of guessed.

Each route records its ordered parameters, parameter kinds, required/default state, annotations, `callable_kind` (`sync` or `async`), and `return_annotation`. A change to any of those dimensions fails before the HTTP application starts. Synchronous and asynchronous generators are rejected until streaming has a separate explicit contract.

Adapters treat artifacts as opaque, record the engine version and artifact hash in deployment provenance, and recompile rather than editing routes by hand. An artifact executes only with the exact `engine_version` that compiled it, so any packaged-engine update requires recompilation. The artifact `version` describes the serialization shape; a breaking serialization change receives a new format version.

## Semantic Versioning and deprecation {#semver}

Before 1.0, `0.y.z` patches are compatible within `0.y`; a new minor can refine a beta surface with migration notes. Starting at 1.0, patches are compatible fixes, minors add backward-compatible functionality, and majors can remove deprecated contracts.

Normal deprecations appear in release notes, emit `DeprecationWarning` for identifiable Python call sites, and remain for at least one following minor during 0.x. After 1.0 they remain for at least two minor releases and normally 90 days. Security, data-corruption, or documented-correctness fixes may use a shorter window with prominent release notes.

- [Read canonical release notes and the public changelog]({{docs}}/releases/)
- [Apply the version-by-version migration guides]({{docs}}/migrations/)
- [Read the canonical Linking YAML contract]({{docs}}/reference/linking-yaml/)
- [Validate a project from the CLI]({{docs}}/reference/cli/)
- [Review current product boundaries]({{docs}}/limits/)

## V1 application and tooling surface

The 1.0 contract additionally documents fastapi.create_app, create_app_from_compilation and create_app_from_routes; extensions.RuntimeExtensions, Provider, ExecutionContext and AccessDenied; limits.RequestLimits; and the routes/explain/export/diff CLI commands. Provider/guard call signatures and scope rules are documented in [resources]({{docs}}/reference/resources-and-permissions/). Imported internal helpers remain private.

New optional manifest fields extend schema v1 while preserving existing meanings. The 1.0 runtime artifact uses format v2, including optional runtime factory data and explicit route contracts. Artifacts remain opaque and bound to their exact compiling engine. Contract-export format v1 is a separate inspection snapshot; conservative diff outcomes do not establish business compatibility. See [0.5 to 1.0]({{docs}}/migrations/0.5-to-1.0/).
