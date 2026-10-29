import csv
import statistics
import time
from pathlib import Path

from app import broker, store
from app.decision import Posture, decide

Path("experiments").mkdir(exist_ok=True)
store.AUDIT_FILE = Path("experiments/audit_exp.log")

N = 100
TASK_SECONDS = 120  # assumed task length, used only for the baseline numbers


def manifest(secs=300, env="prod"):
    return (
        "stage: deploy\n"
        "environment: " + env + "\n"
        "actions: [s3:PutObject]\n"
        'resources: ["arn:aws:s3:::bucket-x/*"]\n'
        "max_duration_seconds: " + str(secs) + "\n"
        "intent: release\n"
    )


def pct(data, p):
    s = sorted(data)
    return s[max(0, min(len(s) - 1, int(round(p / 100 * (len(s) - 1)))))]


def exposure_overhead_decoy():
    overhead, exposure, decoy = [], [], []
    for _ in range(N):
        t0 = time.perf_counter()
        r = broker.request_access(manifest(), Posture())
        creds = broker.exchange(r["broker_token"], source="ci")
        overhead.append((time.perf_counter() - t0) * 1000)

        t1 = time.perf_counter()
        broker.complete(r["run_id"])
        while broker.cloud.is_valid(creds["access_key"]):
            time.sleep(0.001)
        exposure.append(time.perf_counter() - t1)

        t2 = time.perf_counter()
        d = broker.exchange(r["broker_token"], source="9.9.9.9")
        broker.use(d["access_key"], "iam:ListUsers", source="9.9.9.9")
        decoy.append((time.perf_counter() - t2) * 1000)
    return overhead, exposure, decoy


def accuracy():
    cases = [
        ("prod", Posture(), False, "allow"),
        ("dev", Posture(), False, "allow"),
        ("prod", Posture(max_severity="high"), False, "restrict"),
        ("staging", Posture(max_severity="high"), False, "restrict"),
        ("prod", Posture(max_severity="critical"), False, "deny"),
        ("dev", Posture(known_exploited=True), False, "deny"),
        ("prod", Posture(status="failed"), False, "deny"),
        ("prod", Posture(status="stale"), False, "deny"),
        ("dev", Posture(status="stale"), False, "restrict"),
        ("prod", Posture(max_severity="critical", known_exploited=True), True, "restrict"),
    ]
    tp = fp = fn = tn = 0
    wrong = []
    for env, p, rem, expected in cases:
        got = decide(env, p, rem).outcome
        if got != expected:
            wrong.append((env, p.model_dump(), rem, expected, got))
        if expected == "deny" and got == "deny":
            tp += 1
        elif expected != "deny" and got == "deny":
            fp += 1
        elif expected == "deny" and got != "deny":
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    return precision, recall, fp, wrong, len(cases)


def orphan_test():
    r = broker.request_access(manifest(secs=1, env="dev"), Posture())
    c = broker.exchange(r["broker_token"], source="ci")
    time.sleep(1.3)
    n = broker.reap()
    return n == 1 and not broker.cloud.is_valid(c["access_key"])


def retry_no_false_decoy():
    r = broker.request_access(manifest(), Posture())
    broker.exchange(r["broker_token"], source="runner-1")
    second = broker.exchange(r["broker_token"], source="runner-2")
    ok = second["_decoy"] is False
    broker.complete(r["run_id"])
    return ok


def main():
    overhead, exposure, decoy = exposure_overhead_decoy()
    precision, recall, fp, wrong, ncases = accuracy()
    orphan_ok = orphan_test()
    retry_ok = retry_no_false_decoy()

    base_static = 3600 - TASK_SECONDS
    base_oidc = 900 - TASK_SECONDS
    base_vault = 900 - TASK_SECONDS

    rows = [
        ("runs", N),
        ("assumed_task_seconds", TASK_SECONDS),
        ("B0_static_exposure_s", base_static),
        ("B1_oidc_exposure_s", base_oidc),
        ("B2_vault_exposure_s", base_vault),
        ("tessera_exposure_ms_p50", round(statistics.median(exposure) * 1000, 3)),
        ("tessera_exposure_ms_p95", round(pct(exposure, 95) * 1000, 3)),
        ("overhead_ms_p50", round(statistics.median(overhead), 3)),
        ("overhead_ms_p95", round(pct(overhead, 95), 3)),
        ("decoy_detect_ms_p50", round(statistics.median(decoy), 3)),
        ("decoy_detect_ms_p95", round(pct(decoy, 95), 3)),
        ("decision_cases", ncases),
        ("deny_precision", round(precision, 3)),
        ("deny_recall", round(recall, 3)),
        ("false_denies", fp),
        ("S4_orphan_reaped", orphan_ok),
        ("S5_retry_no_false_decoy", retry_ok),
        ("environment", "SIMULATED cloud, not real AWS"),
    ]
    for k, v in rows:
        print(k.ljust(28), v)
    for w in wrong:
        print("WRONG DECISION:", w)

    with open("experiments/results.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("metric", "value")] + rows)
    print("saved experiments/results.csv")


if __name__ == "__main__":
    main()