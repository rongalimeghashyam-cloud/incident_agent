from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.types import JSON


class Incident(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    embeddings: Optional[List[float]] = Field(sa_column=Column(JSON), default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False


class Runbook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    content: str
    tags: Optional[List[str]] = Field(sa_column=Column(JSON), default=None)
