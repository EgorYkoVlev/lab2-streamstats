import csv
import json
from datetime import datetime
from pathlib import Path
from collections.abc import Iterator

from streamstats.models import Event, Level


def parse_csv(file_path: Path) -> Iterator[Event]:
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            event = Event(
                timestamp=datetime.fromisoformat(row["timestamp"]),
                level=Level(row["level"]),
                source=row["source"],
                message=row["message"],
            )

            yield event

def parse_jsonl(file_path: Path) -> Iterator[Event]:
    with file_path.open("r", encoding="utf-8") as file:
        line_number = 0

        for line in file:
            line_number += 1

            if line.strip == "":
                continue

            data = json.loads(line)
            event = Event(
                timestamp=datetime.fromisoformat(data["timestamp"]),
                level=Level(data["level"]),
                source=data["source"],
                message=data["message"]
            )

            yield event