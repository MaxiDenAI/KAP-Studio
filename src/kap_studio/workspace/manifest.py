
from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class WorkspaceManifest(BaseModel):
    format: str = "KAP_WORKSPACE"
    format_version: str = "1.0"
    app_version: str = "0.3.0"
    project_id: str
    project_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revision: int = 1
