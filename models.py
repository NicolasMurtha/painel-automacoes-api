from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional


class Bot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    desc: str

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"

class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bot_id: int = Field(foreign_key="bot.id", index=True)

    status: JobStatus = Field(default=JobStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    error_message: str | None = None

class JobStatusUpdate(BaseModel):
    status: JobStatus
    error_message: Optional[str] = None