import json
import os
import sqlite3
import threading

DB_PATH = os.environ.get("TESSERA_DB", "tessera.db")

_lock = threading.Lock()
_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.execute("CREATE TABLE IF NOT EXISTS kv (name TEXT PRIMARY KEY, value TEXT NOT NULL)")
_conn.commit()


def save(**tables):
    with _lock:
        for name, data in tables.items():
            _conn.execute(
                "INSERT OR REPLACE INTO kv(name, value) VALUES(?, ?)",
                (name, json.dumps(data)),
            )
        _conn.commit()


def load(name):
    with _lock:
        row = _conn.execute("SELECT value FROM kv WHERE name=?", (name,)).fetchone()
    return json.loads(row[0]) if row else {}