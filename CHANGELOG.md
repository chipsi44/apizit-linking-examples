# Changelog

This changelog tracks the public APIZIT Linking package contract and its
canonical public documentation. Package files are distributed through
[PyPI](https://pypi.org/project/apizit-linking/); release explanations and
migrations are published on
[GitHub Pages](https://chipsi44.github.io/apizit-linking-examples/releases/).

## Unreleased

### Documentation

- Enable the public security intake and prepare the release-note and
  migration-documentation lifecycle for the next beta line.
- Document the planned 0.4-to-0.5 rebuild and APIZIT re-pin procedure without
  claiming that package 0.5.0 is available.

There is no public `apizit-linking` 0.5.0 release yet. Install commands remain
pinned to 0.4.0 until a separate publication step succeeds.

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
