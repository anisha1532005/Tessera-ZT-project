import json

from app import store


def test_chain_detects_tampering(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "AUDIT_FILE", tmp_path / "a.log")
    monkeypatch.setattr(store, "_state", {"path": None, "last": store.GENESIS})

    store.audit("one", x=1)
    store.audit("two", x=2)
    store.audit("three", x=3)
    ok, n, bad = store.verify()
    assert ok and n == 3

    lines = store.AUDIT_FILE.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[1])
    rec["x"] = 999
    lines[1] = json.dumps(rec)
    store.AUDIT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, n, bad = store.verify()
    assert not ok and bad == 2