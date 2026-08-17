"""Strategy objects for delivery-related monetary calculations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


class DeliveryFeeStrategy(ABC):
    """Strategy contract for delivery fee calculation."""

    @abstractmethod
    def calculate(self, order_total: Decimal) -> Decimal:
        """Return the delivery fee for the given order subtotal."""


class CanteenCommissionStrategy(ABC):
    """Strategy contract for canteen commission calculation."""

    @abstractmethod
    def calculate(self, order_total: Decimal) -> Decimal:
        """Return the canteen commission for the given order subtotal."""


class CourierRewardStrategy(ABC):
    """Strategy contract for courier reward calculation."""

    @abstractmethod
    def calculate(self, order_total: Decimal, delivery_fee: Decimal) -> Decimal:
        """Return the courier reward for the delivery."""


class StandardFeeStrategy(DeliveryFeeStrategy):
    """Default delivery fee strategy used during regular operation hours."""

    def __init__(self, flat_fee: Decimal = Decimal("5.00")) -> None:
        self.flat_fee = _money(flat_fee)

    def calculate(self, order_total: Decimal) -> Decimal:
        _ = order_total
        return self.flat_fee


class NightShiftFeeStrategy(DeliveryFeeStrategy):
    """Delivery fee strategy with night surcharge."""

    def __init__(self, flat_fee: Decimal = Decimal("7.50"), surcharge_rate: Decimal = Decimal("0.05")) -> None:
        self.flat_fee = _money(flat_fee)
        self.surcharge_rate = surcharge_rate

    def calculate(self, order_total: Decimal) -> Decimal:
        surcharge = order_total * self.surcharge_rate
        return _money(self.flat_fee + surcharge)


class StandardCommissionStrategy(CanteenCommissionStrategy):
    """Commission strategy for daytime cafeteria orders."""

    def __init__(self, rate: Decimal = Decimal("0.10")) -> None:
        self.rate = rate

    def calculate(self, order_total: Decimal) -> Decimal:
        return _money(order_total * self.rate)


class NightShiftCommissionStrategy(CanteenCommissionStrategy):
    """Commission strategy with a slightly higher operational rate at night."""

    def __init__(self, rate: Decimal = Decimal("0.12")) -> None:
        self.rate = rate

    def calculate(self, order_total: Decimal) -> Decimal:
        return _money(order_total * self.rate)


class StandardCourierRewardStrategy(CourierRewardStrategy):
    """Default courier reward strategy based on delivery fee sharing."""

    def __init__(self, share_rate: Decimal = Decimal("0.80"), minimum_reward: Decimal = Decimal("4.00")) -> None:
        self.share_rate = share_rate
        self.minimum_reward = _money(minimum_reward)

    def calculate(self, order_total: Decimal, delivery_fee: Decimal) -> Decimal:
        _ = order_total
        reward = delivery_fee * self.share_rate
        return _money(reward if reward >= self.minimum_reward else self.minimum_reward)


class NightShiftCourierRewardStrategy(CourierRewardStrategy):
    """Courier reward strategy that prioritizes night-shift incentives."""

    def __init__(self, share_rate: Decimal = Decimal("1.00"), minimum_reward: Decimal = Decimal("6.00")) -> None:
        self.share_rate = share_rate
        self.minimum_reward = _money(minimum_reward)

    def calculate(self, order_total: Decimal, delivery_fee: Decimal) -> Decimal:
        _ = order_total
        reward = delivery_fee * self.share_rate
        return _money(reward if reward >= self.minimum_reward else self.minimum_reward)
