
from __future__ import annotations
import json, sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from kap_studio.application.project_service import ProjectService
from kap_studio.domain.models import KapProject
from kap_studio.ui.main_window import MainWindow
from kap_studio.workspace.engine import WorkspaceEngine

def main():
    app = QApplication(sys.argv)
    base = Path(__file__).resolve().parents[2]
    seed = KapProject.model_validate_json(
        (base / "data" / "photoshop_2023.kap.json").read_text(encoding="utf-8")
    )
    service = ProjectService(WorkspaceEngine())
    window = MainWindow(service, seed)
    window.show()
    raise SystemExit(app.exec())

if __name__ == "__main__":
    main()
