import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator

from streamstats.models import Event, Level
from streamstats.errors import InvalidEventError, InvalidTimestampError, InvalidHeaderError, UnsupportedFormatError, \
    InvalidLevelError, MissingRequiredFieldError


def create_event(data: dict, file_path: Path, line_number: int) -> Event:
    location = f"{file_path}, строка {line_number}"

    if not isinstance(data["source"], str) or data["source"].strip() == "":
        raise UnsupportedFormatError(
            f"{location}: поле 'source' должно быть непустой строкой"
        )

    if not isinstance(data["message"], str):
        raise UnsupportedFormatError(
            f"{location}: поле 'message' должно быть строкой"
        )

    try:
        timestamp = datetime.fromisoformat(data["timestamp"])
    except (ValueError, TypeError) as error:
        raise InvalidTimestampError(
            f"{location}: неверный формат timestamp"
        ) from error

    try:
        level = Level(data["level"])
    except (ValueError, TypeError) as error:
        raise InvalidLevelError(
            f"{location}: неизвестный уровень"
        ) from error

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
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = ["timestamp", "level", "source", "message"]

        if reader.fieldnames:
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            for required_field in required_fields:
                if required_field not in reader.fieldnames:
                    raise MissingRequiredFieldError(f"{file_path}: отсутствует обязательное "
                                                    f"поле в заголовке: '{required_field}'"
                    )

        elif reader.fieldnames is not None:
            raise InvalidHeaderError(f"{file_path}: отсутствует заголовок")

        for line_number, row in enumerate(reader, start=2):
            try:
                event = create_event(row, file_path, line_number)
            except InvalidEventError as error:
                if not skip_invalid:
                    raise

                logging.warning("%s", error)

                skipped_lines[0] += 1

                continue

            yield event




def parse_jsonl(
    file_path: Path,
    skipped_lines: list[int],
    skip_invalid: bool = False
) -> Iterator[Event]:
    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip() == "":
                continue

            try:
                data = json.loads(line)

                if not isinstance(data, dict):
                    raise UnsupportedFormatError(
                        f"{file_path}, строка {line_number}: ожидался JSON-объект"
                    )

                required_fields = ["timestamp", "level", "source", "message"]

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

                logging.warning("%s", event_error)

                skipped_lines[0] += 1

                continue

            except InvalidEventError as error:
                if not skip_invalid:
                    raise

                logging.warning("%s", error)

                skipped_lines[0] += 1

                continue

            yield event
