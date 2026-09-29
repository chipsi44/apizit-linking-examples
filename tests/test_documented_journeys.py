from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, "-c", "from apizit_linking.cli import main; main()"]


def blocks(slug: str, language: str) -> list[str]:
    markdown = (ROOT / "docs" / (slug + ".md")).read_text(encoding="utf-8")
    return re.findall(r"```" + language + r"\n(.*?)\n```", markdown, re.DOTALL)


def validate(project: Path) -> dict:
    result = subprocess.run(
        CLI + ["validate", str(project), "--json"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


@contextmanager
def preview(project: Path):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    with tempfile.TemporaryFile() as logs:
        process = subprocess.Popen(
            CLI + ["preview", str(project), "--port", str(port)],
            stdout=logs, stderr=logs,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    logs.seek(0)
                    raise AssertionError(logs.read().decode(errors="replace"))
                try:
                    with urlopen(f"http://127.0.0.1:{port}/openapi.json", timeout=1):
                        break
                except (URLError, TimeoutError):
                    time.sleep(0.05)
            else:
                raise AssertionError("Preview did not become ready.")
            yield port
        finally:
            process.terminate()
            process.wait(timeout=10)


class DocumentedJourneysTests(unittest.TestCase):
    def test_home_function_manifest_and_http_example(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            python = blocks("index", "python")[0]
            (project / "customer_service.py").write_text(python, encoding="utf-8")
            (project / "apizit_linking.yaml").write_text(blocks("index", "yaml")[0], encoding="utf-8")
            self.assertTrue(validate(project)["valid"])
            with preview(project) as port:
                request = Request(
                    f"http://127.0.0.1:{port}/customers",
                    data=b'{"name":"Ada","age":37}',
                    headers={"Content-Type": "application/json"}, method="POST",
                )
                with urlopen(request) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(json.load(response), {"name": "Ada", "age": 37})

    def test_ai_guide_tests_static_diagnostics_preview_and_errors(self):
        slug = "guides/ai-assisted-development"
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            python = blocks(slug, "python")
            (project / "pricing.py").write_text(python[0], encoding="utf-8")
            (project / "test_pricing.py").write_text(python[1], encoding="utf-8")
            subprocess.run([sys.executable, "-m", "unittest", "test_pricing"], cwd=project, check=True, capture_output=True)
            (project / "apizit_linking.yaml").write_text(blocks(slug, "yaml")[0], encoding="utf-8")
            sentinel = project / "imported.txt"
            import_side_effect = f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n"
            (project / "pricing.py").write_text(import_side_effect + python[0], encoding="utf-8")
            self.assertTrue(validate(project)["valid"])
            self.assertFalse(sentinel.exists(), "Validation must not import business code")
            with preview(project) as port:
                subprocess.run([sys.executable, "-c", python[2].replace(":8080", f":{port}")], check=True, capture_output=True)
                for quantity, status in [("many", 400), (0, 500)]:
                    request = Request(
                        f"http://127.0.0.1:{port}/quotes",
                        data=json.dumps({"unit_price": 12.5, "quantity": quantity}).encode(),
                        headers={"Content-Type": "application/json"}, method="POST",
                    )
                    with self.assertRaises(HTTPError) as error:
                        urlopen(request)
                    self.assertEqual(error.exception.code, status)
                    payload = error.exception.read().decode()
                    if status == 400:
                        self.assertIn("INVALID_PARAMETER", json.dumps(json.loads(payload)))
                    else:
                        self.assertNotIn("Price must", payload)
            self.assertTrue(sentinel.exists(), "Preview imports the project")

    def test_trace_guide_matches_real_module_and_request(self):
        slug = "guides/trace-route-to-python"
        project = ROOT / "examples/multi-module-api"
        python = blocks(slug, "python")
        self.assertEqual(python[0].strip(), (project / "catalog/service.py").read_text().strip())
        manifest = blocks(slug, "yaml")[0]
        self.assertIn("catalog.service:quote", manifest)
        self.assertTrue(validate(project)["valid"])
        with preview(project) as port:
            subprocess.run([sys.executable, "-c", python[1].replace(":8080", f":{port}")], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
