"""Authoritative evaluation of a canteen's operating schedule."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo

CAMPUS_TIMEZONE = ZoneInfo("America/Fortaleza")


class SchedulableCanteen(Protocol):
    is_open: bool
    opening_hours: list[dict[str, object]]


def _day_key(weekday: int) -> str:
    if weekday < 5:
        return "weekdays"
    return "saturday" if weekday == 5 else "sunday"


def _parse_time(value: object) -> time | None:
    if not isinstance(value, str):
        return None
    try:
        return time.fromisoformat(value)
    except ValueError:
        return None


def _entry_for(canteen: SchedulableCanteen, moment: datetime) -> dict[str, object] | None:
    key = _day_key(moment.weekday())
    return next((entry for entry in canteen.opening_hours if entry.get("day") == key), None)


def is_canteen_accepting_orders(
    canteen: SchedulableCanteen,
    *,
    now: datetime | None = None,
) -> bool:
    """Return whether both the manual switch and current schedule allow orders."""
    if not canteen.is_open:
        return False
    if not canteen.opening_hours:
        return True

    current = (now or datetime.now(CAMPUS_TIMEZONE)).astimezone(CAMPUS_TIMEZONE)
    entry = _entry_for(canteen, current)
    if not entry or not entry.get("is_open"):
        return False
    opens_at = _parse_time(entry.get("opens_at"))
    closes_at = _parse_time(entry.get("closes_at"))
    if opens_at is None or closes_at is None:
        return False
    current_time = current.time().replace(tzinfo=None)
    if opens_at <= closes_at:
        return opens_at <= current_time < closes_at
    return current_time >= opens_at or current_time < closes_at


def next_canteen_opening(
    canteen: SchedulableCanteen,
    *,
    now: datetime | None = None,
) -> datetime | None:
    """Find the next scheduled opening in campus local time."""
    if not canteen.opening_hours:
        return None
    current = (now or datetime.now(CAMPUS_TIMEZONE)).astimezone(CAMPUS_TIMEZONE)
    for offset in range(8):
        candidate_day = current.date() + timedelta(days=offset)
        probe = datetime.combine(candidate_day, time.min, CAMPUS_TIMEZONE)
        entry = _entry_for(canteen, probe)
        if not entry or not entry.get("is_open"):
            continue
        opens_at = _parse_time(entry.get("opens_at"))
        if opens_at is None:
            continue
        candidate = datetime.combine(candidate_day, opens_at, CAMPUS_TIMEZONE)
        if candidate > current:
            return candidate
    return None
