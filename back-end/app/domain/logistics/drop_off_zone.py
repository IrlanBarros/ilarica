"""Logistics and operations context: drop-off zone aggregate root."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import DropOffZoneAlreadyActiveError, ZoneAtCapacityError


@dataclass
class DropOffZone:
    """Aggregate root representing a physical drop-off zone."""

    id: str
    name: str
    capacity_total: int
    current_load: int = 0
    is_active: bool = False

    def activateZone(self) -> bool:
        """Activate the zone for usage."""
        if self.is_active:
            raise DropOffZoneAlreadyActiveError("The drop-off zone is already active.")

        self.is_active = True
        return True

    def checkCapacity(self) -> int:
        """Return remaining capacity or raise if the zone is full."""
        if self.current_load >= self.capacity_total:
            raise ZoneAtCapacityError("The drop-off zone is already at maximum capacity.")

        return self.capacity_total - self.current_load

    def addLoad(self, amount: int) -> int:
        """Register additional vehicles or loads in the zone."""
        if amount <= 0:
            raise ValueError("Load amount must be greater than zero.")
        if self.current_load + amount > self.capacity_total:
            raise ZoneAtCapacityError("Not enough capacity left in the drop-off zone.")

        self.current_load += amount
        return self.current_load
