# Persistent API

This standalone V1 candidate example combines nested models, SQLite transactions,
owner permissions, bounded pagination and 201/204/400/401/403/404/409 responses. It needs no APIZIT account.
Use Python 3.10–3.14 and install the root pinned requirements in a virtual environment.

Set LINKING_DEMO_DATABASE to a disposable local SQLite path and choose distinct
LINKING_DEMO_WRITER_KEY and LINKING_DEMO_READER_KEY values in your environment.
Optionally set a distinct LINKING_DEMO_OTHER_KEY for the other-owner check.
From this directory run apizit-linking validate . --json and apizit-linking preview .
Static validation does not read credentials or open the database.

POST /tasks with the writer X-API-Key and JSON
{"title":"Read docs","details":{"label":"Work"}}. Expect 201 and Location.
GET the returned URL with the reader key. Stop and restart with the same database
path to verify persistence. Reader writes return 403; another owner sees 404;
duplicate titles return 409; invalid nested fields return 400; DELETE returns empty 204.
GET /tasks?limit=20&offset=0 lists only the current owner's tasks. Limit is 1–100;
offset is 0–1,000,000. Invalid pagination values return 400, and list outputs filter owner.

The business module is independent of Linking. bootstrap.py owns transport policy.
Use the public persistent guide for the full walkthrough. This local example does
not establish durable storage on an ephemeral managed runtime. Applications own
production credentials, identity verification, backups and database migrations.
