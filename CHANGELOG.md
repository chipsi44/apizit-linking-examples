# Changelog

This changelog tracks the public APIZIT Linking package contract and its
canonical public documentation. Package files are distributed through
[PyPI](https://pypi.org/project/apizit-linking/); release explanations and
migrations are published on
[GitHub Pages](https://chipsi44.github.io/apizit-linking-examples/releases/).

## Unreleased

### Documentation

- No unreleased documentation changes.

## 0.5.0 - 2026-07-23

### Added

- Useful OpenAPI 3.1 operations generated statically from compiled routes,
  including explicit and automatic input bindings.
- Minimal documentary `200`, stable Linking `400`, and generic `500` response
  descriptions. Return annotations do not validate, transform, reject, or
  reshape customer values at runtime.
- Multi-OS clean-wheel release gates for Linux, Windows, and macOS.

### Verified

- The final wheel and source distribution are publicly available from
  [PyPI](https://pypi.org/project/apizit-linking/0.5.0/).
- Canonical examples, guides, requirements, and CI use the exact
  `apizit-linking==0.5.0` release.
- Manifest `version: 1` and runtime artifact `version: 1` remain unchanged.
  Exact `engine_version` matching still requires every artifact to be
  recompiled after the package update.

### Integration status

APIZIT completed its separate final promotion with an exact 0.5.0 build and
runtime pin, a recompiled artifact, anti-vendoring checks of APIZIT source, the
generated pre-install runtime, and its wheel, 12 Linking integration tests, 89
backend tests, and a green main-branch CI.

## 0.5.0rc1 - 2026-07-23

### Added

- Useful OpenAPI 3.1 operations generated statically from compiled routes,
  including explicit parameter sources, request bodies, defaults, nullability,
  repeated values, and automatic-binding extensions.
- Swagger UI, ReDoc, and the OpenAPI document in local preview, with safe
  relocation when a customer route would shadow a documentation URL.
- Minimal documentary `200`, stable Linking `400`, and generic `500` response
  descriptions without adding runtime response validation or transformation.

### Verified

- The release workflow completed nine gated jobs: one build, six clean-wheel
  smoke jobs across Linux, Windows, and macOS on Python 3.10 and 3.14, one
  minimum-preview-dependency smoke, and one Trusted Publishing job.
- The published wheel and source distribution are available from
  [PyPI](https://pypi.org/project/apizit-linking/0.5.0rc1/).
- Manifest `version: 1` and runtime artifact `version: 1` remain unchanged;
  exact `engine_version` matching still requires recompilation.

This release candidate was the isolated evaluation build that preceded final
0.5.0. Its publication history and gates remain part of the release narrative;
new installations should use the final exact 0.5.0 pin.

## 0.4.0

### Added

- A versioned, closed runtime-artifact envelope with explicit format, artifact,
  engine, and manifest versions.
- Complete callable-signature metadata and strict startup-time drift detection.
- Explicit rejection of synchronous and asynchronous generators.
- A public, closed JSON Schema for canonical Linking manifest version 1.
- A compatibility and deprecation policy for package, manifest, diagnostic, and
  runtime-artifact contracts.
- A supported artifact-based FastAPI integration so APIZIT can depend on the
  published package instead of vendoring engine code.

### Changed

- Deployment adapters compile a manifest into a complete artifact and create the
  application with `create_app_from_runtime_artifact`.
- Runtime artifacts now require an exact `engine_version` match and must be
  recompiled after an engine update.
- `create_app_from_runtime_routes` is retained only as a documented migration
  bridge for the old unversioned route list.

See the [0.4.0 retrospective](https://chipsi44.github.io/apizit-linking-examples/releases/0.4.0/)
and [0.3-to-0.4 migration](https://chipsi44.github.io/apizit-linking-examples/migrations/0.3-to-0.4/).

## 0.3.1

### Fixed

- Packaging and public metadata fixes following the first PyPI beta.

## 0.3.0

### Added

- Public PyPI distribution with the optional `preview` dependency group.
- `apizit-linking validate` and `apizit-linking preview` commands.
- Local FastAPI-based preview for declaratively linked Python functions.

## 0.2.0

### Added

- Initial standalone APIZIT Linking package and declarative manifest compiler.
