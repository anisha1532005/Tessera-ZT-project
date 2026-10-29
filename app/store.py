import hashlib
import json
import threading
import time
from pathlib import Path

AUDIT_FILE = Path("audit.log")
GENESIS = "0" * 64
_lock = threading.Lock()
_state = {"path": None, "last": GENESIS}


def _digest(rec):
    return hashlib.sha256(json.dumps(rec, sort_keys=True).encode("utf-8")).hexdigest()


def _last_hash():
    last = GENESIS
    if AUDIT_FILE.exists():
        with AUDIT_FILE.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last = json.loads(line).get("hash", GENESIS)
    return last


def audit(event, **data):
    with _lock:
        if _state["path"] != AUDIT_FILE:
            _state["last"] = _last_hash()
            _state["path"] = AUDIT_FILE
        rec = {"ts": time.time(), "event": event, **data, "prev": _state["last"]}
        rec["hash"] = _digest(rec)
        with AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        _state["last"] = rec["hash"]
    return rec


def read_audit(limit=200):
    if not AUDIT_FILE.exists():
        return []
    lines = AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    out = []
    for x in lines[-limit:]:
        rec = json.loads(x)
        rec.pop("prev", None)
        rec["hash"] = rec.get("hash", "")[:10]
        out.append(rec)
    return out


def verify(path=None):
    path = Path(path) if path else AUDIT_FILE
    if not path.exists():
        return True, 0, None
    prev = GENESIS
    n = 0
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            h = rec.pop("hash", None)
            if rec.get("prev") != prev or h != _digest(rec):
                return False, n, i
            prev = h
            n += 1
    return True, n, None