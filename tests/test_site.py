from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = REPOSITORY_ROOT / "site"
BASE_URL = "https://chipsi44.github.io/apizit-linking-examples/"
SCHEMA_RELATIVE_PATH = Path("schema/apizit-linking-v1.schema.json")
PUBLIC_SCHEMA_URL = f"{BASE_URL}{SCHEMA_RELATIVE_PATH.as_posix()}"

PUBLIC_PAGES = {
    "index.html": BASE_URL,
    "quickstart/index.html": f"{BASE_URL}quickstart/",
    "reference/linking-yaml/index.html": f"{BASE_URL}reference/linking-yaml/",
    "reference/cli/index.html": f"{BASE_URL}reference/cli/",
    "reference/compatibility/index.html": f"{BASE_URL}reference/compatibility/",
    "examples/index.html": f"{BASE_URL}examples/",
    "guides/index.html": f"{BASE_URL}guides/",
    "guides/expose-python-function-as-http-api-without-decorators/index.html": (
        f"{BASE_URL}guides/expose-python-function-as-http-api-without-decorators/"
    ),
    "guides/keep-python-business-logic-independent-from-fastapi/index.html": (
        f"{BASE_URL}guides/keep-python-business-logic-independent-from-fastapi/"
    ),
    "guides/turn-python-library-into-api-with-yaml/index.html": (
        f"{BASE_URL}guides/turn-python-library-into-api-with-yaml/"
    ),
    "limits/index.html": f"{BASE_URL}limits/",
    "releases/index.html": f"{BASE_URL}releases/",
    "releases/0.4.0/index.html": f"{BASE_URL}releases/0.4.0/",
    "releases/0.5.0/index.html": f"{BASE_URL}releases/0.5.0/",
    "migrations/index.html": f"{BASE_URL}migrations/",
    "migrations/0.3-to-0.4/index.html": f"{BASE_URL}migrations/0.3-to-0.4/",
    "migrations/0.4-to-0.5/index.html": f"{BASE_URL}migrations/0.4-to-0.5/",
    "security/index.html": f"{BASE_URL}security/",
}


class _HtmlFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = {name: value or "" for name, value in attrs}
        self.tags.append((tag, attributes))
        if element_id := attributes.get("id"):
            self.ids.add(element_id)
        if href := attributes.get("href"):
            self.links.append(href)


def _parse_html(path: Path) -> tuple[str, _HtmlFacts]:
    source = path.read_text(encoding="utf-8")
    parser = _HtmlFacts()
    parser.feed(source)
    return source, parser


def _canonical_from(parser: _HtmlFacts) -> str | None:
    for tag, attributes in parser.tags:
        if tag == "link" and attributes.get("rel") == "canonical":
            return attributes.get("href")
    return None


def _target_for(url: str) -> tuple[Path, str]:
    parsed = urlparse(url)
    expected_prefix = "/apizit-linking-examples/"
    if parsed.netloc and parsed.netloc != "chipsi44.github.io":
        raise ValueError(f"Not an internal URL: {url}")
    if not parsed.path.startswith(expected_prefix):
        raise AssertionError(f"Internal URL escapes the project path: {url}")

    relative = unquote(parsed.path.removeprefix(expected_prefix))
    if not relative or relative.endswith("/"):
        relative = f"{relative}index.html"
    return SITE_ROOT / relative, parsed.fragment


class DocumentationSiteTests(unittest.TestCase):
    def test_published_schema_is_an_exact_canonical_copy(self) -> None:
        canonical = REPOSITORY_ROOT / SCHEMA_RELATIVE_PATH
        published = SITE_ROOT / SCHEMA_RELATIVE_PATH

        self.assertTrue(canonical.is_file(), canonical)
        self.assertTrue(published.is_file(), published)
        self.assertEqual(published.read_bytes(), canonical.read_bytes())

        schema = json.loads(canonical.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], PUBLIC_SCHEMA_URL)
        self.assertEqual(schema["properties"]["version"]["const"], 1)
        self.assertNotIn("response", schema["$defs"]["route"]["properties"])

    def test_compatibility_policy_names_each_public_contract(self) -> None:
        policy = (
            SITE_ROOT / "reference" / "compatibility" / "index.html"
        ).read_text(encoding="utf-8")

        for expected in (
            "discover_linking_file",
            "compile_linking_file",
            "CompilationResult",
            "RUNTIME_ARTIFACT_VERSION",
            "create_app_from_runtime_artifact",
            "Manifest schema guarantees",
            "Diagnostic guarantees",
            "Runtime artifact guarantees",
            "callable_kind",
            "return_annotation",
            "Semantic Versioning and deprecation",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, policy)

    def test_public_pages_have_unique_canonical_metadata_and_valid_json_ld(self) -> None:
        seen_titles: set[str] = set()
        seen_descriptions: set[str] = set()

        for relative_path, expected_canonical in PUBLIC_PAGES.items():
            with self.subTest(page=relative_path):
                path = SITE_ROOT / relative_path
                self.assertTrue(path.is_file(), path)
                source, parser = _parse_html(path)

                self.assertTrue(source.lower().startswith("<!doctype html>"))
                self.assertRegex(source, r'<html\s+lang="en">')
                self.assertIn('class="skip-link"', source)
                self.assertIn('<main id="main-content"', source)
                self.assertEqual(_canonical_from(parser), expected_canonical)

                title_match = re.search(r"<title>([^<]+)</title>", source)
                self.assertIsNotNone(title_match)
                title = title_match.group(1).strip()
                self.assertNotIn(title, seen_titles)
                seen_titles.add(title)

                description_match = re.search(
                    r'<meta\s+name="description"\s+content="([^"]+)"',
                    source,
                    flags=re.DOTALL,
                )
                self.assertIsNotNone(description_match)
                description = " ".join(description_match.group(1).split())
                self.assertGreaterEqual(len(description), 60)
                self.assertNotIn(description, seen_descriptions)
                seen_descriptions.add(description)

                json_ld_blocks = re.findall(
                    r'<script\s+type="application/ld\+json">\s*(.*?)\s*</script>',
                    source,
                    flags=re.DOTALL,
                )
                self.assertTrue(json_ld_blocks, f"Missing JSON-LD in {relative_path}")
                for block in json_ld_blocks:
                    json.loads(block)

    def test_404_is_index_safe(self) -> None:
        source, _ = _parse_html(SITE_ROOT / "404.html")
        self.assertIn('name="robots" content="noindex, follow"', source)
        self.assertNotIn('rel="canonical"', source)
        self.assertIn('<main id="main-content"', source)

    def test_every_internal_link_and_fragment_resolves(self) -> None:
        html_files = tuple(SITE_ROOT.rglob("*.html"))
        self.assertEqual(len(html_files), len(PUBLIC_PAGES) + 1)

        facts_by_path = {path: _parse_html(path)[1] for path in html_files}
        for page, facts in facts_by_path.items():
            page_relative = page.relative_to(SITE_ROOT).as_posix()
            page_url = (
                BASE_URL
                if page_relative == "index.html"
                else urljoin(BASE_URL, page_relative)
            )
            for href in facts.links:
                with self.subTest(page=page_relative, href=href):
                    if href.startswith("#"):
                        self.assertIn(href[1:], facts.ids)
                        continue

                    resolved = urljoin(page_url, href)
                    parsed = urlparse(resolved)
                    if parsed.scheme not in {"http", "https"}:
                        continue
                    if parsed.netloc != "chipsi44.github.io":
                        continue

                    target, fragment = _target_for(resolved)
                    self.assertTrue(target.is_file(), f"{href} resolves to missing {target}")
                    if fragment and target.suffix == ".html":
                        self.assertIn(fragment, facts_by_path[target].ids)

    def test_sitemap_and_robots_publish_the_canonical_set(self) -> None:
        sitemap = ET.parse(SITE_ROOT / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        actual_urls = {
            element.text
            for element in sitemap.findall("s:url/s:loc", namespace)
            if element.text
        }
        self.assertEqual(actual_urls, set(PUBLIC_PAGES.values()))

        robots = (SITE_ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("User-agent: OAI-SearchBot", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn(f"Sitemap: {BASE_URL}sitemap.xml", robots)

    def test_public_site_does_not_claim_the_private_engine_repository(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (*SITE_ROOT.rglob("*.html"), SITE_ROOT / "llms.txt")
        )
        self.assertNotIn(
            'href="https://github.com/chipsi44/apizit-linking"',
            public_text,
        )
        self.assertNotIn(
            "git clone https://github.com/chipsi44/apizit-linking.git",
            public_text,
        )

        homepage = (SITE_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('"softwareVersion": "0.5.0"', homepage)
        self.assertNotIn('"codeRepository"', homepage)

    def test_three_search_guides_are_substantive_and_reproducible(self) -> None:
        guide_slugs = {
            "expose-python-function-as-http-api-without-decorators",
            "keep-python-business-logic-independent-from-fastapi",
            "turn-python-library-into-api-with-yaml",
        }
        actual_slugs = {
            path.parent.name
            for path in (SITE_ROOT / "guides").glob("*/index.html")
        }
        self.assertEqual(actual_slugs, guide_slugs)

        for slug in guide_slugs:
            with self.subTest(guide=slug):
                source = (
                    SITE_ROOT / "guides" / slug / "index.html"
                ).read_text(encoding="utf-8")
                visible_text = re.sub(r"<[^>]+>", " ", source)
                self.assertGreater(len(visible_text.split()), 650)
                self.assertIn('"@type": "TechArticle"', source)
                self.assertIn('apizit-linking[preview]==0.5.0', source)

    def test_release_migration_and_security_links_are_site_wide(self) -> None:
        required_links = (
            "/apizit-linking-examples/releases/",
            "/apizit-linking-examples/migrations/",
            "/apizit-linking-examples/security/",
        )
        for relative_path in PUBLIC_PAGES:
            source = (SITE_ROOT / relative_path).read_text(encoding="utf-8")
            for link in required_links:
                with self.subTest(page=relative_path, link=link):
                    self.assertIn(f'href="{link}"', source)

    def test_0_5_material_documents_final_release_and_verified_apizit(self) -> None:
        release = (
            SITE_ROOT / "releases" / "0.5.0" / "index.html"
        ).read_text(encoding="utf-8")
        migration = (
            SITE_ROOT / "migrations" / "0.4-to-0.5" / "index.html"
        ).read_text(encoding="utf-8")
        combined = f"{release}\n{migration}"

        for expected in (
            "0.5.0rc1",
            "https://pypi.org/project/apizit-linking/0.5.0/",
            'apizit-linking[preview]==0.5.0',
            "Manifest <code>version: 1</code>",
            "Runtime artifact <code>version: 1</code>",
            "exact <code>engine_version</code>",
            "recompil",
            "APIZIT",
            "promotion is verified",
            "documentary only",
            "nine gated jobs",
            "six clean-environment smoke jobs",
            "12 Linking",
            "89 backend",
            "anti-vendoring",
            "main-branch CI is green",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, combined)

        self.assertIn("response model", combined)
        self.assertRegex(release, r"do not\s+validate or transform")
        self.assertRegex(combined, r"no Linking engine source is\s+vendored")
        self.assertIn("0.5.0 is available from", combined)
        self.assertNotIn("final 0.5.0 is not published", combined)
        self.assertNotIn("PROMOTION_STATUS=PENDING", combined)

    def test_stable_examples_guides_and_ci_are_pinned_to_0_5_0(self) -> None:
        requirements = (REPOSITORY_ROOT / "requirements.txt").read_text(
            encoding="utf-8"
        )
        self.assertEqual(requirements.strip(), "apizit-linking[preview]==0.5.0")

        stable_surfaces = (
            REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml",
            SITE_ROOT / "quickstart" / "index.html",
            *tuple((SITE_ROOT / "guides").glob("*/index.html")),
        )
        for path in stable_surfaces:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT).as_posix()):
                source = path.read_text(encoding="utf-8")
                self.assertIn("0.5.0", source)
                self.assertNotIn("0.4.0", source)
                self.assertNotIn("0.5.0rc1", source)

    def test_public_security_channel_is_documented_as_enabled(self) -> None:
        security_url = (
            "https://github.com/chipsi44/apizit-linking-examples/"
            "security/advisories/new"
        )
        policy = (REPOSITORY_ROOT / "SECURITY.md").read_text(encoding="utf-8")
        page = (SITE_ROOT / "security" / "index.html").read_text(encoding="utf-8")

        self.assertIn(security_url, policy)
        self.assertIn(security_url, page)
        self.assertIn("Private Vulnerability Reporting is enabled", policy)
        self.assertRegex(page, r"Private Vulnerability Reporting is enabled")
        self.assertNotIn("not active yet", policy)
        self.assertIn("Do **not** disclose vulnerability details", policy)
        self.assertIn("latest published minor line only", policy)
        self.assertIn("0.5.x", policy)
        self.assertIn("0.4.x", policy)
        self.assertIn("No — previous minor line", policy)
        self.assertIn("0.5.x</td>", page)
        self.assertIn("0.4.x</td>", page)
        self.assertIn("Not supported — previous minor line</td>", page)
        self.assertNotIn("Not published</td>", page)

        for name in ("bug.yml", "feature.yml"):
            source = (
                REPOSITORY_ROOT / ".github" / "ISSUE_TEMPLATE" / name
            ).read_text(encoding="utf-8")
            with self.subTest(issue_form=name):
                self.assertIn("Security warning", source)
                self.assertIn("security policy", source)
                self.assertIn("customer data", source)

        contact_form = (
            REPOSITORY_ROOT
            / ".github"
            / "ISSUE_TEMPLATE"
            / "security-contact.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("this issue is public", contact_form)
        self.assertIn("no vulnerability details", contact_form)
        self.assertNotIn("type: textarea", contact_form)

        config = (
            REPOSITORY_ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("blank_issues_enabled: false", config)
        self.assertIn(f"{BASE_URL}security/", config)

    def test_public_changelog_and_machine_index_publish_final_and_rc_history(self) -> None:
        changelog = (REPOSITORY_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        llms = (SITE_ROOT / "llms.txt").read_text(encoding="utf-8")

        self.assertIn("## Unreleased", changelog)
        self.assertIn("## 0.4.0", changelog)
        self.assertIn("## 0.5.0rc1 - 2026-07-23", changelog)
        self.assertIn("## 0.5.0 - 2026-07-23", changelog)
        self.assertNotIn("PROMOTION_STATUS=PENDING", changelog)
        self.assertIn("12 Linking integration tests", changelog)
        self.assertIn("89 backend tests", changelog)

        for expected in (
            f"{BASE_URL}releases/",
            f"{BASE_URL}releases/0.4.0/",
            f"{BASE_URL}releases/0.5.0/",
            f"{BASE_URL}migrations/",
            f"{BASE_URL}migrations/0.3-to-0.4/",
            f"{BASE_URL}migrations/0.4-to-0.5/",
            f"{BASE_URL}security/",
            "apizit-linking[preview]==0.5.0",
            "Response annotations are documentary only",
            "nine gated jobs",
            "six clean-wheel",
            "12 Linking",
            "89 backend",
            "anti-vendoring",
            "main-branch CI is green",
            "does not publish engine GitHub Releases",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, llms)


if __name__ == "__main__":
    unittest.main()
