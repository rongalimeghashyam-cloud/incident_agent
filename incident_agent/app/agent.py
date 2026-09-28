from typing import List, Dict, Any
from app.db import get_session
from app.models import Incident, Runbook
from app.embeddings import get_provider
from app.search import find_most_similar
from app.vector_store import get_store


def ingest_incident(title: str, description: str, root_cause: str | None = None, resolution: str | None = None) -> Incident:
    provider = get_provider()
    emb = provider.embed([title + "\n" + description])[0]
    incident = Incident(title=title, description=description, root_cause=root_cause, resolution=resolution, embeddings=emb)
    with get_session() as s:
        s.add(incident)
        s.commit()
        s.refresh(incident)
    # add to vector index
    try:
        store = get_store(len(emb))
        store.add(incident.id, emb)
        store.save()
    except Exception:
        # fail silently if vector store not available
        pass
    return incident


def add_runbook(name: str, content: str, tags: List[str] | None = None) -> Runbook:
    rb = Runbook(name=name, content=content, tags=tags)
    with get_session() as s:
        s.add(rb)
        s.commit()
        s.refresh(rb)
    return rb


def find_similar_incidents(text: str, top_k: int = 5):
    provider = get_provider()
    qv = provider.embed([text])[0]
    # Prefer FAISS store for performance
    try:
        store = get_store(len(qv))
        return store.search(qv, top_k=top_k)
    except Exception:
        with get_session() as s:
            incidents = s.exec(Incident.select()).all()
            candidates = [(inc.id, inc.embeddings) for inc in incidents]
        results = find_most_similar(qv, candidates, top_k=top_k)
        return results
