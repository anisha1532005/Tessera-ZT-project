import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app import broker, demo
from app.dashboard import PAGE
from app.decision import Posture
from app.store import read_audit


def _reaper_loop():
    while True:
        try:
            broker.reap()
        except Exception:
            pass
        time.sleep(1)


@asynccontextmanager
async def lifespan(_app):
    threading.Thread(target=_reaper_loop, daemon=True).start()
    yield


app = FastAPI(title="Tessera", lifespan=lifespan)


class AccessRequest(BaseModel):
    manifest: str
    posture: Posture = Posture()
    remediation: bool = False


class ExchangeRequest(BaseModel):
    token: str
    source: str = "unknown"


class UseRequest(BaseModel):
    access_key: str
    action: str
    source: str = "unknown"


class CompletionRequest(BaseModel):
    run_id: str
    status: str = "success"


class ScenarioRequest(BaseModel):
    name: str


class ReplayRequest(BaseModel):
    run_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/access-requests")
def access(req: AccessRequest):
    try:
        return broker.request_access(req.manifest, req.posture, req.remediation)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/v1/exchange")
def exchange(req: ExchangeRequest):
    try:
        creds = broker.exchange(req.token, req.source)
    except PermissionError:
        raise HTTPException(status_code=401, detail="invalid token")
    creds.pop("_decoy", None)  # attacker must not see which one is a decoy
    return creds


@app.post("/v1/use")
def use(req: UseRequest):
    if not broker.use(req.access_key, req.action, req.source):
        raise HTTPException(status_code=403, detail="AccessDenied")
    return {"result": "ok"}


@app.post("/v1/completions")
def completions(req: CompletionRequest):
    return broker.complete(req.run_id, req.status)


@app.post("/v1/reap")
def reap():
    return {"reaped": broker.reap()}


@app.get("/v1/audit")
def audit_log():
    return read_audit()


@app.get("/v1/state")
def state():
    s = broker.snapshot()
    for r in s["runs"]:
        r["replayable"] = r["run_id"] in demo.held and r["state"] in ("revoked", "expired")
    s["audit"] = read_audit(60)
    return s


@app.post("/v1/demo/scenario")
def demo_scenario(req: ScenarioRequest):
    try:
        demo.launch(req.name)
    except KeyError:
        raise HTTPException(status_code=404, detail="unknown scenario")
    return {"started": req.name}


@app.post("/v1/demo/replay")
def demo_replay(req: ReplayRequest):
    try:
        return demo.replay(req.run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="no token held for this run")
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return PAGE