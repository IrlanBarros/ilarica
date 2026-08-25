"""Application use cases for the canteen aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.application.ports.repositories import ICanteenRepository
from app.domain.catalog.canteen import Canteen


@dataclass
class CreateCanteenUseCase:
    canteen_repository: ICanteenRepository

    def execute(
        self, *, user_id: str, name: str, location: str,
        description: str | None = None, logo_url: str | None = None,
        is_open: bool = False,
    ) -> Canteen:
        canteen = Canteen(
            id=str(uuid4()),
            user_id=user_id,
            name=name,
            location=location,
            description=description,
            logo_url=logo_url,
            is_open=is_open,
        )
        return self.canteen_repository.add(canteen)


@dataclass
class GetCanteenUseCase:
    canteen_repository: ICanteenRepository

    def execute(self, canteen_id: str) -> Canteen | None:
        return self.canteen_repository.get_by_id(canteen_id)


@dataclass
class ListCanteensUseCase:
    canteen_repository: ICanteenRepository

    def execute(self) -> list[Canteen]:
        return self.canteen_repository.list_all()


@dataclass
class UpdateCanteenUseCase:
    canteen_repository: ICanteenRepository

    def execute(
        self,
        canteen_id: str,
        *,
        name: str | None = None,
        location: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
        is_open: bool | None = None,
        opening_hours: list[dict[str, object]] | None = None,
    ) -> Canteen | None:
        canteen = self.canteen_repository.get_by_id(canteen_id)
        if canteen is None:
            return None
        canteen.update_profile(name=name, location=location)
        if description is not None:
            canteen.description = description.strip() or None
        if logo_url is not None:
            canteen.logo_url = logo_url.strip() or None
        if is_open is not None:
            canteen.is_open = is_open
        if opening_hours is not None:
            canteen.opening_hours = opening_hours
        return self.canteen_repository.save(canteen)
