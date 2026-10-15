import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*arguments):
    """
    Функция запуска интерфейса командной строки
    """
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            *[str(argument) for argument in arguments],
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_cli_creates_json_report(tmp_path):
    """
    Позитивный тест корректной работы CLI
    """
    input_file = tmp_path / "events.csv"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-10T10:00:00,INFO,server,Started\n"
        "2026-10-10T10:01:00,ERROR,database,Failed\n",
        encoding="utf-8",
    )

    result = run_cli(
        input_file,
        "--format", "csv",
        "--output", output_file,
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total_events"] == 2
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1
    assert report["sources"] == {"database": 1, "server": 1}
    assert report["top_error_sources"] == [{"source": "database", "count": 1}]
    assert report ["first_timestamp"] == "2026-10-10T10:00:00"
    assert report ["last_timestamp"] == "2026-10-10T10:01:00"


def test_cli_returns_code_2_for_invalid_event(tmp_path):
    """
    Негативный тест корректной работы CLI
    """
    input_file = tmp_path / "broken.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "nao a JSON object\n",
        encoding="utf-8",
    )

    result = run_cli(
        input_file,
        "--format", "jsonl",
        "--output", output_file,
    )

    assert result.returncode == 2
    assert "broken.jsonl" in result.stderr
    assert "1" in result.stderr
    assert not output_file.exists()


def test_cli_skips_invalid_event(tmp_path):
    """
    Позитивный тест корректной работы CLI с флагом --skip-invalid
    """
    input_file = tmp_path / "mixed.jsonl"
    output_file = tmp_path / "report.json"

    input_file.write_text(
        "not a JSON object\n"
        '{"timestamp":"2026-10-10T10:00:00",'
        '"level":"INFO","source":"server","message":"Started"}\n',
        encoding="utf-8",
    )

    result = run_cli(
        input_file,
        "--format", "jsonl",
        "--output", output_file,
        "--skip-invalid",
    )

    assert result.returncode == 0, result.stderr
    assert output_file.exists()

    report = json.loads(output_file.read_text(encoding="utf-8"))

    assert report["total_events"] == 1
    assert report["skipped_lines"] == 1
