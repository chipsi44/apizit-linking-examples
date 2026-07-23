from __future__ import annotations

import ast
import unittest
from pathlib import Path

import httpx

from apizit_linking import compile_linking_file
from apizit_linking.fastapi import create_app

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

PROJECTS = {
    "hello-world": REPOSITORY_ROOT,
    "path-and-query-parameters": REPOSITORY_ROOT
    / "examples"
    / "path-and-query-parameters",
    "json-body": REPOSITORY_ROOT / "examples" / "json-body",
    "error-handling": REPOSITORY_ROOT / "examples" / "error-handling",
    "multi-module-api": REPOSITORY_ROOT / "examples" / "multi-module-api",
    "task-api": REPOSITORY_ROOT / "examples" / "task-api",
}

EXPECTED_ROUTES = {
    "hello-world": {("GET", "/hello")},
    "path-and-query-parameters": {("GET", "/users/{user_id}/greeting")},
    "json-body": {("POST", "/products")},
    "error-handling": {("GET", "/divide")},
    "multi-module-api": {("GET", "/products/{product_id}/quote")},
    "task-api": {
        ("GET", "/tasks"),
        ("POST", "/tasks"),
        ("GET", "/tasks/{task_id}"),
        ("PATCH", "/tasks/{task_id}"),
        ("DELETE", "/tasks/{task_id}"),
    },
}

BUSINESS_FILES = (
    REPOSITORY_ROOT / "hello.py",
    REPOSITORY_ROOT / "examples" / "path-and-query-parameters" / "greetings.py",
    REPOSITORY_ROOT / "examples" / "json-body" / "products.py",
    REPOSITORY_ROOT / "examples" / "error-handling" / "calculator.py",
    REPOSITORY_ROOT / "examples" / "multi-module-api" / "catalog" / "__init__.py",
    REPOSITORY_ROOT / "examples" / "multi-module-api" / "catalog" / "pricing.py",
    REPOSITORY_ROOT / "examples" / "multi-module-api" / "catalog" / "service.py",
    REPOSITORY_ROOT / "examples" / "task-api" / "tasks.py",
)


class ExampleProjectContractTests(unittest.TestCase):
    def test_every_project_is_independent_documented_and_valid(self) -> None:
        self.assertEqual(set(PROJECTS), set(EXPECTED_ROUTES))

        for name, project_root in PROJECTS.items():
            with self.subTest(example=name):
                readme = (
                    REPOSITORY_ROOT / "README.md"
                    if project_root == REPOSITORY_ROOT
                    else project_root / "README.md"
                )
                self.assertTrue(readme.is_file())
                manifest = project_root / "apizit_linking.yaml"
                result = compile_linking_file(manifest, project_root)
                self.assertTrue(
                    result.is_valid,
                    [diagnostic.to_dict() for diagnostic in result.diagnostics],
                )
                actual_routes = {
                    (route.definition.method, route.definition.path)
                    for route in result.routes
                }
                self.assertEqual(actual_routes, EXPECTED_ROUTES[name])

    def test_business_code_has_no_web_or_linking_imports(self) -> None:
        forbidden_roots = {"apizit_linking", "fastapi", "flask"}
        for source_file in BUSINESS_FILES:
            with self.subTest(source=str(source_file.relative_to(REPOSITORY_ROOT))):
                tree = ast.parse(source_file.read_text(encoding="utf-8"))
                imported_roots: set[str] = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported_roots.update(
                            alias.name.partition(".")[0] for alias in node.names
                        )
                    elif (
                        isinstance(node, ast.ImportFrom)
                        and node.level == 0
                        and node.module
                    ):
                        imported_roots.add(node.module.partition(".")[0])
                self.assertFalse(imported_roots & forbidden_roots)


class ExampleProjectHttpTests(unittest.IsolatedAsyncioTestCase):
    async def test_hello_world(self) -> None:
        async with self._client("hello-world") as client:
            response = await client.get("/hello")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello from APIZIT Linking!"})

    async def test_path_and_query_conversions_and_default(self) -> None:
        async with self._client("path-and-query-parameters") as client:
            default_response = await client.get("/users/42/greeting")
            verbose_response = await client.get(
                "/users/42/greeting",
                params={"verbose": "true"},
            )

        self.assertEqual(default_response.status_code, 200)
        self.assertEqual(
            default_response.json(),
            {"user_id": 42, "message": "Hello, user 42!"},
        )
        self.assertEqual(verbose_response.status_code, 200)
        self.assertEqual(
            verbose_response.json(),
            {
                "user_id": 42,
                "message": "Hello, user 42!",
                "details": "The verbose query parameter is enabled.",
            },
        )

    async def test_json_body_defaults_and_validation(self) -> None:
        async with self._client("json-body") as client:
            response = await client.post(
                "/products",
                json={
                    "name": "Notebook",
                    "price": 12.5,
                    "in_stock": True,
                    "tags": ["paper", "office"],
                },
            )
            default_response = await client.post(
                "/products",
                json={"name": "Pen", "price": "2.75"},
            )
            invalid_response = await client.post(
                "/products",
                json={"name": "Mystery", "price": "free"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "name": "Notebook",
                "price": 12.5,
                "in_stock": True,
                "tags": ["paper", "office"],
            },
        )
        self.assertEqual(
            default_response.json(),
            {"name": "Pen", "price": 2.75, "in_stock": True, "tags": []},
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(invalid_response.json()["error"]["code"], "INVALID_PARAMETER")

    async def test_request_errors_and_generic_business_failure(self) -> None:
        async with self._client("error-handling", raise_app_exceptions=False) as client:
            success = await client.get(
                "/divide",
                params={"dividend": "10", "divisor": "4"},
            )
            missing = await client.get("/divide", params={"dividend": "10"})
            invalid = await client.get(
                "/divide",
                params={"dividend": "10", "divisor": "many"},
            )
            business_failure = await client.get(
                "/divide",
                params={"dividend": "10", "divisor": "0"},
            )

        self.assertEqual(
            success.json(),
            {"dividend": 10.0, "divisor": 4.0, "result": 2.5},
        )
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(
            missing.json(),
            {
                "error": {
                    "code": "PARAMETER_NOT_FOUND_IN_SOURCE",
                    "message": (
                        "Required field 'divisor' was not found in request source 'query'."
                    ),
                    "parameter": "divisor",
                    "external_name": "divisor",
                    "source": "query",
                }
            },
        )
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.json()["error"]["code"], "INVALID_PARAMETER")
        self.assertEqual(business_failure.status_code, 500)
        self.assertNotIn("divisor must not be zero", business_failure.text)

    async def test_multi_module_package(self) -> None:
        async with self._client("multi-module-api") as client:
            response = await client.get(
                "/products/4/quote",
                params={"discount": "25"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "product_id": 4,
                "base_price": 16.0,
                "discount": 25.0,
                "final_price": 12.0,
            },
        )

    async def test_task_crud_lifecycle(self) -> None:
        async with self._client("task-api") as client:
            empty = await client.get("/tasks")
            created = await client.post(
                "/tasks",
                json={
                    "title": "Write examples",
                    "description": "Cover the V1 features",
                },
            )
            task_id = created.json()["id"]
            fetched = await client.get(f"/tasks/{task_id}")
            updated = await client.patch(
                f"/tasks/{task_id}",
                json={"completed": True},
            )
            completed = await client.get("/tasks", params={"completed": "true"})
            deleted = await client.delete(f"/tasks/{task_id}")
            missing = await client.get(f"/tasks/{task_id}")

        self.assertEqual(empty.json(), [])
        self.assertEqual(created.status_code, 200)
        self.assertEqual(fetched.json(), created.json())
        self.assertTrue(updated.json()["completed"])
        self.assertEqual(completed.json(), [updated.json()])
        self.assertEqual(
            deleted.json(),
            {"deleted": True, "task": updated.json()},
        )
        self.assertEqual(missing.status_code, 200)
        self.assertEqual(missing.json()["error"]["code"], "TASK_NOT_FOUND")

    def _client(
        self,
        example: str,
        *,
        raise_app_exceptions: bool = True,
    ) -> httpx.AsyncClient:
        app = create_app(PROJECTS[example])
        transport = httpx.ASGITransport(
            app=app,
            raise_app_exceptions=raise_app_exceptions,
        )
        return httpx.AsyncClient(transport=transport, base_url="http://example.test")


if __name__ == "__main__":
    unittest.main()
