from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.use_cases.checkout_order import CheckoutOrderUseCase
from app.domain.exceptions import ZoneAtCapacityError
from app.domain.logistics.drop_off_zone import DropOffZone
from app.domain.order.order import Order
from app.domain.order.order_item import OrderItem


@pytest.fixture
def session() -> MagicMock:
    return MagicMock()


@pytest.fixture
def product_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def zone_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def order_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def wallet_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def valid_order_item() -> OrderItem:
    return OrderItem(
        product_id="p-1",
        product_name="Rice Bowl",
        quantity=1,
        unit_price=Decimal("12.50"),
    )


def test_checkout_use_case_creates_paid_order_and_charges_wallet(
    session: MagicMock,
    order_repository: MagicMock,
    zone_repository: MagicMock,
    product_repository: MagicMock,
    wallet_repository: MagicMock,
    valid_order_item: OrderItem,
) -> None:
    zone = DropOffZone(id="zone-1", name="North Gate", capacity_total=5)
    wallet = MagicMock()
    zone_repository.get_by_id.return_value = zone
    wallet_repository.get_by_user_id.return_value = wallet
    product_repository.get_by_id.return_value = MagicMock(id="p-1", is_active=True)
    order_repository.add.side_effect = lambda order: order

    use_case = CheckoutOrderUseCase(
        session=session,
        order_repository=order_repository,
        drop_off_zone_repository=zone_repository,
        product_repository=product_repository,
        wallet_repository=wallet_repository,
    )

    result = use_case.execute("user-1", "zone-1", [valid_order_item], order_id="order-1")

    assert result.status == Order.STATUS_PAID
    assert result.is_paid is True
    assert result.total() == Decimal("12.50")
    assert result.total_with_delivery() == Decimal("17.50")
    assert zone.current_load == 1
    wallet.debitOrderAmount.assert_called_once_with(Decimal("17.50"))
    order_repository.add.assert_called_once()
    zone_repository.save.assert_called_once_with(zone)
    wallet_repository.save.assert_called_once_with(wallet)
    session.commit.assert_called_once_with()


def test_checkout_use_case_rejects_missing_zone(
    session: MagicMock,
    order_repository: MagicMock,
    zone_repository: MagicMock,
    product_repository: MagicMock,
    wallet_repository: MagicMock,
    valid_order_item: OrderItem,
) -> None:
    zone_repository.get_by_id.return_value = None
    use_case = CheckoutOrderUseCase(
        session=session,
        order_repository=order_repository,
        drop_off_zone_repository=zone_repository,
        product_repository=product_repository,
        wallet_repository=wallet_repository,
    )

    with pytest.raises(ValueError, match="drop-off zone does not exist"):
        use_case.execute("user-1", "zone-1", [valid_order_item])


def test_checkout_use_case_rejects_full_zone(
    session: MagicMock,
    order_repository: MagicMock,
    zone_repository: MagicMock,
    product_repository: MagicMock,
    wallet_repository: MagicMock,
    valid_order_item: OrderItem,
) -> None:
    zone = DropOffZone(id="zone-1", name="North Gate", capacity_total=1, current_load=1)
    wallet = MagicMock()
    zone_repository.get_by_id.return_value = zone
    wallet_repository.get_by_user_id.return_value = wallet
    product_repository.get_by_id.return_value = MagicMock(id="p-1", is_active=True)
    order_repository.add.side_effect = lambda order: order

    use_case = CheckoutOrderUseCase(
        session=session,
        order_repository=order_repository,
        drop_off_zone_repository=zone_repository,
        product_repository=product_repository,
        wallet_repository=wallet_repository,
    )

    with pytest.raises(ZoneAtCapacityError, match="Not enough capacity"):
        use_case.execute("user-1", "zone-1", [valid_order_item])
    session.rollback.assert_called_once_with()
