import json

import pytest

from streamstats.errors import (
    InvalidTimestampError,
    MissingHeaderError,
    MissingRequiredFieldError,
    UnsupportedFormatError,
)
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_csv(tmp_path):
    file_path = tmp_path / "test.csv"

    file_path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-14T10:00:00,INFO,server,Started\n"
        "2026-10-14T10:01:00,ERROR,database,Failed\n"
        "2026-10-14T10:02:20,WARNING,server,Broken\n",
        encoding="utf-8",
    )

    events = list(parse_csv(file_path, [0], False))

    assert len(events) == 3
    assert events[0].timestamp.isoformat() == "2026-10-14T10:00:00"
    assert events[1].timestamp.isoformat() == "2026-10-14T10:01:00"
    assert events[2].timestamp.isoformat() == "2026-10-14T10:02:20"
    assert events[0].level.value == "INFO"
    assert events[1].level.value == "ERROR"
    assert events[2].level.value == "WARNING"
    assert events[0].source == "server"
    assert events[1].source == "database"
    assert events[2].source == "server"
    assert events[0].message == "Started"
    assert events[1].message == "Failed"
    assert events[2].message == "Broken"


def test_parse_jsonl(tmp_path):
    file_path = tmp_path / "test.jsonl"

    file_path.write_text(
        '{"timestamp":"2026-10-10T10:00:00",'
        '"level":"INFO","source":"server","message":"Started"}\n'
        '{"timestamp":"2026-10-12T10:01:00",'
        '"level":"ERROR","source":"database","message":"Failed"}\n'
        '{"timestamp":"2026-10-14T10:02:20",'
        '"level":"WARNING","source":"server","message":"Broken"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(file_path, [0], False))

    assert len(events) == 3
    assert events[0].timestamp.isoformat() == "2026-10-10T10:00:00"
    assert events[1].timestamp.isoformat() == "2026-10-12T10:01:00"
    assert events[2].timestamp.isoformat() == "2026-10-14T10:02:20"
    assert events[0].level.value == "INFO"
    assert events[1].level.value == "ERROR"
    assert events[2].level.value == "WARNING"
    assert events[0].source == "server"
    assert events[1].source == "database"
    assert events[2].source == "server"
    assert events[0].message == "Started"
    assert events[1].message == "Failed"
    assert events[2].message == "Broken"


def test_empty_csv_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    events = list(parse_csv(file_path, [0], False))

    assert events == []


def test_empty_jsonl_file(tmp_path):
    file_path = tmp_path / "empty.jsonl"
    file_path.write_text("", encoding="utf-8")

    events = list(parse_jsonl(file_path, [0], False))

    assert events == []


def test_parse_csv_invalid_1(tmp_path):
    file_path = tmp_path / "broken.csv"

    file_path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-14T10:02:20,INFO,server,Started\n"
        "2026:10:14T10-02-20,DEBUG,database,Crashed\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidTimestampError):
        list(parse_csv(file_path, [0], False))

def test_parse_csv_invalid_2(tmp_path):
    file_path = tmp_path / "broken.csv"

    file_path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-14T10:02:20,INFO,server,Started\n"
        "2026-10-14T10:02:20,DEBUG,,Crashed\n",
        encoding="utf-8",
    )

    with pytest.raises(UnsupportedFormatError):
        list(parse_csv(file_path, [0], False))

def test_parse_csv_skip_invalid(tmp_path):
    file_path = tmp_path / "broken.csv"

    file_path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-14T10:02:20,INFO,server,Started\n"
        "2026:10:14T10-02-20,DEBUG,database,Crashed\n"
        "2026-10-14T10:01:00,ERROR,database,Failed\n",
        encoding="utf-8",
    )

    skipped_lines = [0]

    events = list(
        parse_csv(
            file_path,
            skipped_lines=skipped_lines,
            skip_invalid=True
        )
    )

    assert len(events) == 2
    assert events[0].timestamp.isoformat() == "2026-10-14T10:02:20"
    assert events[1].timestamp.isoformat() == "2026-10-14T10:01:00"
    assert events[0].level.value == "INFO"
    assert events[1].level.value == "ERROR"
    assert events[0].source == "server"
    assert events[1].source == "database"
    assert events[0].message == "Started"
    assert events[1].message == "Failed"
    assert skipped_lines[0] == 1

def test_missing_header_csv(tmp_path):
    file_path = tmp_path / "broken.csv"

    file_path.write_text(
        "\n2026-10-14T10:02:20,INFO,server,Started\n"
        "2026-10-14T10:01:00,ERROR,database,Failed\n",
    )

    with pytest.raises(MissingHeaderError):
        list(parse_csv(file_path, [0], False))

def test_parse_jsonl_invalid(tmp_path):
    file_path = tmp_path / "broken.jsonl"

    file_path.write_text(
        '{"timestamp":"2026-10-10T10:00:00",'
        '"level":"INFO","source":"server","message":"Started"}\n'
        '{"timestamp":"2026-10-12T10:01:00",'
        '"level":"ERROR","message":"Failed"}\n'
        '{"timestamp":"2026-10-14T10:02:20",'
        '"level":"WARNING","source":"server","message":"Broken"}\n',
        encoding="utf-8",
    )

    with pytest.raises(MissingRequiredFieldError):
        list(parse_jsonl(file_path, [0], False))


def test_parse_jsonl_skip_invalid(tmp_path):
    file_path = tmp_path / "broken.jsonl"

    file_path.write_text(
        "not a JSON object\n"
        '{"timestamp":"2026-10-10T10:01:00",'
        '"level":"INFO","source":"server","message":"Valid"}\n',
        encoding="utf-8",
    )

    skipped_lines = [0]

    events = list(
        parse_jsonl(
            file_path,
            skipped_lines=skipped_lines,
            skip_invalid=True,
        )
    )

    assert len(events) == 1
    assert events[0].timestamp.isoformat() == "2026-10-10T10:01:00"
    assert events[0].level.value == "INFO"
    assert events[0].source == "server"
    assert events[0].message == "Valid"
    assert skipped_lines[0] == 1


def test_unicode(tmp_path):
    file_path = tmp_path / "unicode.jsonl"

    file_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-10-10T10:00:00",
                "level": "INFO",
                "source": "сервер",
                "message": "Ошибка подключения — база данных недоступна",
            },
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    events = list(parse_jsonl(file_path, [0], False))

    assert events[0].source == "сервер"
    assert events[0].message == "Ошибка подключения — база данных недоступна"
