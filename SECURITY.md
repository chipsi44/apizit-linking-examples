# Security policy

## Supported versions

APIZIT Linking is currently a public beta. The 0.4 line remains the stable beta
line. Published release candidates receive fixes during evaluation but are not
recommended as production replacements.

| Version | Supported |
| --- | --- |
| 0.4.x | Yes — current stable beta |
| 0.5.0rc1 | Evaluation candidate — reports accepted |
| 0.3.x and earlier | No |
| 0.5.0 | Not published |

Upgrade to the latest patch in the relevant supported line before reporting a
problem. Keep production on 0.4.0 while evaluating 0.5.0rc1 separately. The
canonical package is distributed through
[PyPI](https://pypi.org/project/apizit-linking/); the candidate files are
available on the
[0.5.0rc1 project page](https://pypi.org/project/apizit-linking/0.5.0rc1/).

## Report a vulnerability privately

Do **not** disclose vulnerability details in a public issue, pull request,
discussion, example, log, screenshot, or repository fork.

The private reporting URL is:

<https://github.com/chipsi44/apizit-linking-examples/security/advisories/new>

GitHub Private Vulnerability Reporting is enabled for this repository. Use the
URL above as the canonical intake channel. If it is temporarily unavailable,
open the
[minimal security contact form](https://github.com/chipsi44/apizit-linking-examples/issues/new?template=security-contact.yml)
that contains **no vulnerability details, logs, proof of concept, secrets, or
affected customer information**. Ask only for a private channel and wait for a
maintainer to respond.

A useful private report includes:

- the affected APIZIT Linking version and Python version;
- the component and deployment context;
- impact and realistic attack preconditions;
- minimal reproduction steps or a proof of concept;
- suggested mitigation, if known;
- whether the issue has been disclosed anywhere else.

Maintainers aim to acknowledge a complete report within three business days and
provide an initial assessment within seven business days. Complex investigations
can take longer. Please coordinate publication with the maintainers so users have
time to update.

## Scope

This policy covers:

- the `apizit-linking` package distributed on PyPI;
- its compiler, runtime-artifact validation, FastAPI adapter, and preview CLI;
- the public schema, examples, documentation, and release metadata in this
  repository.

The hosted APIZIT product has its own operational security process. Customer
applications, dependencies selected by customers, and infrastructure outside
these repositories are not automatically in scope.

The preview command imports and executes linked project code. It is a local
development tool for trusted code, not a sandbox, authentication boundary, or
production server. Reports that rely only on running deliberately malicious,
locally trusted project code are generally out of scope unless they cross a
documented trust boundary.

## Public bug reports

Use the public
[bug form](https://github.com/chipsi44/apizit-linking-examples/issues/new?template=bug.yml)
for non-security defects. Remove tokens, credentials, personal data, private
source code, and sensitive paths from diagnostics before posting them.
