"""Transactional use case for accepting a delivery ride in the logistics context."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.ports.repositories import IDeliveryRideRepository, IOrderRepository
from app.domain.exceptions import DeliveryRideOrderMismatchError
from app.domain.logistics.delivery_ride import DeliveryRide


@dataclass
class AcceptDeliveryUseCase:
    """Assign a queued delivery to a courier and transition the order to in transit."""

    session: Session
    delivery_ride_repository: IDeliveryRideRepository
    order_repository: IOrderRepository

    def execute(self, ride_id: str, courier_id: str, order_id: str | None = None) -> DeliveryRide:
        """Match a courier to a ride and atomically dispatch the related order."""
        if not ride_id:
            raise ValueError("A valid ride identifier is required.")
        if not courier_id:
            raise ValueError("A valid courier identifier is required.")

        ride = self.delivery_ride_repository.get_by_id(ride_id)
        if ride is None:
            raise ValueError("The delivery ride does not exist.")

        resolved_order_id = order_id or ride.order_id
        if not resolved_order_id:
            raise DeliveryRideOrderMismatchError("The delivery ride is not linked to an order.")

        order = self.order_repository.get_by_id(resolved_order_id)
        if order is None:
            raise ValueError("The order associated with this delivery ride does not exist.")

        try:
            if ride.status == "draft":
                ride.publish_to_queue()
            ride.accept_delivery(courier_id)
            order.attach_delivery_ride(ride.id)
            order.mark_as_in_transit()

            self.delivery_ride_repository.save(ride)
            self.order_repository.save(order)
            self.session.commit()
            return ride
        except Exception:
            self.session.rollback()
            raise
