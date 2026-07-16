
from __future__ import annotations
import io, json, zipfile, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml

from kap_studio.domain.models import KapProject
from .manifest import WorkspaceManifest

class WorkspaceError(RuntimeError):
    pass

class WorkspaceEngine:
    """
    Формат .kap — ZIP-контейнер.

    manifest.yaml
    project.json
    history/revision-XXXX.json
    review/.keep
    assets/.keep
    exports/.keep
    """

    MANIFEST = "manifest.yaml"
    PROJECT = "project.json"

    def create(self, project: KapProject, path: str | Path) -> Path:
        target = self._ensure_extension(Path(path))
        manifest = WorkspaceManifest(
            project_id=project.product.id,
            project_name=f"{project.product.name} {project.product.version}",
        )
        self._write_container(target, manifest, project, history_payload=None)
        return target

    def open(self, path: str | Path) -> tuple[WorkspaceManifest, KapProject]:
        source = Path(path)
        if not source.exists():
            raise WorkspaceError(f"Файл проекта не найден: {source}")

        try:
            with zipfile.ZipFile(source, "r") as zf:
                names = set(zf.namelist())
                if self.MANIFEST not in names or self.PROJECT not in names:
                    raise WorkspaceError("Некорректный .kap: отсутствует manifest.yaml или project.json.")

                manifest = WorkspaceManifest.model_validate(
                    yaml.safe_load(zf.read(self.MANIFEST).decode("utf-8"))
                )
                project = KapProject.model_validate_json(
                    zf.read(self.PROJECT).decode("utf-8")
                )
                return manifest, project
        except zipfile.BadZipFile as exc:
            raise WorkspaceError("Файл .kap повреждён или не является ZIP-контейнером.") from exc

    def save(self, project: KapProject, path: str | Path) -> Path:
        target = self._ensure_extension(Path(path))
        if target.exists():
            old_manifest, old_project = self.open(target)
            history_payload = old_project.model_dump(mode="json")
            manifest = old_manifest.model_copy(update={
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "revision": old_manifest.revision + 1,
                "project_name": f"{project.product.name} {project.product.version}",
            })
        else:
            history_payload = None
            manifest = WorkspaceManifest(
                project_id=project.product.id,
                project_name=f"{project.product.name} {project.product.version}",
            )

        self._write_container(target, manifest, project, history_payload)
        return target

    def export_json(self, project: KapProject, path: str | Path) -> Path:
        target = Path(path)
        target.write_text(project.model_dump_json(indent=2), encoding="utf-8")
        return target

    def checksum(self, path: str | Path) -> str:
        h = hashlib.sha256()
        with Path(path).open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def _write_container(
        self,
        target: Path,
        manifest: WorkspaceManifest,
        project: KapProject,
        history_payload: dict[str, Any] | None,
    ) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")

        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                self.MANIFEST,
                yaml.safe_dump(
                    manifest.model_dump(mode="json"),
                    allow_unicode=True,
                    sort_keys=False,
                ),
            )
            zf.writestr(self.PROJECT, project.model_dump_json(indent=2))
            zf.writestr("assets/.keep", "")
            zf.writestr("exports/.keep", "")
            zf.writestr("review/.keep", "")
            if history_payload is not None:
                hist_name = f"history/revision-{manifest.revision - 1:04d}.json"
                zf.writestr(hist_name, json.dumps(history_payload, ensure_ascii=False, indent=2))
            else:
                zf.writestr("history/.keep", "")

        tmp.replace(target)

    @staticmethod
    def _ensure_extension(path: Path) -> Path:
        return path if path.suffix.lower() == ".kap" else path.with_suffix(".kap")
