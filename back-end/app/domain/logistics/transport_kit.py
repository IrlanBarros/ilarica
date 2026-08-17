"""Logistics and operations context: transport kit entity."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import TransportKitAlreadyAllocatedError, TransportKitNotAllocatedError


@dataclass
class TransportKit:
    """Entity representing the deliverable kit assigned to a courier."""

    id: str
    kit_code: str
    assigned_courier_id: str | None = None
    status: str = "available"

    def allocateToCourier(self, courierId: str) -> str:
        """Allocate the kit to a courier."""
        if self.assigned_courier_id is not None:
            raise TransportKitAlreadyAllocatedError("This transport kit has already been assigned to a courier.")

        self.assigned_courier_id = courierId
        self.status = "in_use"
        return self.status

    def registerReturn(self) -> str:
        """Return the kit to the general pool."""
        if self.assigned_courier_id is None:
            raise TransportKitNotAllocatedError("This transport kit must be allocated before it can be returned.")

        self.assigned_courier_id = None
        self.status = "returned"
        return self.status
