#!/bin/sh
set -eu

python - <<'PY'
import subprocess
from sqlalchemy import inspect

from app.db import engine

inspector = inspect(engine)
tables = set(inspector.get_table_names())

if "organizations" in tables and "alembic_version" not in tables:
    print("Existing pre-Alembic schema detected; stamping baseline 0001_initial.")
    subprocess.run(["alembic", "stamp", "0001_initial"], check=True)
PY

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
