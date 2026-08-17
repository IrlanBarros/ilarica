#!/bin/sh
set -e

echo "[backend] waiting for database ${DB_HOST:-db}:${DB_PORT:-5432}"
python - <<'PY'
import os
import socket
import sys
import time

host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))

for attempt in range(30):
	try:
		with socket.create_connection((host, port), timeout=2):
			print(f"[backend] database reachable at {host}:{port}")
			break
	except OSError:
		print(f"[backend] database not ready yet ({attempt + 1}/30)")
		time.sleep(2)
else:
	print(f"[backend] database did not become ready at {host}:{port}", file=sys.stderr)
	sys.exit(1)
PY

echo "[backend] applying database migrations"
alembic upgrade head

echo "[backend] starting application"
exec "$@"