
from itertools import chain

from streamstats.analysis import analyze
from streamstats.parsers import parse_csv, parse_jsonl


def test_several_csv_files(tmp_path):
    first_file = tmp_path / "first.csv"
    second_file = tmp_path / "second.csv"

    skipped_lines = [0]

    first_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-10T10:00:00,INFO,server,Started\n",
        encoding="utf-8",
    )
    second_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-10T10:01:00,ERROR,database,Failed\n"
        "2026-10-10T10:02:00,ERROR,,Failed\n",
        encoding="utf-8",
    )

    events = chain.from_iterable(
        parse_csv(path, skipped_lines, True) for path in [first_file, second_file]
    )
    report = analyze(events)

    assert report["total_events"] == 2
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1
    assert report["sources"] == {"server": 1, "database": 1}
    assert report["top_error_sources"] == [{"source": "database", "count": 1}]
    assert report["first_timestamp"] == "2026-10-10T10:00:00"
    assert report["last_timestamp"] == "2026-10-10T10:01:00"
    assert skipped_lines[0] == 1


def test_csv_and_jsonl_produce_same_statistics(tmp_path):
    csv_file = tmp_path / "events.csv"
    jsonl_file = tmp_path / "events.jsonl"

    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-10T10:00:00,INFO,server,Started\n"
        "2026-10-10T10:01:00,ERROR,database,Failed\n",
        encoding="utf-8",
    )
    jsonl_file.write_text(
        '{"timestamp":"2026-10-10T10:00:00",'
        '"level":"INFO","source":"server","message":"Started"}\n'
        '{"timestamp":"2026-10-10T10:01:00",'
        '"level":"ERROR","source":"database","message":"Failed"}\n',
        encoding="utf-8",
    )

    csv_report = analyze(parse_csv(csv_file, [0], False))
    jsonl_report = analyze(parse_jsonl(jsonl_file, [0], False))

    assert csv_report == jsonl_report
