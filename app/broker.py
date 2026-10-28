import hashlib
import secrets
import time

from app.cloud import FakeCloud
from app.decision import Posture, decide
from app.manifest import load_manifest
from app.store import audit

cloud = FakeCloud()
tokens = {}     # token hash -> record
canaries = {}   # decoy access key -> record
runs = {}       # run id -> info shown on the dashboard

# Baseline credential lifetimes in seconds, used to compare exposure
BASELINES = {"static": 3600, "oidc": 900, "vault": 900}


def _h(t):
    return hashlib.sha256(t.encode()).hexdigest()


def _new_run(run_id, stage, environment, target, outcome, reasons, severity):
    run = {
        "run_id": run_id,
        "stage": stage,
        "environment": environment,
        "target": target,
        "outcome": outcome,
        "reasons": reasons,
        "severity": severity,
        "state": "denied" if outcome == "deny" else "active",
        "created_at": time.time(),
        "issued_at": None,
        "expires_at": None,
        "ended_at": None,
        "ttl": 0,
        "revoke_ms": None,
        "end_reason": None,
        "decoys": 0,
        "decoy_hits": 0,
    }
    runs[run_id] = run
    return run


def request_access(manifest_text, posture, remediation=False):
    run_id = secrets.token_hex(4)
    try:
        m = load_manifest(manifest_text)
    except (ValueError, TypeError) as e:
        errs = e.errors() if hasattr(e, "errors") else None
        why = errs[0]["msg"] if errs else str(e)
        run = _new_run(run_id, "unknown", "unknown", "", "deny", ["manifest rejected: " + why], "none")
        run["end_reason"] = "manifest_rejected"
        audit("manifest_rejected", run_id=run_id, reason=why)
        raise

    d = decide(m.environment, posture, remediation)
    audit("decision", run_id=run_id, outcome=d.outcome, reasons=d.reasons)
    run = _new_run(run_id, m.stage, m.environment, m.resources[0], d.outcome, d.reasons, posture.max_severity)
    if d.outcome == "deny":
        run["end_reason"] = "denied"
        return {"run_id": run_id, "outcome": "deny", "reasons": d.reasons}

    ttl = m.max_duration_seconds
    actions = m.actions
    if d.outcome == "restrict":
        ttl = min(ttl, 60)
        actions = [a for a in actions if not a.startswith("iam:")]

    now = time.time()
    token = secrets.token_urlsafe(24)
    tokens[_h(token)] = {
        "run_id": run_id,
        "state": "active",
        "expires": now + ttl,
        "actions": actions,
        "resources": m.resources,
    }
    run["issued_at"] = now
    run["expires_at"] = now + ttl
    run["ttl"] = ttl
    audit("token_issued", run_id=run_id, ttl=ttl, outcome=d.outcome)
    return {
        "run_id": run_id,
        "outcome": d.outcome,
        "reasons": d.reasons,
        "broker_token": token,
        "ttl": ttl,
    }


def _expire(rec, now):
    rec["state"] = "expired"
    cloud.revoke(rec["run_id"])
    run = runs.get(rec["run_id"])
    if run and run["state"] == "active":
        run["state"] = "expired"
        run["ended_at"] = now
        run["end_reason"] = "ttl_backstop"


def exchange(token, source="unknown"):
    rec = tokens.get(_h(token))
    if rec is None:
        audit("unknown_token", source=source)
        raise PermissionError("invalid token")

    now = time.time()
    if rec["state"] == "active" and rec["expires"] > now:
        creds = cloud.issue(rec["run_id"], rec["actions"], rec["resources"], int(rec["expires"] - now))
        audit("exchange", run_id=rec["run_id"], source=source)
        creds["_decoy"] = False
        return creds

    # revoked or expired token came back: give a decoy
    if rec["state"] == "active":
        _expire(rec, now)
    cid = secrets.token_hex(6)
    key = "AKIA" + secrets.token_hex(8).upper()
    canaries[key] = {"correlation_id": cid, "hits": 0, "run_id": rec["run_id"]}
    run = runs.get(rec["run_id"])
    if run:
        run["decoys"] += 1
    audit("DECOY_ISSUED", correlation_id=cid, run_id=rec["run_id"], source=source)
    return {"access_key": key, "secret": secrets.token_hex(16), "expires_in": 300, "_decoy": True}


def use(access_key, action, source="unknown"):
    c = canaries.get(access_key)
    if c:
        c["hits"] += 1
        run = runs.get(c["run_id"])
        if run:
            run["decoy_hits"] += 1
        audit("DECOY_HIT", correlation_id=c["correlation_id"], action=action, source=source)
        return False
    ok = cloud.is_valid(access_key)
    audit("credential_use", valid=ok, action=action)
    return ok


def complete(run_id, status="success"):
    t0 = time.perf_counter()
    now = time.time()
    n = 0
    for rec in list(tokens.values()):
        if rec["run_id"] == run_id and rec["state"] == "active":
            rec["state"] = "revoked"
            n += 1
    cloud.revoke(run_id)
    ms = round((time.perf_counter() - t0) * 1000, 3)
    run = runs.get(run_id)
    if run and run["state"] == "active":
        run["state"] = "revoked"
        run["ended_at"] = now
        run["revoke_ms"] = ms
        run["end_reason"] = status
    audit("revoked", run_id=run_id, status=status, tokens=n, ms=ms)
    return {"revoked": n}


def reap():
    now = time.time()
    n = 0
    for rec in list(tokens.values()):
        if rec["state"] == "active" and rec["expires"] <= now:
            _expire(rec, now)
            n += 1
    if n:
        audit("reaped", count=n)
    return n


def snapshot():
    now = time.time()
    allruns = list(runs.values())
    allruns.sort(key=lambda r: r["created_at"], reverse=True)

    shown = []
    for r in allruns[:24]:
        item = dict(r)
        item["remaining"] = max(0.0, r["expires_at"] - now) if r["state"] == "active" else 0.0
        shown.append(item)

    revoked = [r for r in allruns if r["state"] == "revoked" and r["issued_at"] and r["ended_at"]]
    after = {k: [] for k in BASELINES}
    for r in revoked:
        task = r["ended_at"] - r["issued_at"]
        for k, life in BASELINES.items():
            after[k].append(max(0.0, life - task))

    def avg(x):
        return sum(x) / len(x) if x else None

    ms = [r["revoke_ms"] for r in revoked if r["revoke_ms"] is not None]
    avg_ms = avg(ms)
    return {
        "kpis": {
            "active": sum(1 for r in allruns if r["state"] == "active"),
            "denied": sum(1 for r in allruns if r["state"] == "denied"),
            "decoy_hits": sum(r["decoy_hits"] for r in allruns),
            "total": len(allruns),
            "avg_revoke_ms": avg_ms,
        },
        "exposure": {
            "n": len(revoked),
            "static": avg(after["static"]),
            "oidc": avg(after["oidc"]),
            "vault": avg(after["vault"]),
            "tessera": (avg_ms / 1000) if avg_ms is not None else None,
        },
        "runs": shown,
    }