import threading
import time

from app import broker
from app.decision import Posture

held = {}   # run id -> broker token (lab only, so the dashboard can replay it)


def _manifest(stage="deploy", env="prod", actions="[s3:PutObject]", secs=300):
    lines = [
        "stage: " + stage,
        "environment: " + env,
        "actions: " + actions,
        'resources: ["arn:aws:s3:::bucket-x/*"]',
        "max_duration_seconds: " + str(secs),
        "intent: release",
    ]
    return "\n".join(lines) + "\n"


def _issue(manifest, posture, remediation=False):
    r = broker.request_access(manifest, posture, remediation)
    if "broker_token" in r:
        held[r["run_id"]] = r["broker_token"]
        broker.exchange(r["broker_token"], source="jenkins")
    return r


def replay(run_id, source="203.0.113.7"):
    token = held.get(run_id)
    if token is None:
        raise KeyError(run_id)
    run = broker.runs.get(run_id)
    if not run or run["state"] not in ("revoked", "expired"):
        raise ValueError("credential is still active, revoke it first")
    creds = broker.exchange(token, source=source)
    broker.use(creds["access_key"], "iam:ListUsers", source=source)
    return {"replayed": True}


def manual():
    _issue(_manifest("deploy", "dev", secs=120), Posture())


def allow_revoke():
    r = _issue(_manifest("deploy", "prod", secs=300), Posture())
    time.sleep(8)
    broker.complete(r["run_id"], "success")


def high_restrict():
    r = _issue(_manifest("deploy", "staging", secs=300), Posture(max_severity="high"))
    time.sleep(6)
    broker.complete(r["run_id"], "success")


def critical_deny():
    broker.request_access(_manifest("deploy", "prod"), Posture(max_severity="critical", known_exploited=True))


def fix_deploy():
    r = _issue(_manifest("hotfix", "prod", secs=300),
               Posture(max_severity="critical", known_exploited=True), remediation=True)
    time.sleep(5)
    broker.complete(r["run_id"], "success")


def replay_decoy():
    r = _issue(_manifest("deploy", "prod", secs=300), Posture())
    time.sleep(4)
    broker.complete(r["run_id"], "success")
    time.sleep(2)
    replay(r["run_id"])


def orphan_reaper():
    _issue(_manifest("deploy", "dev", secs=20), Posture())


def scan_fail_prod():
    broker.request_access(_manifest("deploy", "prod"), Posture(status="failed"))


def wildcard_deny():
    try:
        broker.request_access(_manifest("deploy", "prod", actions="[s3:*]"), Posture())
    except (ValueError, TypeError):
        pass


SCENARIOS = {
    "manual": manual,
    "allow_revoke": allow_revoke,
    "high_restrict": high_restrict,
    "critical_deny": critical_deny,
    "fix_deploy": fix_deploy,
    "replay_decoy": replay_decoy,
    "orphan_reaper": orphan_reaper,
    "scan_fail_prod": scan_fail_prod,
    "wildcard_deny": wildcard_deny,
}


def launch(name):
    fn = SCENARIOS[name]
    threading.Thread(target=fn, daemon=True).start()