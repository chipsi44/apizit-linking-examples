# Release notes

PyPI is the source of installable package files. These pages are the canonical human-readable release history, with migrations kept next to every compatibility change.

**Stable public beta: 0.5.0.** The final wheel and source distribution are published on [PyPI](https://pypi.org/project/apizit-linking/0.5.0/). Examples, guides, and CI now pin the exact final release.

## Two public channels, one role each {#channels}

| Channel | Canonical content |
| --- | --- |
| [PyPI](https://pypi.org/project/apizit-linking/) | Installable wheel, source distribution, version, metadata, and file hashes |
| This GitHub Pages site | Release explanation, compatibility impact, migrations, and known limits |
| [Public changelog](https://github.com/chipsi44/apizit-linking-examples/blob/main/CHANGELOG.md) | Compact chronological summary suitable for repository readers |

This examples repository deliberately does not publish GitHub Releases for the engine. GitHub-generated source archives here would contain the examples, not the private engine source or the canonical PyPI distributions.

## Published releases {#published}

Stable public beta

### [0.5.0]({{docs}}/releases/0.5.0/)

Useful OpenAPI 3.1, minimal documentary responses, and a release pipeline verified by multi-OS clean-wheel smokes. The page preserves the 0.5.0rc1 evaluation history.

Previous stable beta

### [0.4.0 retrospective]({{docs}}/releases/0.4.0/)

Closed runtime artifact v1, strict callable drift detection, generator rejection, public schema v1, and the non-vendored APIZIT adapter contract.

Migration

### [0.3 to 0.4]({{docs}}/migrations/0.3-to-0.4/)

Replace bare runtime route lists with the versioned artifact envelope, validate canonical manifests, and rebuild deployment outputs.

## Move from 0.4 to final 0.5 deliberately {#migration}

**Exact final pin:** install [0.5.0](https://pypi.org/project/apizit-linking/0.5.0/) and recompile every generated runtime artifact. Manifest version 1 and runtime artifact version 1 remain unchanged, while exact engine identity still prevents reuse of 0.4-generated artifacts.

The accompanying [final 0.4-to-0.5 migration guide]({{docs}}/migrations/0.4-to-0.5/) includes the independently verified APIZIT platform promotion.

## Install the current release {#install-current}

Terminal

```text
python -m pip install "apizit-linking[preview]==0.5.0"
apizit-linking validate .
apizit-linking preview . --port 8080
```
