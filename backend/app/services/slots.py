"""Pure slot-generation logic (no I/O) so it is trivial to unit test."""
from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Protocol
from datetime import time


class ScheduleLike(Protocol):
    weekday: int
    start_time: time
    end_time: time


def generate_slots(
    day: date, schedules: Iterable[ScheduleLike], slot_minutes: int, tz: tzinfo
) -> list[datetime]:
    """All slot start times (UTC, aware) for `day`, where `day` is a clinic-local date."""
    step = timedelta(minutes=slot_minutes)
    slots: set[datetime] = set()
    for sched in schedules:
        if sched.weekday != day.weekday():
            continue
        cursor = datetime.combine(day, sched.start_time, tzinfo=tz)
        end = datetime.combine(day, sched.end_time, tzinfo=tz)
        while cursor + step <= end:
            slots.add(cursor.astimezone(timezone.utc))
            cursor += step
    return sorted(slots)
