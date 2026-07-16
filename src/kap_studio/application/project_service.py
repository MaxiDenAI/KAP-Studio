
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from kap_studio.domain.models import KapProject
from kap_studio.domain.review import ReviewReport, review_project
from kap_studio.workspace.engine import WorkspaceEngine
from kap_studio.workspace.manifest import WorkspaceManifest

@dataclass
class ProjectService:
    workspace: WorkspaceEngine

    def create(self, project: KapProject, path: str | Path) -> Path:
        return self.workspace.create(project, path)

    def open(self, path: str | Path) -> tuple[WorkspaceManifest, KapProject]:
        return self.workspace.open(path)

    def save(self, project: KapProject, path: str | Path) -> Path:
        return self.workspace.save(project, path)

    def review(self, project: KapProject) -> ReviewReport:
        return review_project(project)
