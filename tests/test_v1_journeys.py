from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import httpx
from apizit_linking.fastapi import create_app

from tests.test_documented_journeys import CLI, ROOT, blocks, preview, validate


def command(*arguments):
    return subprocess.run(CLI + list(map(str, arguments)), capture_output=True, text=True)


def request(port, path, *, key=None, body=None, method="GET", extra_headers=None):
    headers = {**({"X-API-Key": key} if key else {}), **(extra_headers or {})}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers, method=method,
    )
    try:
        response = urlopen(req, timeout=3)
    except HTTPError as error:
        response = error
    with response:
        content = response.read()
        return response.status, json.loads(content) if content else None, response.headers


class PersistentJourneyTests(unittest.TestCase):
    def test_documented_bearer_recipe_verifies_tokens_and_application_permissions(self):
        import time
        import jwt

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            slug = "reference/resources-and-permissions"
            (root / "auth.py").write_text(blocks(slug, "python")[1], encoding="utf-8")
            (root / "service.py").write_text(blocks(slug, "python")[2], encoding="utf-8")
            (root / "apizit_linking.yaml").write_text(blocks(slug, "yaml")[1], encoding="utf-8")
            self.assertTrue(validate(root)["valid"])
            secret = "local-test-fixture-" * 4
            environment = {**os.environ, "LINKING_DEMO_JWT_SECRET": secret}
            now = int(time.time())
            claims = {"sub": "alice", "iss": "urn:linking-demo", "aud": "linking-demo-api",
                      "iat": now, "nbf": now, "exp": now + 300}
            def token(changes=None, *, key=secret, algorithm="HS256"):
                return jwt.encode({**claims, **(changes or {})}, key, algorithm=algorithm)
            with preview(root, environment) as port:
                def call(value=None, *, path="/identity", method="GET"):
                    headers = {"Authorization": "Bearer " + value} if value else {}
                    return request(port, path, method=method, extra_headers=headers)
                self.assertEqual(call()[0], 401)
                self.assertEqual(call(token())[1], {"user": "alice"})
                self.assertEqual(call(token(), path="/writer", method="POST")[0], 200)
                bob = token({"sub": "bob", "role": "writer"})
                self.assertEqual(call(bob)[1], {"user": "bob"})
                self.assertEqual(call(bob, path="/writer", method="POST")[0], 403)
                for invalid in [
                    token({"exp": now - 60}), token({"nbf": now + 600}),
                    token({"iss": "urn:foreign"}), token({"aud": "foreign"}),
                    token({"sub": "mallory"}), token({"sub": None}),
                    token(key="wrong-key-" * 8), token(algorithm="HS384"),
                    token(key=None, algorithm="none"), "malformed.token",
                ]:
                    status, body, _ = call(invalid)
                    self.assertEqual(status, 401)
                    self.assertNotIn(invalid, json.dumps(body))
                missing = {key: value for key, value in claims.items() if key != "exp"}
                self.assertEqual(call(jwt.encode(missing, secret, algorithm="HS256"))[0], 401)

    def test_documented_persistent_api_survives_server_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "examples/persistent-api", root, dirs_exist_ok=True)
            environment = {
                **os.environ, "LINKING_DEMO_DATABASE": str(root / "tasks.sqlite"),
                "LINKING_DEMO_WRITER_KEY": "journey-writer",
                "LINKING_DEMO_READER_KEY": "journey-reader",
                "LINKING_DEMO_OTHER_KEY": "journey-other",
            }
            self.assertTrue(validate(root)["valid"])
            self.assertFalse((root / "tasks.sqlite").exists())
            payload = {"title": "Read docs", "details": {"label": "Work"}}
            with preview(root, environment) as port:
                status, task, headers = request(port, "/tasks", method="POST", body=payload, key="journey-writer")
                self.assertEqual(status, 201)
                self.assertEqual(headers["Location"], f"/tasks/{task['id']}")
                self.assertNotIn("owner", task)
                self.assertEqual(request(port, "/tasks/1")[0], 401)
                self.assertEqual(request(port, "/tasks", method="POST", body=payload, key="journey-reader")[0], 403)
                self.assertEqual(request(port, "/tasks/1", key="journey-other")[0], 404)
                self.assertEqual(request(port, "/tasks", method="POST", body=payload, key="journey-writer")[0], 409)
                changed = {"title": "Read docs", "details": {"label": "Home"}}
                status, task, _ = request(port, "/tasks/1", method="PATCH", body=changed, key="journey-writer")
                self.assertEqual(status, 200)
                second = {"title": "Test pagination", "details": {"label": "Work"}}
                self.assertEqual(request(port, "/tasks", method="POST", body=second, key="journey-writer")[0], 201)
                status, page, _ = request(port, "/tasks?limit=1&offset=1", key="journey-reader")
                self.assertEqual(status, 200)
                self.assertEqual(len(page), 1)
                self.assertEqual(page[0]["title"], "Test pagination")
                self.assertNotIn("owner", page[0])
                self.assertEqual(len(request(port, "/tasks", key="journey-reader")[1]), 2)
                self.assertEqual(request(port, "/tasks", key="journey-other")[1], [])
                for query in ["limit=0", "limit=101", "limit=abc", "offset=-1", "offset=1000001"]:
                    self.assertEqual(request(port, "/tasks?" + query, key="journey-reader")[0], 400, query)
                invalid = {"title": "Invalid", "details": {"label": "x"}}
                self.assertEqual(request(port, "/tasks", method="POST", body=invalid, key="journey-writer")[0], 400)
            with preview(root, environment) as port:
                self.assertEqual(request(port, "/tasks/1", key="journey-reader")[1], task)
                self.assertEqual(request(port, "/missing")[0], 404)
                self.assertEqual(request(port, "/tasks", method="PUT", key="journey-writer")[0], 405)
                self.assertEqual(request(port, "/tasks/1", method="DELETE", key="journey-writer")[:2], (204, None))
                self.assertEqual(request(port, "/tasks/1", key="journey-reader")[0], 404)
                self.assertEqual(len(request(port, "/tasks", key="journey-reader")[1]), 1)

    def test_models_and_response_reference_examples_execute(self):
        for slug in ["reference/models", "reference/responses"]:
            with self.subTest(slug=slug), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "service.py").write_text(blocks(slug, "python")[0], encoding="utf-8")
                (root / "apizit_linking.yaml").write_text(blocks(slug, "yaml")[0], encoding="utf-8")
                self.assertTrue(validate(root)["valid"])
                with preview(root) as port:
                    payload = {"title": "Read docs", "details": {"label": "Work"}}
                    status, body, headers = request(port, "/tasks", body=payload, method="POST")
                    self.assertEqual(status, 201)
                    self.assertEqual(headers["Location"], "/tasks/1")
                    self.assertNotIn("internal_owner", body)
                    if slug.endswith("responses"):
                        status, body, _ = request(port, "/tasks", body={"title": "existing"}, method="POST")
                        self.assertEqual(status, 409)
                        self.assertNotIn("Private database detail", json.dumps(body))


class DiagnosisJourneyTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_http_event_locates_unchanged_library_and_gates_fix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "examples/multi-module-api", root, dirs_exist_ok=True)
            original = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*.py")}
            self.assertTrue(validate(root)["valid"])
            before = command("export", root, "--output", root / "before.json")
            self.assertEqual(before.returncode, 0, before.stderr)
            with self.assertLogs("apizit_linking.requests", level="INFO") as logs:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app(root)), base_url="http://test") as client:
                    response = await client.get("/products/42/quote?quantity=2")
            self.assertEqual(response.status_code, 200)
            event = json.loads(logs.records[0].message)
            located = command("explain", root, "--method", event["method"], "--path", "/products/42/quote", "--json")
            self.assertEqual(located.returncode, 0, located.stderr)
            location = json.loads(located.stdout)["route"]
            self.assertEqual(location["function"], "catalog.service:quote")
            self.assertEqual(location["source"]["file"], "catalog/service.py")
            self.assertGreater(location["source"]["line"], 0)
            self.assertEqual(location["route_id"], event["route_id"])
            snapshot = json.loads((root / "before.json").read_text())
            self.assertEqual(snapshot["source_fingerprint"], event["source_fingerprint"])
            self.assertEqual(original, {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in root.rglob("*.py")})
            module = root / "catalog/pricing.py"
            source = module.read_text()
            self.assertIn("round(", source)
            # A precision correction changes behavior without changing the HTTP contract.
            module.write_text(source.replace(", 2)", ", 3)"), encoding="utf-8")
            self.assertNotEqual(source, module.read_text())
            self.assertTrue(validate(root)["valid"])
            corrected = command("export", root, "--output", root / "after.json")
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            self.assertEqual(command("diff", root / "before.json", root / "after.json", "--json").returncode, 0)
            direct = subprocess.run([sys.executable, "-c", "from catalog.pricing import apply_discount; assert apply_discount(1.1234, 0) == 1.123"], cwd=root, capture_output=True, text=True)
            self.assertEqual(direct.returncode, 0, direct.stderr)
            manifest = root / "apizit_linking.yaml"
            manifest.write_text(manifest.read_text() + "    response: {status: 201}\n", encoding="utf-8")
            self.assertTrue(validate(root)["valid"])
            self.assertEqual(command("export", root, "--output", root / "breaking.json").returncode, 0)
            self.assertEqual(command("diff", root / "before.json", root / "breaking.json", "--json").returncode, 1)
