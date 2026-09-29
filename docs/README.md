# Documentation maintenance

Edit the English Markdown in this directory and its ordered `catalog.json`. This is the single editorial source for GitHub Pages and the APIZIT website. Pages are generated offline with the portable renderer in `scripts/docs-renderer.cjs`.

## Build and validate

```sh
node scripts/build-docs.cjs
python -m unittest discover -s tests -v
node --test tests/*.test.cjs
node scripts/export-apizit-docs.cjs --website /path/to/apizit-website
node scripts/export-apizit-docs.cjs --website /path/to/apizit-website --check
```

Install `requirements.txt` and `requirements-test.txt` first. Export from a clean source commit for a release. The bundle records its commit and SHA-256 file inventory; APIZIT verifies it before loading the shared renderer. Neither build downloads documentation.

## Stable URLs and anchors

Keep existing slugs and explicit anchors. Headings may use `{#anchor}` and old aliases may use a standalone `<a id="anchor"></a>`. Internal publication links use `{{docs}}/path/`; `{{origin}}` is the selected host. Do not insert arbitrary HTML. Code, tables and links are escaped by the renderer.

The public JSON Schema remains at its existing GitHub Pages URL and retains its identity. Markdown downloads and the page catalogue support agents; `llms.txt` is a convenience index, not a promise of search ranking.

## Future official-domain switch

GitHub Pages remains public during the transition. APIZIT's protected environments keep authentication and noindex. For every catalogue slug, map `https://chipsi44.github.io/apizit-linking-examples/<slug>/` to `https://apizit.com/linking/<slug>/`, using an empty slug for the home page and retaining fragments.

Before switching, publish and verify the complete official space, schema and downloads; decide the long-term schema URL separately; remove official-site noindex only through an approved public launch; update Pages canonicals and internal distribution links to the official origin; then retain a redirect or navigation notice at every former URL. GitHub Pages cannot issue arbitrary HTTP 301 redirects, so any static redirect must include a readable link and preserve query/fragment values. Do not remove Pages until replacement URLs really exist.

Validate requests, true 404s, mobile and keyboard navigation and crawler access at the final host. Evaluate indexing and search performance from observed data after public launch.
