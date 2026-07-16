
from __future__ import annotations
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QFrame
)

from kap_studio.application.project_service import ProjectService
from kap_studio.infrastructure.settings_repository import SettingsRepository
from kap_studio.ui.new_project_dialog import NewProjectWizard
from kap_studio.ui.project_editor import ProjectEditor

class WelcomeWindow(QWidget):
    def __init__(self, service: ProjectService, settings: SettingsRepository):
        super().__init__()
        self.service = service
        self.settings = settings
        self.editor = None

        self.setWindowTitle("KAP Studio v0.3.0")
        self.resize(980, 640)
        self._build_ui()
        self.refresh_recent()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 34, 42, 34)
        title = QLabel("KAP Studio")
        title.setStyleSheet("font-size: 30px; font-weight: 800;")
        subtitle = QLabel("Creative Automation Platform")
        subtitle.setStyleSheet("color: #9CA9BA; font-size: 14px;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        buttons = QHBoxLayout()
        new_btn = QPushButton("Новый проект")
        new_btn.setMinimumHeight(48)
        new_btn.clicked.connect(self.create_project)
        open_btn = QPushButton("Открыть проект")
        open_btn.setMinimumHeight(48)
        open_btn.clicked.connect(self.open_project)
        buttons.addWidget(new_btn)
        buttons.addWidget(open_btn)
        layout.addLayout(buttons)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        layout.addWidget(QLabel("<b>Последние проекты</b>"))
        self.recent = QListWidget()
        self.recent.itemDoubleClicked.connect(self.open_recent)
        layout.addWidget(self.recent)

        footer = QLabel("KAP Studio v0.3.0 · Project Manager")
        footer.setAlignment(Qt.AlignRight)
        footer.setStyleSheet("color: #7F8A99;")
        layout.addWidget(footer)

    def refresh_recent(self):
        self.recent.clear()
        for path in self.settings.load_recent():
            item = QListWidgetItem(f"{Path(path).stem}\n{path}")
            item.setData(Qt.UserRole, path)
            self.recent.addItem(item)

    def remember(self, path: Path):
        items = [str(path)] + self.settings.load_recent()
        self.settings.save_recent(items)
        self.refresh_recent()

    def create_project(self):
        wizard = NewProjectWizard(self)
        if wizard.exec() != wizard.Accepted:
            return
        project = wizard.build_project()
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить новый проект", f"{project.product.name}_{project.product.version}.kap",
            "KAP Project (*.kap)"
        )
        if not path:
            return
        try:
            saved = self.service.create(project, path)
            self.remember(saved)
            self.open_editor(project, saved)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка создания", str(exc))

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "KAP Project (*.kap)"
        )
        if path:
            self._open_path(Path(path))

    def open_recent(self, item):
        self._open_path(Path(item.data(Qt.UserRole)))

    def _open_path(self, path: Path):
        try:
            _manifest, project = self.service.open(path)
            self.remember(path)
            self.open_editor(project, path)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка открытия", str(exc))

    def open_editor(self, project, path):
        self.editor = ProjectEditor(self.service, project, Path(path))
        self.editor.show()
