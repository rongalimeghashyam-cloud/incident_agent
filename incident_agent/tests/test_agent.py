import os
import tempfile
import json
from app.db import init_db, get_session
from app.agent import ingest_incident, find_similar_incidents


def test_ingest_and_search(tmp_path):
    # Use a temporary sqlite DB for tests
    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path / 'test.db'}"
    init_db()
    # ingest sample incidents
    a = ingest_incident("Test A", "Service A crashed due to timeout", "timeout", "increase timeout")
    b = ingest_incident("Test B", "Database connection exhausted", "connection_pool", "increase pool")
    # search similar to A
    results = find_similar_incidents("Service A timeout during requests", top_k=2)
    assert isinstance(results, list)
    # ensure at least one result id is present
    assert len(results) >= 1
