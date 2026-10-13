import sys
import json
from itertools import chain
from pathlib import Path
from streamstats.analysis import analyze
from streamstats.parsers import parse_jsonl, parse_csv

def json_report(report: dict, out_file: Path) -> None:
    with out_file.open(mode="w", encoding="utf-8", ) as file:
        json.dump(report, file, ensure_ascii=False, indent=4)

def main():
    files = [
        Path("../../json_test.jsonl"),
        Path("../../json_test.jsonl")
    ]

    skipped_lines = [0]

    events = chain.from_iterable(parse_jsonl(file, skipped_lines, True) for file in files)

    result = analyze(events)
    if skipped_lines[0] != 0:
        result["skipped_lines"] = skipped_lines[0]

    json_report(result, Path("REPORT.json"))

if __name__ == "__main__":
    sys.exit(main())