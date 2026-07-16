
from __future__ import annotations
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QFormLayout, QLineEdit, QComboBox,
    QListWidget, QListWidgetItem, QVBoxLayout, QLabel
)

from kap_studio.domain.models import Product, KapProject
from kap_studio.domain.journey_factory import build_standard_journey

MARKETPLACES = [
    "Wildberries", "Ozon", "Яндекс Маркет", "МегаМаркет",
    "Авито", "Lamoda", "Детский мир", "Магнит Маркет", "KazanExpress"
]

class NewProjectWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый проект KAP")
        self.resize(620, 420)

        self.product_page = QWizardPage()
        self.product_page.setTitle("Что продаём?")
        form = QFormLayout(self.product_page)

        self.name = QLineEdit()
        self.version = QLineEdit()
        self.manufacturer = QLineEdit()
        self.category = QLineEdit()

        form.addRow("Название продукта", self.name)
        form.addRow("Версия", self.version)
        form.addRow("Производитель", self.manufacturer)
        form.addRow("Категория", self.category)
        self.addPage(self.product_page)

        self.dna_page = QWizardPage()
        self.dna_page.setTitle("Какой характер продукта?")
        form2 = QFormLayout(self.dna_page)
        self.archetype = QComboBox()
        self.archetype.addItems([
            "Creator", "Builder", "Storyteller", "Organizer",
            "Maker", "Musician", "Specialist"
        ])
        self.accent = QLineEdit("#1AA3FF")
        self.audience = QLineEdit()
        self.promise = QLineEdit()
        form2.addRow("Creative DNA", self.archetype)
        form2.addRow("Акцентный цвет", self.accent)
        form2.addRow("Целевая аудитория", self.audience)
        form2.addRow("Главное обещание", self.promise)
        self.addPage(self.dna_page)

        self.market_page = QWizardPage()
        self.market_page.setTitle("Маркетплейсы")
        layout = QVBoxLayout(self.market_page)
        layout.addWidget(QLabel("Выберите площадки проекта:"))
        self.markets = QListWidget()
        for name in MARKETPLACES:
            item = QListWidgetItem(name)
            item.setCheckState(2 if name == "Wildberries" else 0)
            self.markets.addItem(item)
        layout.addWidget(self.markets)
        self.addPage(self.market_page)

    def build_project(self) -> KapProject:
        project_id = "PROD-" + "".join(ch for ch in self.name.text().upper() if ch.isalnum())[:12]
        product = Product(
            id=project_id or "PROD-NEW",
            name=self.name.text().strip(),
            version=self.version.text().strip(),
            manufacturer=self.manufacturer.text().strip(),
            category=self.category.text().strip(),
            archetype=self.archetype.currentText(),
            accent=self.accent.text().strip(),
            audience=self.audience.text().strip(),
            promise=self.promise.text().strip(),
            journey=[],
        )
        product.journey = build_standard_journey(product)
        selected = []
        for i in range(self.markets.count()):
            item = self.markets.item(i)
            if item.checkState() == 2:
                selected.append(item.text())
        return KapProject(product=product, marketplace_profiles=selected)
