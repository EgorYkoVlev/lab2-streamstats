# Лабораторная работа №2. Потоковый анализатор файлов 'streamstats'

## Назначение программы

Чтение событий из логов построчно с последующим формированием JSON-файла с отчётом.

## Обязательные поля событий

```text
timestamp: ISO 8601
level: DEBUG | INFO | WARNING | ERROR | CRITICAL
source: непустая строка
message: строка
```

## Возможности

- Поддержка CSV с заголовком и JSON.
- Объединение статистики нескольких входных файлов.
- Подсчёт общего числа событий.
- Подсчёт количества событий каждого уровня.
- Подсчёт количества событий каждого источника.
- Вывод top-5 источников ошибок уровня ERROR/CRITICAL.
- Нахождение первой и последней временной метки.
- Формирование JSON-отчёта.

## Поддерживаемые команды

```text
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output report.json

python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output report.json --skip-invalid

python -m streamstats --help

python -m streamstats analyze --help
```

## Обработка ошибочных строк

Режим по умолчанию: остановка обработки, вывод номер файла и строки, завершение CLI с кодом `2`.

Режим `--skip-invalid`: пропуск некорректной строки, запись WARNING в лог, добавление числа пропущенных строк в отчёт.

## Структура

```text
lab2-streamstats/
  pyproject.toml
  README.md
  src/streamstats/
    __init__.py
    __main__.py
    models.py
    parsers.py
    analysis.py
    report.py
    errors.py
  tests/
    test_analysis.py
    test_CLI.py
    test_parsers.py
```

## Команды проверки

### Тесты

Unit-тесты проверяют как успешные сценарии, так и ошибки:

- Несуществование входных файлов.
- Отсутствие обязательных полей.
- Отсутствие заголовка в CSV.
- Синтаксическая ошибка в JSONL.
- Строка не является JSON-объектом.

Запуск всех 16 unit-тестов:

```shell
python -m pytest
```

### Ruff

Запуск проверки:

```shell
ruff check .
```

