AI Incident Response Agent (Hindsight)

Minimal Python service that stores incidents, embeddings, runbooks, and finds similar past incidents to suggest root causes and runbooks.

Quick start

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\Activate.ps1 on Windows
pip install -r requirements.txt
```

2. Run the API:

```bash
uvicorn app.main:app --reload
```

Endpoints
- `POST /incidents` - add an incident
- `GET /incidents/{id}` - fetch incident
- `POST /search` - search similar incidents by text
- `POST /runbooks` - add runbook

Fill `.env` with any model/config settings if needed.

Training with a dataset

1. Put a JSONL file in `data/` where each line is a JSON object with `title`, `description`, `root_cause`, and `resolution` fields.
2. Run ingestion:

```bash
python scripts/ingest_dataset.py data/sample_incidents.jsonl
```

This will store incidents and build a FAISS vector index for fast similarity search.

Frontend

See `frontend/README.md` for instructions to run the minimal React UI.
