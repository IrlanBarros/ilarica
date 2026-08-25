from __future__ import annotations

import pytest

from app.domain.catalog.canteen import Canteen


def test_canteen_normalizes_required_identity_fields() -> None:
    canteen = Canteen(
        id="canteen-1",
        user_id="user-1",
        name="  Cantina Central  ",
        location="  Campus Juazeiro  ",
    )

    assert canteen.name == "Cantina Central"
    assert canteen.location == "Campus Juazeiro"


@pytest.mark.parametrize(
    ("name", "location"),
    [(" ", "Campus Juazeiro"), ("Cantina Central", " ")],
)
def test_canteen_rejects_blank_identity_fields(name: str, location: str) -> None:
    with pytest.raises(ValueError):
        Canteen(id="canteen-1", user_id="user-1", name=name, location=location)


def test_canteen_profile_update_preserves_consistency() -> None:
    canteen = Canteen(
        id="canteen-1",
        user_id="user-1",
        name="Cantina Central",
        location="Campus Juazeiro",
    )

    canteen.update_profile(name="  Cantina do Bloco B ", location="  Bloco B ")

    assert canteen.name == "Cantina do Bloco B"
    assert canteen.location == "Bloco B"
