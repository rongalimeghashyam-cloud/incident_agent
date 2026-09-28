"""Ingest a JSONL dataset of incidents into the DB and vector store.

Expected format per line: {"title": "...", "description": "...", "root_cause": "...", "resolution": "..."}
"""
import json
import argparse
from app.agent import ingest_incident


def main(path: str):
    count = 0
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            title = obj.get("title") or obj.get("summary") or "Untitled"
            desc = obj.get("description") or obj.get("body") or ""
            rc = obj.get("root_cause")
            res = obj.get("resolution")
            ingest_incident(title, desc, rc, res)
            count += 1
    print(f"Ingested {count} incidents from {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path", help="Path to dataset JSONL file")
    args = p.parse_args()
    main(args.path)
