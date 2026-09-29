# Security policy

Keep vulnerability details out of public issues and examples. This page records supported package lines, the enabled private intake, scope, and a safe fallback for temporary service unavailability.

**Do not publish vulnerability details.** Public issues, pull requests, discussions, logs, screenshots, and forks are visible to everyone.

## Supported versions {#supported}

| Version | Security support |
| --- | --- |
| 0.5.x | Supported — current stable public beta |
| 0.5 pre-releases | Not supported — upgrade to the final 0.5 release |
| 0.4.x | Not supported — previous minor line |
| 0.3.x and earlier | Not supported |

Security fixes are provided for the latest published minor line only. Reproduce on its latest patch before reporting. Canonical package files come from [PyPI](https://pypi.org/project/apizit-linking/); the current stable public beta has a dedicated [0.5.0 page](https://pypi.org/project/apizit-linking/0.5.0/).

## Private reporting channel {#private-report}

The canonical private-report URL is: [report an APIZIT Linking vulnerability privately](https://github.com/chipsi44/apizit-linking-examples/security/advisories/new).

**Status:** GitHub Private Vulnerability Reporting is enabled for this repository. Submit technical details only through that private form.

If the private form is temporarily unavailable, create only a [minimal security contact request](https://github.com/chipsi44/apizit-linking-examples/issues/new?template=security-contact.yml) asking a maintainer for a private channel. Include no vulnerability details, proof of concept, logs, customer information, secrets, or sensitive paths.

## What to include privately {#report-content}

- APIZIT Linking and Python versions;
- affected component and deployment context;
- impact and realistic attack preconditions;
- minimal reproduction steps or a proof of concept;
- possible mitigation, if known;
- whether the issue has been disclosed elsewhere.

Maintainers aim to acknowledge a complete report within three business days and provide an initial assessment within seven business days. Coordinate any publication so a verified fix and update guidance can reach users first.

## Scope {#scope}

This policy covers:

- the `apizit-linking` package distributed on PyPI;
- compiler, artifact validation, FastAPI adapter, and preview CLI behavior;
- the public schema, examples, documentation, and release metadata here.

The hosted APIZIT product has a separate operational security process. Customer applications, customer-selected dependencies, and unrelated infrastructure are not automatically in scope.

## Preview trust boundary {#trust-boundary}

`apizit-linking preview` imports and executes linked project code. It is a local development server for trusted source, not a sandbox, authentication boundary, or production server. Merely executing deliberately malicious trusted project code is not a sandbox escape because no sandbox is promised.

## Non-security bugs {#public-bugs}

Use the [public bug form](https://github.com/chipsi44/apizit-linking-examples/issues/new?template=bug.yml) for ordinary defects. Sanitize commands and diagnostics before posting them. The repository copy of [SECURITY.md](https://github.com/chipsi44/apizit-linking-examples/blob/main/SECURITY.md) is the concise source-controlled version of this policy.
