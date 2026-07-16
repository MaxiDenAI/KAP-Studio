
from __future__ import annotations
from dataclasses import dataclass, field
from .models import KapProject

AGGRESSIVE = (
    "ОФОРМИТЕ ЗАКАЗ", "КУПИТЕ СЕЙЧАС", "ЗАКАЖИТЕ",
    "НАЖМИТЕ КУПИТЬ", "УСПЕЙТЕ ПРИОБРЕСТИ"
)

@dataclass
class ReviewReport:
    passed: bool
    score: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

def review_project(project: KapProject) -> ReviewReport:
    errors, warnings = [], []
    p = project.product

    if not all([p.id, p.name, p.version, p.manufacturer]):
        errors.append("Не заполнены обязательные поля Product DNA.")

    if len(p.journey) != 7:
        errors.append("Journey должен содержать ровно 7 карточек.")

    if [a.position for a in p.journey] != list(range(1, 8)):
        errors.append("Нарушена последовательность Journey 1–7.")

    seen_stages = set()
    for a in p.journey:
        if a.stage in seen_stages:
            warnings.append(f"Повторяется Journey Stage: {a.stage}.")
        seen_stages.add(a.stage)

        if a.hero_count != 1:
            errors.append(f"Карточка {a.position}: должен быть один Hero.")
        if not a.primary_message.strip():
            errors.append(f"Карточка {a.position}: отсутствует Primary Message.")
        if a.brand_footer != "external_only":
            errors.append(f"Карточка {a.position}: Brand Lock должен быть внешним.")

    if p.journey:
        final = p.journey[-1].primary_message.upper()
        if any(x in final for x in AGGRESSIVE):
            errors.append("Карточка 7 содержит агрессивный CTA.")

    if project.brand.footer_mode != "external_only":
        errors.append("Футер KAP должен накладываться только внешним утверждённым Asset.")

    if project.brand.safe_area_height_px < 260:
        warnings.append("Safe Area меньше рекомендуемых 260 px.")

    score = max(0, 100 - len(errors) * 20 - len(warnings) * 5)
    return ReviewReport(not errors and score >= 90, score, errors, warnings)
