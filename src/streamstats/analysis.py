from _collections_abc import Iterable

from streamstats.models import Event, Level

def analyze(events: Iterable[Event]) -> dict:
    event_counts = 0

    level_counts = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0
    }

    source_counts = {}
    source_error_critical_counts = {}

    first_timestamp = None
    last_timestamp = None

    for event in events:
        event_counts += 1

        level_counts[event.level.value] += 1

        source_counts[event.source] = source_counts.get(event.source, 0) + 1

        if event.level == Level.ERROR or event.level == Level.CRITICAL:
            source_error_critical_counts[event.source] = source_error_critical_counts.get(event.source, 0) + 1

        if first_timestamp is None or event.timestamp < first_timestamp:
            first_timestamp = event.timestamp

        if last_timestamp is None or event.timestamp > last_timestamp:
            last_timestamp = event.timestamp

    top_sources_by_errors = sorted(
        source_error_critical_counts.items(),
        key=lambda item: [-item[1], item[0]],
    )[:5]

    top_error_sources = []

    for source, count in top_sources_by_errors:
        top_error_sources.append({
            "source": source,
            "count": count,
        })

    return {
        "total_events": event_counts,
        "levels": level_counts,
        "sources": source_counts,
        "top_error_sources": top_error_sources,
        "first_timestamp": (
            first_timestamp.isoformat() if first_timestamp is not None else None
        ),
        "last_timestamp": (
            last_timestamp.isoformat() if last_timestamp is not None else None
        ),
    }
