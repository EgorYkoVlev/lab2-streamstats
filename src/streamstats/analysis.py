from _collections_abc import Iterable

from streamstats.models import Event, Level


def analyze(events: Iterable[Event]) -> dict:
    """
    Функция анализа каждого события,
    создающая отчёт
    """
    # Общее число событий
    event_counts = 0
    # Количество событий каждого уровня
    level_counts = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0
    }
    # Количество событий каждого источника
    source_counts = {}
    # Количество событий каждого
    # источника ошибок уровня ERROR/CRITICAL
    source_error_critical_counts = {}
    # Первая временная метка
    first_timestamp = None
    # Последняя временная метка
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
    # top-5 источников ошибок уровня ERROR/CRITICAL
    top_sources_by_errors = sorted(
        source_error_critical_counts.items(),
        key=lambda item: [-item[1], item[0]],
    )[:5]
    # Список top-5 источников ошибок уровня ERROR/CRITICAL
    top_error_sources = []

    for source, count in top_sources_by_errors:
        top_error_sources.append({
            "source": source,
            "count": count,
        })
    # Формирование отчёта
    return {
        "total_events": event_counts,
        "levels": level_counts,
        "sources": source_counts,
        "top_error_sources": top_error_sources,
        "first_timestamp": (
            first_timestamp.isoformat() if first_timestamp else None
        ),
        "last_timestamp": (
            last_timestamp.isoformat() if last_timestamp else None
        )
    }
