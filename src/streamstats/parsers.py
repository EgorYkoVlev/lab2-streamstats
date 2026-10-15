import csv
import json
import logging
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from streamstats.errors import (
    InvalidEventError,
    InvalidLevelError,
    InvalidTimestampError,
    MissingHeaderError,
    MissingRequiredFieldError,
    UnsupportedFormatError,
)
from streamstats.models import Event, Level


def create_event(data: dict, file_path: Path, line_number: int) -> Event:
    """
    Функция валидации полей каждого события
    и преобразования его в тип данных Event
    """
    location = f"{file_path}, строка {line_number}"
    # Проверка на то, что поле source является непустой строкой
    if not isinstance(data["source"], str) or data["source"].strip() == "":
        raise UnsupportedFormatError(
            f"{location}: поле 'source' должно быть непустой строкой"
        )
    # Проверка на то, что поле message является строкой
    if not isinstance(data["message"], str):
        raise UnsupportedFormatError(
            f"{location}: поле 'message' должно быть строкой"
        )
    # Проверка на то, что формат значения поля timestamp
    # соответствует формату ISO 8601
    try:
        timestamp = datetime.fromisoformat(data["timestamp"])
    except (ValueError, TypeError) as error:
        raise InvalidTimestampError(
            f"{location}: неверный формат timestamp"
        ) from error
    # Проверка на то что тип значения поля
    # level является типом данных Level
    try:
        level = Level(data["level"])
    except (ValueError, TypeError) as error:
        raise InvalidLevelError(
            f"{location}: неизвестный уровень"
        ) from error
    # Создания объекта класса Event
    # и его возврат
    return Event(
        timestamp=timestamp,
        level=level,
        source=data["source"],
        message=data["message"],
    )

def parse_csv(
    file_path: Path,
    skipped_lines: list[int],
    skip_invalid: bool = False
) -> Iterator[Event]:
    """
    Функция построкового парсинга событий
    входных файлов формата csv, возвращающая
    генератор типа данных Event
    """
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = ["timestamp", "level", "source", "message"]

        # Проверка на наличие заголовка
        if reader.fieldnames:
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            # Проверка на наличие всех обязательных полей
            for required_field in required_fields:
                if required_field not in reader.fieldnames:
                    raise MissingRequiredFieldError(f"{file_path}: отсутствует обязательное "
                                                    f"поле в заголовке: '{required_field}'"
                    )
        # Проверка на пустоту файла
        elif reader.fieldnames is not None:
            raise MissingHeaderError(f"{file_path}: отсутствует заголовок")

        # Построковое считывание событий и преобразование
        # в тип данных Event
        for line_number, row in enumerate(reader, start=2):
            try:
                event = create_event(row, file_path, line_number)
            except InvalidEventError as error:
                # Проверка на флаг --skip-invalid
                if not skip_invalid:
                    raise

                logging.warning(f"{error}")

                skipped_lines[0] += 1

                continue

            yield event

def parse_jsonl(
    file_path: Path,
    skipped_lines: list[int],
    skip_invalid: bool = False
) -> Iterator[Event]:
    """
        Функция построкового парсинга событий
        входных файлов формата jsonl, возвращающая
        генератор типа данных Event
        """
    with file_path.open("r", encoding="utf-8") as file:
        # Построковое считывание событий и преобразование
        # в тип данных Event
        for line_number, line in enumerate(file, start=1):
            # Проверка на пустую строку
            if line.strip() == "":
                continue

            try:
                data = json.loads(line)

                # Проверка на JSON-объект
                if not isinstance(data, dict):
                    raise UnsupportedFormatError(
                        f"{file_path}, строка {line_number}: ожидался JSON-объект"
                    )

                required_fields = ["timestamp", "level", "source", "message"]

                # Проверка на наличие всех обязательных полей
                for field in required_fields:
                    if field not in data:
                        raise MissingRequiredFieldError(
                            f"{file_path}, строка {line_number}: отсутствует поле '{field}'"
                        )

                event = create_event(data, file_path, line_number)

            except json.JSONDecodeError as error:
                event_error = UnsupportedFormatError(
                    f"{file_path}, строка {line_number}: неверный формат JSONL"
                )
                if not skip_invalid:
                    raise event_error from error

                logging.warning(f"{event_error}")

                skipped_lines[0] += 1

                continue

            except InvalidEventError as error:
                # Проверка на флаг --skip-invalid
                if not skip_invalid:
                    raise

                logging.warning(f"{error}")

                skipped_lines[0] += 1

                continue

            yield event
