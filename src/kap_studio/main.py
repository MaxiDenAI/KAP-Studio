
from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from kap_studio.application.project_service import ProjectService
from kap_studio.infrastructure.settings_repository import SettingsRepository
from kap_studio.ui.welcome_window import WelcomeWindow
from kap_studio.workspace.engine import WorkspaceEngine

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("KAP Studio")

    app_dir = Path.home() / "KAP Studio"
    service = ProjectService(WorkspaceEngine())
    settings = SettingsRepository(app_dir)

    window = WelcomeWindow(service, settings)
    window.show()
    raise SystemExit(app.exec())

if __name__ == "__main__":
    main()
