
from __future__ import annotations
from .models import Product, JourneyAsset

ENDING = {
    "Creator": "ТВОРИТЕ БЕЗ ГРАНИЦ",
    "Builder": "ВАШ СЛЕДУЮЩИЙ ПРОЕКТ НАЧИНАЕТСЯ ЗДЕСЬ",
    "Storyteller": "КАЖДЫЙ КАДР МОЖЕТ СТАТЬ ИСТОРИЕЙ",
    "Organizer": "РАБОТАЙТЕ БЫСТРЕЕ И СПОКОЙНЕЕ",
    "Maker": "СОЗДАВАЙТЕ ТО, ЧТО ОСТАНЕТСЯ",
    "Musician": "ПУСТЬ ВАША МУЗЫКА ЗВУЧИТ",
    "Specialist": "ТОЧНОСТЬ, КОТОРОЙ МОЖНО ДОВЕРЯТЬ",
}

def build_standard_journey(product: Product) -> list[JourneyAsset]:
    ending = ENDING.get(product.archetype, "НАЧНИТЕ НОВУЮ ГЛАВУ ПРОФЕССИОНАЛЬНОЙ РАБОТЫ")
    return [
        JourneyAsset(position=1, type="DISCOVERY", stage="RECOGNITION",
            primary_message=f"{product.name} {product.version}", hero="PRODUCT_BOX",
            pattern="PAT-0001", goal="Остановить взгляд и распознать профессиональный продукт"),
        JourneyAsset(position=2, type="PACKAGE", stage="UNDERSTANDING",
            primary_message="ЧТО ВЫ ПОЛУЧИТЕ", hero="OPEN_PRODUCT_BOX",
            pattern="PAT-0002", goal="Снять неопределённость комплектации"),
        JourneyAsset(position=3, type="RESULT", stage="ASPIRATION",
            primary_message="ЧТО МОЖНО СОЗДАТЬ", hero="RESULT_SHOWCASE",
            pattern="PAT-0003", goal="Показать профессиональный результат"),
        JourneyAsset(position=4, type="PROCESS", stage="PROCESS_CONFIDENCE",
            primary_message="КАК ПОЛУЧИТЬ ТОВАР", hero="NUMBERS_1_2_3",
            pattern="PAT-0004", goal="Снять страх получения цифрового товара"),
        JourneyAsset(position=5, type="SERVICE", stage="SELLER_TRUST",
            primary_message="ПОЧЕМУ ВЫБИРАЮТ KAP STORE", hero="SERVICE_GRID",
            pattern="PAT-0005", goal="Усилить доверие к сервису"),
        JourneyAsset(position=6, type="COMPATIBILITY", stage="COMPATIBILITY_CONFIDENCE",
            primary_message="СИСТЕМНЫЕ ТРЕБОВАНИЯ", hero="RECOMMENDED_CONFIGURATION",
            pattern="PAT-0006", goal="Снять техническое сомнение"),
        JourneyAsset(position=7, type="EMOTIONAL_ENDING", stage="MENTAL_OWNERSHIP",
            primary_message=ending, hero="FUTURE_RESULT",
            pattern="PAT-0007", goal="Представить начало профессиональной работы"),
    ]
