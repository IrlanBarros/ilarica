"""Logistics and operations context: delivery ride entity."""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.exceptions import (
    DeliveryRideAlreadyAcceptedError,
    DeliveryRideAlreadyInTransitError,
    DeliveryRideNotAcceptedError,
    DeliveryRideNotQueuedError,
)


@dataclass
class DeliveryRide:
    """Delivery ride representing an assigned trip from the canteen to a drop-off zone."""

    id: str
    order_id: str | None = None
    drop_off_zone_id: str | None = None
    status: str = "draft"
    assigned_courier_id: str | None = None
    is_arrived: bool = False

    def publish_to_queue(self) -> str:
        """Publish the ride for courier assignment."""
        if self.status == "queued":
            return self.status
        if self.assigned_courier_id is not None:
            raise DeliveryRideAlreadyAcceptedError("The ride already has a courier assigned.")

        self.status = "queued"
        return self.status

    def accept_delivery(self, courier_id: str) -> str:
        """Assign the ride to a courier and move it to transit."""
        if self.status not in {"queued", "accepted"}:
            raise DeliveryRideNotQueuedError("This delivery is not queued for acceptance.")
        if self.assigned_courier_id is not None and self.assigned_courier_id != courier_id:
            raise DeliveryRideAlreadyAcceptedError("This delivery already has a courier assigned.")
        if self.status == "in_transit":
            raise DeliveryRideAlreadyInTransitError("This delivery ride is already in transit.")

        self.assigned_courier_id = courier_id
        self.status = "in_transit"
        return self.status

    def register_drop_off_arrival(self) -> bool:
        """Register the ride arrival to the drop-off zone."""
        if self.assigned_courier_id is None:
            raise DeliveryRideNotAcceptedError("The ride must be accepted by a courier before arrival is registered.")
        if self.status not in {"in_transit", "accepted"}:
            raise DeliveryRideNotAcceptedError("The ride must be in transit before arrival is registered.")

        self.is_arrived = True
        self.status = "arrived"
        return True

    def publishToQueue(self) -> str:
        return self.publish_to_queue()

    def acceptDelivery(self, courierId: str) -> str:
        return self.accept_delivery(courierId)

    def registerDropOffArrival(self) -> bool:
        return self.register_drop_off_arrival()
