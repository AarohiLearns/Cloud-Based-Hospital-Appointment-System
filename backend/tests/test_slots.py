from datetime import date, time, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.services.slots import generate_slots

IST = ZoneInfo("Asia/Kolkata")


def test_generates_slots_in_clinic_time_returned_as_utc():
    day = date(2030, 1, 7)  # a Monday
    sched = [SimpleNamespace(weekday=0, start_time=time(9), end_time=time(11))]
    slots = generate_slots(day, sched, 30, IST)
    assert len(slots) == 4
    assert slots[0].tzinfo == timezone.utc
    assert slots[0].astimezone(IST).hour == 9


def test_other_weekday_has_no_slots():
    sched = [SimpleNamespace(weekday=1, start_time=time(9), end_time=time(11))]
    assert generate_slots(date(2030, 1, 7), sched, 30, IST) == []


def test_partial_trailing_slot_is_dropped():
    sched = [SimpleNamespace(weekday=0, start_time=time(9), end_time=time(10, 15))]
    assert len(generate_slots(date(2030, 1, 7), sched, 30, IST)) == 2
