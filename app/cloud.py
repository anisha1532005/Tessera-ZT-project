import secrets
import time


class FakeCloud:
    """Pretend AWS. Later we swap this for a real boto3 class with the same methods."""

    def __init__(self):
        self.sessions = {}

    def issue(self, run_id, actions, resources, ttl):
        key = "ASIA" + secrets.token_hex(8).upper()
        self.sessions[key] = {
            "run_id": run_id,
            "actions": actions,
            "resources": resources,
            "expires": time.time() + ttl,
            "revoked": False,
        }
        return {"access_key": key, "secret": secrets.token_hex(16), "expires_in": ttl}

    def revoke(self, run_id):
        n = 0
        for s in self.sessions.values():
            if s["run_id"] == run_id and not s["revoked"]:
                s["revoked"] = True
                n += 1
        return n

    def is_valid(self, key):
        s = self.sessions.get(key)
        return bool(s) and not s["revoked"] and s["expires"] > time.time()