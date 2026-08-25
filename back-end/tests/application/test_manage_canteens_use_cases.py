from __future__ import annotations

from unittest.mock import MagicMock

from app.application.use_cases.manage_canteens import CreateCanteenUseCase, UpdateCanteenUseCase
from app.domain.catalog.canteen import Canteen


def test_create_canteen_use_case_passes_valid_domain_entity_to_repository() -> None:
    repository = MagicMock()
    repository.add.side_effect = lambda canteen: canteen

    result = CreateCanteenUseCase(repository).execute(
        user_id="user-1",
        name="  Cantina Central ",
        location=" Campus Juazeiro ",
        is_open=True,
    )

    assert result.name == "Cantina Central"
    assert result.location == "Campus Juazeiro"
    assert result.is_open is True
    repository.add.assert_called_once_with(result)


def test_update_canteen_use_case_persists_name_location_and_status() -> None:
    canteen = Canteen(
        id="canteen-1",
        user_id="user-1",
        name="Cantina Central",
        location="Campus Juazeiro",
    )
    repository = MagicMock()
    repository.get_by_id.return_value = canteen
    repository.save.side_effect = lambda updated: updated

    result = UpdateCanteenUseCase(repository).execute(
        "canteen-1",
        name="Cantina do Bloco B",
        location="Bloco B",
        is_open=True,
    )

    assert result is not None
    assert result.name == "Cantina do Bloco B"
    assert result.location == "Bloco B"
    assert result.is_open is True
    repository.save.assert_called_once_with(canteen)
