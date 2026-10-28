import json
import subprocess

from app.decision import Posture

ORDER = ["none", "medium", "high", "critical"]


def scan_image(image, kev_ids=None):
    kev_ids = kev_ids or set()
    try:
        out = subprocess.run(
            ["trivy", "image", "--quiet", "--format", "json", image],
            capture_output=True, text=True, timeout=120,
        )
        data = json.loads(out.stdout)
    except Exception:
        return Posture(status="failed")

    worst = "none"
    exploited = False
    for res in data.get("Results", []):
        for v in res.get("Vulnerabilities") or []:
            sev = v.get("Severity", "").lower()
            if sev in ORDER and ORDER.index(sev) > ORDER.index(worst):
                worst = sev
            if v.get("VulnerabilityID") in kev_ids:
                exploited = True
    return Posture(status="ok", max_severity=worst, known_exploited=exploited)