# KAP Studio v0.1.0

Первый исходный репозиторий полноценного настольного приложения на PySide6/Qt.

## Реализовано
- открытие и сохранение `.kap.json`;
- Product DNA Editor;
- Journey из 7 карточек;
- JSON-редактор отдельного Asset;
- Review Engine;
- проверка одного Hero;
- внешний Brand Lock;
- запрет агрессивного CTA на карточке №7;
- стартовый проект Adobe Photoshop 2023.

## Сборка EXE
Готовый Windows EXE должен собираться в Windows-среде.

Локально:
1. `scripts\setup_windows.bat`
2. `scripts\build_windows_exe.bat`

После сборки конечному пользователю Python не нужен.

Автоматически:
- загрузить проект на GitHub;
- открыть Actions;
- запустить `Build Windows EXE`;
- скачать артефакт `KAP-Studio-Windows`.

## Следующий релиз
Project Explorer, Registry, Pattern Library, Marketplace Profiles,
Generation Plan Compiler и Brand Assembly Module.
