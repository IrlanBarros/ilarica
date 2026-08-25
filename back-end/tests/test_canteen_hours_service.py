from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.services.canteen_hours_service import (
    is_canteen_accepting_orders,
    next_canteen_opening,
)

FORTALEZA = ZoneInfo("America/Fortaleza")


def test_schedule_allows_orders_only_inside_business_hours() -> None:
    canteen = SimpleNamespace(
        is_open=True,
        opening_hours=[
            {"day": "weekdays", "opens_at": "08:00", "closes_at": "18:00", "is_open": True}
        ],
    )

    assert is_canteen_accepting_orders(
        canteen, now=datetime(2026, 8, 24, 12, 0, tzinfo=FORTALEZA)
    )
    assert not is_canteen_accepting_orders(
        canteen, now=datetime(2026, 8, 24, 19, 0, tzinfo=FORTALEZA)
    )


def test_manual_pause_overrides_schedule_and_next_opening_is_calculated() -> None:
    canteen = SimpleNamespace(
        is_open=False,
        opening_hours=[
            {"day": "weekdays", "opens_at": "08:00", "closes_at": "18:00", "is_open": True},
            {"day": "saturday", "opens_at": "09:00", "closes_at": "13:00", "is_open": True},
            {"day": "sunday", "opens_at": "09:00", "closes_at": "13:00", "is_open": False},
        ],
    )

    now = datetime(2026, 8, 24, 19, 0, tzinfo=FORTALEZA)
    assert not is_canteen_accepting_orders(canteen, now=now)
    assert next_canteen_opening(canteen, now=now) == datetime(
        2026, 8, 25, 8, 0, tzinfo=FORTALEZA
    )
