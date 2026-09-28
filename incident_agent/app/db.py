import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./incidents.db")

engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    from app.models import Incident, Runbook

    SQLModel.metadata.create_all(engine)
    # ensure vector index is initialized and rebuilt if necessary
    try:
        from app.embeddings import get_provider
        from app.vector_store import get_store

        provider = get_provider()
        dim = len(provider.embed(["test"])[0])
        store = get_store(dim)
        # if index empty, rebuild from DB
        if store.index.ntotal == 0:
            with Session(engine) as s:
                incidents = s.exec(Incident.select()).all()
                for inc in incidents:
                    if inc.embeddings:
                        store.add(inc.id, inc.embeddings)
            store.save()
    except Exception:
        pass


def get_session():
    return Session(engine)
