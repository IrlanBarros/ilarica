from sqlalchemy.orm import Session

from scripts.seed import create_drop_off_zones


EXPECTED_MACRO_ZONES = {
    *(f"Bloco {letter}" for letter in "ABCDEFGHIJKLMN"),
    "Bloco R",
    "Mirante",
    "Quadra 1",
    "Quadra 2",
}


def test_seed_creates_only_the_fixed_campus_macro_zones(db_session: Session) -> None:
    zones = create_drop_off_zones(db_session)

    assert {zone.name for zone in zones} == EXPECTED_MACRO_ZONES
    assert len(zones) == len(EXPECTED_MACRO_ZONES)
    assert all(zone.is_active for zone in zones)
