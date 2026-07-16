
from __future__ import annotations
import json
from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QFileDialog, QMessageBox, QHeaderView, QLabel
)

from kap_studio.application.project_service import ProjectService
from kap_studio.domain.models import KapProject, JourneyAsset

class MainWindow(QMainWindow):
    def __init__(self, service: ProjectService, initial_project: KapProject):
        super().__init__()
        self.service = service
        self.project = initial_project
        self.current_path: Path | None = None

        self.setWindowTitle("KAP Studio v0.2.0 — Workspace Engine")
        self.resize(1280, 820)
        self._build_menu()
        self._build_ui()
        self.refresh()

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("Файл")

        action = QAction("Новый .kap", self)
        action.triggered.connect(self.create_workspace)
        file_menu.addAction(action)

        action = QAction("Открыть .kap", self)
        action.triggered.connect(self.open_workspace)
        file_menu.addAction(action)

        action = QAction("Сохранить", self)
        action.triggered.connect(self.save_workspace)
        file_menu.addAction(action)

        action = QAction("Сохранить как…", self)
        action.triggered.connect(self.save_workspace_as)
        file_menu.addAction(action)

        action = QAction("Экспорт JSON", self)
        action.triggered.connect(self.export_json)
        file_menu.addAction(action)

        review_action = QAction("Провести Review", self)
        review_action.triggered.connect(self.run_review)
        self.menuBar().addAction(review_action)

    def _build_ui(self):
        self.tabs = QTabWidget()
        self.product_tab = QWidget()
        self.journey_tab = QWidget()
        self.review_tab = QWidget()

        self.tabs.addTab(self.product_tab, "Product DNA")
        self.tabs.addTab(self.journey_tab, "Journey")
        self.tabs.addTab(self.review_tab, "Review")
        self.setCentralWidget(self.tabs)

        form = QFormLayout(self.product_tab)
        self.fields = {}

        for key, label in [
            ("id", "ID"), ("name", "Название"), ("version", "Версия"),
            ("manufacturer", "Производитель"), ("category", "Категория"),
            ("accent", "Акцентный цвет"), ("audience", "Целевая аудитория"),
            ("promise", "Главное обещание"),
        ]:
            widget = QTextEdit() if key in ("audience", "promise") else QLineEdit()
            if isinstance(widget, QTextEdit):
                widget.setFixedHeight(72)
            self.fields[key] = widget
            form.addRow(label, widget)

        self.archetype = QComboBox()
        self.archetype.addItems([
            "Creator", "Builder", "Storyteller", "Organizer",
            "Maker", "Musician", "Specialist"
        ])
        form.insertRow(5, "Архетип", self.archetype)

        apply_button = QPushButton("Применить Product DNA")
        apply_button.clicked.connect(self.apply_product)
        form.addRow(apply_button)

        journey_layout = QVBoxLayout(self.journey_tab)
        journey_layout.addWidget(QLabel("Двойной щелчок по строке открывает JSON-редактор Asset."))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            "№", "Тип", "Этап", "Primary Message", "Hero", "Pattern"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemDoubleClicked.connect(self.edit_asset)
        journey_layout.addWidget(self.table)

        review_layout = QVBoxLayout(self.review_tab)
        button = QPushButton("Провести Review")
        button.clicked.connect(self.run_review)
        review_layout.addWidget(button)
        self.review_output = QTextEdit()
        self.review_output.setReadOnly(True)
        review_layout.addWidget(self.review_output)

    def refresh(self):
        p = self.project.product
        for key, widget in self.fields.items():
            value = getattr(p, key)
            if isinstance(widget, QTextEdit):
                widget.setPlainText(value)
            else:
                widget.setText(value)
        self.archetype.setCurrentText(p.archetype)

        self.table.setRowCount(len(p.journey))
        for row, asset in enumerate(p.journey):
            values = [
                asset.position, asset.type, asset.stage,
                asset.primary_message, asset.hero, asset.pattern
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

    def apply_product(self):
        p = self.project.product
        for key, widget in self.fields.items():
            value = widget.toPlainText().strip() if isinstance(widget, QTextEdit) else widget.text().strip()
            setattr(p, key, value)
        p.archetype = self.archetype.currentText()

    def edit_asset(self, item):
        row = item.row()
        asset = self.project.product.journey[row]

        dialog = QMessageBox(self)
        dialog.setWindowTitle(f"Asset {asset.position}")
        editor = QTextEdit(asset.model_dump_json(indent=2))
        editor.setMinimumSize(720, 480)
        dialog.layout().addWidget(editor, 1, 0, 1, dialog.layout().columnCount())
        dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)

        if dialog.exec() == QMessageBox.Save:
            try:
                self.project.product.journey[row] = JourneyAsset.model_validate_json(editor.toPlainText())
                self.refresh()
            except Exception as exc:
                QMessageBox.critical(self, "Ошибка спецификации", str(exc))

    def create_workspace(self):
        path, _ = QFileDialog.getSaveFileName(self, "Создать проект", "project.kap", "KAP Project (*.kap)")
        if not path:
            return
        self.apply_product()
        try:
            self.current_path = self.service.create(self.project, path)
            self.statusBar().showMessage(f"Создан проект: {self.current_path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def open_workspace(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть проект", "", "KAP Project (*.kap)")
        if not path:
            return
        try:
            manifest, project = self.service.open(path)
            self.project = project
            self.current_path = Path(path)
            self.refresh()
            self.statusBar().showMessage(
                f"Открыт: {manifest.project_name} · revision {manifest.revision}", 6000
            )
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка открытия", str(exc))

    def save_workspace(self):
        self.apply_product()
        if self.current_path is None:
            self.save_workspace_as()
            return
        try:
            self.current_path = self.service.save(self.project, self.current_path)
            self.statusBar().showMessage(f"Сохранено: {self.current_path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка сохранения", str(exc))

    def save_workspace_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить проект как", "project.kap", "KAP Project (*.kap)")
        if not path:
            return
        self.apply_product()
        try:
            self.current_path = self.service.save(self.project, path)
            self.statusBar().showMessage(f"Сохранено: {self.current_path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка сохранения", str(exc))

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт JSON", "project.kap.json", "JSON (*.json)")
        if not path:
            return
        self.apply_product()
        try:
            self.service.workspace.export_json(self.project, path)
            self.statusBar().showMessage(f"Экспортировано: {path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка экспорта", str(exc))

    def run_review(self):
        self.apply_product()
        report = self.service.review(self.project)
        lines = [
            f"Статус: {'PASS' if report.passed else 'FAIL'}",
            f"Score: {report.score}/100",
            "",
        ]
        if report.errors:
            lines += ["Ошибки:"] + [f"• {item}" for item in report.errors] + [""]
        if report.warnings:
            lines += ["Предупреждения:"] + [f"• {item}" for item in report.warnings]
        if not report.errors and not report.warnings:
            lines.append("Критических нарушений не найдено.")
        self.review_output.setPlainText("\n".join(lines))
        self.tabs.setCurrentWidget(self.review_tab)
