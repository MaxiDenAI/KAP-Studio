
from __future__ import annotations
import json, sys
from pathlib import Path
from pydantic import BaseModel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QSplitter,QVBoxLayout,QFormLayout,
    QLineEdit,QTextEdit,QComboBox,QPushButton,QTableWidget,QTableWidgetItem,
    QTabWidget,QFileDialog,QMessageBox,QHeaderView,QLabel
)

class Asset(BaseModel):
    position:int; type:str; stage:str; primary_message:str
    hero:str; pattern:str; goal:str; hero_count:int=1
    brand_footer:str="external_only"

class Product(BaseModel):
    id:str; name:str; version:str; manufacturer:str; category:str
    archetype:str; accent:str; audience:str; promise:str
    journey:list[Asset]=[]

class Project(BaseModel):
    kap_version:str="0.2.0"; schema_version:str="1.0"
    product:Product; marketplace_profiles:list[str]=[]
    brand:dict={"footer_mode":"external_only","safe_area_height_px":280}
    exported_at:str|None=None

def review(p:Project):
    errors=[]; warnings=[]
    if not all([p.product.id,p.product.name,p.product.version,p.product.manufacturer]):
        errors.append("Не заполнены обязательные поля Product DNA.")
    if len(p.product.journey)!=7:
        errors.append("Journey должен содержать 7 карточек.")
    if [a.position for a in p.product.journey] != list(range(1,8)):
        errors.append("Нарушена последовательность Journey 1–7.")
    for a in p.product.journey:
        if a.hero_count != 1: errors.append(f"Карточка {a.position}: должен быть один Hero.")
        if not a.primary_message.strip(): errors.append(f"Карточка {a.position}: нет Primary Message.")
        if a.brand_footer != "external_only": errors.append(f"Карточка {a.position}: Brand Lock должен быть внешним.")
    if p.product.journey:
        final=p.product.journey[-1].primary_message.upper()
        if any(x in final for x in ("ОФОРМИТЕ ЗАКАЗ","КУПИТЕ СЕЙЧАС","ЗАКАЖИТЕ")):
            errors.append("Карточка 7 содержит агрессивный CTA.")
    if p.brand.get("footer_mode")!="external_only":
        errors.append("Футер должен накладываться внешним утверждённым Asset.")
    score=max(0,100-len(errors)*20-len(warnings)*5)
    return score,errors,warnings

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAP Studio v0.1.0")
        self.resize(1280,800)
        self.project=None; self.path=None
        self._menu(); self._ui()
        seed=Path(__file__).resolve().parents[2]/"data"/"photoshop_2023.kap.json"
        if seed.exists(): self.load(seed)

    def _menu(self):
        m=self.menuBar().addMenu("Файл")
        a=QAction("Открыть",self); a.triggered.connect(self.open); m.addAction(a)
        a=QAction("Сохранить",self); a.triggered.connect(self.save); m.addAction(a)
        a=QAction("Сохранить как",self); a.triggered.connect(self.save_as); m.addAction(a)
        a=QAction("Review",self); a.triggered.connect(self.run_review); self.menuBar().addAction(a)

    def _ui(self):
        self.tabs=QTabWidget()
        self.product_tab=QWidget(); self.journey_tab=QWidget(); self.review_tab=QWidget()
        self.tabs.addTab(self.product_tab,"Product DNA")
        self.tabs.addTab(self.journey_tab,"Journey")
        self.tabs.addTab(self.review_tab,"Review")

        form=QFormLayout(self.product_tab); self.f={}
        for key,label in [("id","ID"),("name","Название"),("version","Версия"),
                          ("manufacturer","Производитель"),("category","Категория"),
                          ("accent","Акцент"),("audience","Аудитория"),("promise","Обещание")]:
            w=QTextEdit() if key in ("audience","promise") else QLineEdit()
            if isinstance(w,QTextEdit): w.setFixedHeight(75)
            self.f[key]=w; form.addRow(label,w)
        self.arch=QComboBox(); self.arch.addItems(
            ["Creator","Builder","Storyteller","Organizer","Maker","Musician","Specialist"])
        form.insertRow(5,"Архетип",self.arch)
        b=QPushButton("Применить Product DNA"); b.clicked.connect(self.apply_product); form.addRow(b)

        lay=QVBoxLayout(self.journey_tab)
        self.table=QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(["№","Тип","Этап","Primary Message","Hero","Pattern"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemDoubleClicked.connect(self.edit_asset)
        lay.addWidget(QLabel("Двойной щелчок по строке открывает JSON-редактор Asset."))
        lay.addWidget(self.table)

        rl=QVBoxLayout(self.review_tab)
        rb=QPushButton("Провести Review"); rb.clicked.connect(self.run_review); rl.addWidget(rb)
        self.out=QTextEdit(); self.out.setReadOnly(True); rl.addWidget(self.out)

        self.setCentralWidget(self.tabs)

    def load(self,path):
        self.project=Project.model_validate_json(Path(path).read_text(encoding="utf-8"))
        self.path=Path(path); self.refresh()

    def refresh(self):
        p=self.project.product
        for k,w in self.f.items():
            v=getattr(p,k)
            w.setPlainText(v) if isinstance(w,QTextEdit) else w.setText(v)
        self.arch.setCurrentText(p.archetype)
        self.table.setRowCount(len(p.journey))
        for r,a in enumerate(p.journey):
            for c,v in enumerate([a.position,a.type,a.stage,a.primary_message,a.hero,a.pattern]):
                self.table.setItem(r,c,QTableWidgetItem(str(v)))

    def apply_product(self):
        p=self.project.product
        for k,w in self.f.items():
            setattr(p,k,w.toPlainText().strip() if isinstance(w,QTextEdit) else w.text().strip())
        p.archetype=self.arch.currentText()
        QMessageBox.information(self,"KAP Studio","Product DNA применён.")

    def edit_asset(self,item):
        row=item.row(); a=self.project.product.journey[row]
        dlg=QMessageBox(self); dlg.setWindowTitle(f"Asset {a.position}")
        ed=QTextEdit(a.model_dump_json(indent=2)); ed.setMinimumSize(720,480)
        dlg.layout().addWidget(ed,1,0,1,dlg.layout().columnCount())
        dlg.setStandardButtons(QMessageBox.Save|QMessageBox.Cancel)
        if dlg.exec()==QMessageBox.Save:
            try:
                self.project.product.journey[row]=Asset.model_validate_json(ed.toPlainText())
                self.refresh()
            except Exception as e: QMessageBox.critical(self,"Ошибка",str(e))

    def open(self):
        p,_=QFileDialog.getOpenFileName(self,"Открыть KAP","","KAP JSON (*.json *.kap)")
        if p:
            try:self.load(p)
            except Exception as e: QMessageBox.critical(self,"Ошибка",str(e))

    def save(self):
        self.apply_product()
        if not self.path: return self.save_as()
        self.path.write_text(self.project.model_dump_json(indent=2),encoding="utf-8")
        self.statusBar().showMessage(f"Сохранено: {self.path}",4000)

    def save_as(self):
        p,_=QFileDialog.getSaveFileName(self,"Сохранить","project.kap.json","JSON (*.json)")
        if p:self.path=Path(p);self.save()

    def run_review(self):
        self.apply_product()
        score,errors,warnings=review(self.project)
        lines=[f"Статус: {'PASS' if not errors and score>=90 else 'FAIL'}",f"Score: {score}/100",""]
        if errors: lines+=["Ошибки:"]+[f"• {x}" for x in errors]
        if warnings: lines+=["","Предупреждения:"]+[f"• {x}" for x in warnings]
        if not errors and not warnings: lines+=["Критических нарушений не найдено."]
        self.out.setPlainText("\n".join(lines)); self.tabs.setCurrentWidget(self.review_tab)

def main():
    app=QApplication(sys.argv)
    win=Main(); win.show()
    raise SystemExit(app.exec())

if __name__=="__main__": main()
