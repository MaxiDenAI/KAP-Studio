
from __future__ import annotations
import json
from pathlib import Path

class SettingsRepository:
    def __init__(self, app_dir: Path):
        self.path = app_dir / "settings.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_recent(self) -> list[str]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return [x for x in data.get("recent_projects", []) if Path(x).exists()]
        except Exception:
            return []

    def save_recent(self, items: list[str]) -> None:
        unique = []
        for item in items:
            if item not in unique:
                unique.append(item)
        self.path.write_text(json.dumps(
            {"recent_projects": unique[:10]}, ensure_ascii=False, indent=2
        ), encoding="utf-8")
