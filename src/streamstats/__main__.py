import argparse
import json
import sys
from itertools import chain
from pathlib import Path

from streamstats.analysis import analyze
from streamstats.errors import StreamStatsError
from streamstats.parsers import parse_csv, parse_jsonl


def parse_CLI() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        prog="streamstats",
        description="Потоковый анализатор файлов"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Проанализировать события из файла(ов) и создать отчёт"
    )

    analyze_parser.add_argument(
        "input",
        nargs="+",
        help="Пути к входным файлам"
    )

    analyze_parser.add_argument(
        "--format",
        choices=["jsonl", "csv"],
        required=True,
        help="Формат подаваемых на вход файлов"
    )

    analyze_parser.add_argument(
        "--output",
        required=True,
        help="Путь к JSON-файлу для записи отчёта"
    )

    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Пропускать некорректные записи"
    )

    return parser

def json_report(report: dict, out_file: Path) -> None:
    with out_file.open(mode="w", encoding="utf-8", ) as file:
        json.dump(report, file, ensure_ascii=False, indent=4)
        file.write("\n")

def main() -> int:
    parser = parse_CLI()
    args = parser.parse_args()

    if args.format == "jsonl":
        parse_file_type = parse_jsonl
    else:
        parse_file_type = parse_csv

    try:
        skipped_lines_count = [0]

        file_paths = [Path(file_path) for file_path in args.input]

        for path in file_paths:
            if not path.is_file():
                raise StreamStatsError(
                    f"входной файл не найден: {path}"
                )

        events = chain.from_iterable(
            parse_file_type(
                file_path,
                skipped_lines_count,
                args.skip_invalid
            )
            for file_path in file_paths
        )

        report = analyze(events)

        if skipped_lines_count[0] != 0:
            report["skipped_lines"] = skipped_lines_count[0]

        json_report(report, Path(args.output))

    except StreamStatsError as error:

        print(f"Ошибка: {error}", file=sys.stderr)

        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
