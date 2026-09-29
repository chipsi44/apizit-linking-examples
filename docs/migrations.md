# Migration guides

A package version, manifest version, runtime-artifact version, and exact artifact engine identity are separate contracts. Use the guide for every minor upgrade instead of changing a pin in isolation.

## Available migrations {#available}

Published path

### [0.3 to 0.4]({{docs}}/migrations/0.3-to-0.4/)

Adopt the closed runtime artifact, strict signature metadata, public schema, generator rejection, and supported non-vendored adapter flow.

Published final migration

### [0.4 to 0.5]({{docs}}/migrations/0.4-to-0.5/)

Move from 0.4.0 to final 0.5.0 with fresh artifacts while manifest v1 and runtime artifact v1 remain unchanged. The separate APIZIT promotion is now verified.

## Read version fields correctly {#model}

| Value | What it versions | Upgrade rule |
| --- | --- | --- |
| Package version | Compiler, CLI, adapter, and public Python API release | Pin an exact released version in reproducible deployments. |
| Manifest `version` | User-authored Linking YAML contract | Change only when the authoring contract itself changes. |
| Artifact `version` | Generated serialization envelope | Change only for an incompatible artifact-shape revision. |
| Artifact `engine_version` | Exact compiler/runtime implementation identity | Must equal the runtime package; always recompile after an update. |

Runtime artifacts are generated outputs. Do not patch `engine_version`, routes, or signatures by hand to make an old artifact load under a new package.

## Compatibility source of truth {#policy}

The [compatibility policy]({{docs}}/reference/compatibility/) defines guarantees and deprecation windows. Release notes state what changed; migrations translate those changes into actions for project authors and adapter owners.
