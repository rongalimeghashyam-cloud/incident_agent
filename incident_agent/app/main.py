from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.db import init_db, get_session
from app.agent import ingest_incident, add_runbook, find_similar_incidents
from app.models import Incident, Runbook

app = FastAPI(title="Hindsight Incident Agent")


class IncidentIn(BaseModel):
    title: str
    description: str
    root_cause: Optional[str] = None
    resolution: Optional[str] = None


class SearchIn(BaseModel):
    text: str
    top_k: Optional[int] = 5


class RunbookIn(BaseModel):
    name: str
    content: str
    tags: Optional[List[str]] = None


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/incidents")
def create_incident(payload: IncidentIn):
    inc = ingest_incident(payload.title, payload.description, payload.root_cause, payload.resolution)
    return {"id": inc.id}


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    with get_session() as s:
        inc = s.get(Incident, incident_id)
        if not inc:
            raise HTTPException(status_code=404, detail="Not found")
        return inc


@app.post("/search")
def search_similar(payload: SearchIn):
    results = find_similar_incidents(payload.text, top_k=payload.top_k)
    return {"results": results}


@app.post("/runbooks")
def create_runbook(payload: RunbookIn):
    rb = add_runbook(payload.name, payload.content, payload.tags)
    return {"id": rb.id}
