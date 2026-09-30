import hmac
import os
import sqlite3
from contextlib import contextmanager
from apizit_linking.extensions import AccessDenied, Provider, RuntimeExtensions


class ApiKeyChallenge:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def challenged(message):
            if message["type"] == "http.response.start" and message["status"] == 401:
                headers = list(message.get("headers", []))
                headers.append((b"www-authenticate", b'ApiKey realm="linking-demo"'))
                message = {**message, "headers": headers}
            await send(message)
        await self.app(scope, receive, challenged)


def configure():
    writer = os.environ["LINKING_DEMO_WRITER_KEY"]
    reader = os.environ["LINKING_DEMO_READER_KEY"]
    other = os.environ.get("LINKING_DEMO_OTHER_KEY", "")
    path = os.environ["LINKING_DEMO_DATABASE"]
    if not writer or not reader or writer == reader or (other and other in {reader, writer}):
        raise ValueError("Demo keys must be non-empty and distinct")

    def authenticated(context):
        present, token = context.request.lookup("header", "X-API-Key")
        if not present or not isinstance(token, str):
            raise AccessDenied(401, "UNAUTHENTICATED", "Valid API key required")
        if hmac.compare_digest(token.encode(), writer.encode()):
            context.state.update(user="demo", write=True)
        elif hmac.compare_digest(token.encode(), reader.encode()):
            context.state.update(user="demo", write=False)
        elif other and hmac.compare_digest(token.encode(), other.encode()):
            context.state.update(user="other", write=True)
        else:
            raise AccessDenied(401, "UNAUTHENTICATED", "Valid API key required")

    def write(context):
        if not context.state.get("write"):
            raise AccessDenied()

    def user(context):
        return context.state["user"]

    @contextmanager
    def database(context):
        connection = sqlite3.connect(path, check_same_thread=False)
        try:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, owner TEXT NOT NULL, title TEXT NOT NULL, label TEXT NOT NULL, UNIQUE(owner,title))"
            )
            yield connection
        except BaseException:
            connection.rollback()
            raise
        else:
            connection.commit()
        finally:
            connection.close()

    return RuntimeExtensions(
        middlewares=((ApiKeyChallenge, {}),),
        providers={"database": Provider(database), "user": Provider(user)},
        guards={"authenticated": authenticated, "write": write},
        security_schemes={"authenticated": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
    )
