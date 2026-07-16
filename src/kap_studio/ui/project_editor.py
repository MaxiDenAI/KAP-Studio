
from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QFileDialog, QMessageBox, QHeaderView, QLabel
)

from kap_studio.application.project_service import ProjectService
from kap_studio.domain.models import KapProject

class ProjectEditor(QMainWindow):
    def __init__(self, service: ProjectService, project: KapProject, path: Path):
        super().__init__()
        self.service = service
        self.project = project
        self.path = path
        self.setWindowTitle(f"KAP Studio — {project.product.name} {project.product.version}")
        self.resize(1280, 820)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.tabs = QTabWidget()
        self.product_tab = QWidget()
        self.journey_tab = QWidget()
        self.review_tab = QWidget()
        self.tabs.addTab(self.product_tab, "Паспорт продукта")
        self.tabs.addTab(self.journey_tab, "Воронка")
        self.tabs.addTab(self.review_tab, "Проверка")
        self.setCentralWidget(self.tabs)

        form = QFormLayout(self.product_tab)
        self.fields = {}
        for key, label in [
            ("id", "ID"), ("name", "Название"), ("version", "Версия"),
            ("manufacturer", "Производитель"), ("category", "Категория"),
            ("accent", "Акцент"), ("audience", "Аудитория"), ("promise", "Обещание")
        ]:
            widget = QTextEdit() if key in ("audience", "promise") else QLineEdit()
            if isinstance(widget, QTextEdit):
                widget.setFixedHeight(70)
            self.fields[key] = widget
            form.addRow(label, widget)

        self.archetype = QComboBox()
        self.archetype.addItems([
            "Creator", "Builder", "Storyteller", "Organizer",
            "Maker", "Musician", "Specialist"
        ])
        form.insertRow(5, "Архетип", self.archetype)

        save_btn = QPushButton("Сохранить проект")
        save_btn.clicked.connect(self.save)
        form.addRow(save_btn)

        jlayout = QVBoxLayout(self.journey_tab)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["№", "Тип", "Этап", "Primary Message", "Hero", "Pattern"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        jlayout.addWidget(self.table)

        rlayout = QVBoxLayout(self.review_tab)
        review_btn = QPushButton("Провести Review")
        review_btn.clicked.connect(self.run_review)
        rlayout.addWidget(review_btn)
        self.review_output = QTextEdit()
        self.review_output.setReadOnly(True)
        rlayout.addWidget(self.review_output)

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
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def apply_form(self):
        p = self.project.product
        for key, widget in self.fields.items():
            value = widget.toPlainText().strip() if isinstance(widget, QTextEdit) else widget.text().strip()
            setattr(p, key, value)
        p.archetype = self.archetype.currentText()

    def save(self):
        try:
            self.apply_form()
            self.path = self.service.save(self.project, self.path)
            self.statusBar().showMessage(f"Сохранено: {self.path}", 5000)
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка сохранения", str(exc))

    def run_review(self):
        self.apply_form()
        report = self.service.review(self.project)
        lines = [
            f"Статус: {'PASS' if report.passed else 'FAIL'}",
            f"Score: {report.score}/100", ""
        ]
        if report.errors:
            lines += ["Ошибки:"] + [f"• {x}" for x in report.errors] + [""]
        if report.warnings:
            lines += ["Предупреждения:"] + [f"• {x}" for x in report.warnings]
        if not report.errors and not report.warnings:
            lines.append("Критических нарушений не найдено.")
        self.review_output.setPlainText("\n".join(lines))
        self.tabs.setCurrentWidget(self.review_tab)
