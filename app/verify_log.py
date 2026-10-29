import sys

from app.store import verify

ok, n, bad = verify(sys.argv[1] if len(sys.argv) > 1 else None)
print("OK" if ok else "TAMPERED", "records:", n, "" if ok else "first bad line: " + str(bad))