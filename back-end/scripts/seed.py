#!/usr/bin/env python3
"""Seed the PostgreSQL database with realistic dummy data for the iLarica app."""
# ruff: noqa: E402

from __future__ import annotations

import random
import sys
from pathlib import Path
from uuid import uuid4

from faker import Faker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.security import get_password_hash
from app.database.base import Base
from app.database.models import (
    CanteenModel,
    DropOffZoneModel,
    OrderItemModel,
    OrderModel,
    ProductModel,
    UserModel,
    WalletModel,
)
from app.database.session import SessionLocal, engine

fake = Faker("pt_BR")
DEFAULT_PASSWORD = "Password123!"


def print_step(title: str) -> None:
    print(f"\n\033[1;36m==> {title}\033[0m")


def print_success(message: str) -> None:
    print(f"\033[1;32m{message}\033[0m")


def create_base_users_and_wallets(session) -> tuple[list[UserModel], list[UserModel]]:
    """Step 1 - Create customers and delivery personnel, then assign a wallet to each."""
    print_step("Step 1/4: creating base users and linked wallets...")
    customers: list[UserModel] = []
    delivery_personnel: list[UserModel] = []

    try:
        # 5 customers
        for index in range(5):
            user = UserModel(
                id=uuid4(),
                name=fake.name(),
                email=fake.unique.email(),
                whatsapp=f"558899990{index:04d}",
                password_hash=get_password_hash(DEFAULT_PASSWORD),
                role_type="customer",
                is_email_validated=True,
            )
            session.add(user)
            customers.append(user)

        # 3 delivery personnel
        for index in range(3):
            user = UserModel(
                id=uuid4(),
                name=fake.name(),
                email=fake.unique.email(),
                whatsapp=f"558899991{index:04d}",
                password_hash=get_password_hash(DEFAULT_PASSWORD),
                role_type="courier",
                is_email_validated=True,
            )
            session.add(user)
            delivery_personnel.append(user)

        session.flush()

        for user in customers + delivery_personnel:
            wallet = WalletModel(
                id=uuid4(),
                user_id=user.id,
                available_balance=float(fake.random_int(min=100, max=800)),
            )
            session.add(wallet)

        session.commit()
        print_success(f"Created {len(customers)} customers, {len(delivery_personnel)} delivery personnel, and {len(customers) + len(delivery_personnel)} wallets successfully.")
        return customers, delivery_personnel
    except Exception as exc:  # pragma: no cover - runtime seeding guard
        session.rollback()
        print(f"\033[1;31mError while creating base users and wallets: {exc}\033[0m")
        raise


def create_canteen_owners_and_canteens(session) -> list[CanteenModel]:
    """Step 2 - Create canteen owners and then create canteens linked to them."""
    print_step("Step 2/4: creating canteen owners and canteens...")
    canteens: list[CanteenModel] = []

    try:
        owners: list[UserModel] = []
        for index in range(3):
            owner = UserModel(
                id=uuid4(),
                name=fake.name(),
                email=fake.unique.email(),
                whatsapp=f"558899992{index:04d}",
                password_hash=get_password_hash(DEFAULT_PASSWORD),
                role_type="canteen_staff",
                is_email_validated=True,
            )
            session.add(owner)
            owners.append(owner)

        session.flush()

        for owner in owners:
            canteen = CanteenModel(
                id=uuid4(),
                user_id=owner.id,
                is_open=True,
            )
            session.add(canteen)
            canteens.append(canteen)

        session.commit()
        print_success(f"Created {len(owners)} canteen owners and {len(canteens)} canteens successfully.")
        return canteens
    except Exception as exc:  # pragma: no cover - runtime seeding guard
        session.rollback()
        print(f"\033[1;31mError while creating canteen owners and canteens: {exc}\033[0m")
        raise


def create_products_for_canteens(session, canteens: list[CanteenModel]) -> list[ProductModel]:
    """Step 3 - Create products (snacks, drinks, meals) for every canteen."""
    print_step("Step 3/4: creating products for each canteen...")
    created_products: list[ProductModel] = []

    try:
        product_templates = [
            ("Coxinha", "snack", 8.50),
            ("Pastel de Queijo", "snack", 9.00),
            ("Pão de Queijo", "snack", 6.00),
            ("Suco de Laranja", "drink", 6.50),
            ("Refrigerante Lata", "drink", 7.00),
            ("Água Mineral", "drink", 4.50),
            ("Arroz com Feijão", "meal", 18.00),
            ("Frango Grelhado", "meal", 22.50),
            ("Salada Tropical", "meal", 16.00),
        ]

        for canteen in canteens:
            for product_name, category, base_price in product_templates:
                product = ProductModel(
                    id=uuid4(),
                    canteen_id=canteen.id,
                    name=product_name,
                    description=(
                        f"{category.capitalize()} preparado com ingredientes frescos. "
                        f"Imagem de referência: {fake.image_url(width=800, height=600)}"
                    ),
                    price=float(base_price + random.uniform(-0.5, 2.5)),
                    is_fast_stock_enabled=random.choice([True, False]),
                    is_active=True,
                )
                session.add(product)
                created_products.append(product)

        session.commit()
        print_success(f"Created {len(created_products)} products across all canteens.")
        return created_products
    except Exception as exc:  # pragma: no cover - runtime seeding guard
        session.rollback()
        print(f"\033[1;31mError while creating products: {exc}\033[0m")
        raise


def create_drop_off_zones(session) -> list[DropOffZoneModel]:
    """Create physical drop-off zones where students can receive orders."""
    print_step("Creating delivery drop-off zones...")
    zones: list[DropOffZoneModel] = []

    try:
        for zone_name in ["Bloco A", "Biblioteca Central", "Praça do Campus", "Residência Norte"]:
            zone = DropOffZoneModel(
                id=uuid4(),
                name=zone_name,
                description=f"Zona de entrega para {zone_name.lower()}.",
                capacity=random.randint(12, 30),
                is_active=True,
            )
            session.add(zone)
            zones.append(zone)

        session.commit()
        print_success(f"Created {len(zones)} drop-off zones successfully.")
        return zones
    except Exception as exc:  # pragma: no cover - runtime seeding guard
        session.rollback()
        print(f"\033[1;31mError while creating drop-off zones: {exc}\033[0m")
        raise


def create_orders(session, customer_users: list[UserModel], canteens: list[CanteenModel], products: list[ProductModel], zones: list[DropOffZoneModel]) -> None:
    """Step 4 - Create orders with different statuses and link them to a user, canteen, and products."""
    print_step("Step 4/4: creating orders with different statuses and order items...")
    try:
        order_statuses = ["pending", "preparing", "completed"]

        for index in range(12):
            customer = random.choice(customer_users)
            canteen = random.choice(canteens)
            zone = random.choice(zones)
            chosen_products = random.sample(products, k=random.randint(2, 4))
            status = order_statuses[index % len(order_statuses)]

            order = OrderModel(
                id=uuid4(),
                customer_id=customer.id,
                canteen_id=canteen.id,
                drop_off_zone_id=zone.id,
                status=status,
                total_amount=0.0,
                pickup_pin=str(random.randint(1000, 9999)) if status == "completed" else None,
            )
            session.add(order)
            session.flush()

            subtotal = 0.0
            for product in chosen_products:
                quantity = random.randint(1, 3)
                item = OrderItemModel(
                    id=uuid4(),
                    order_id=order.id,
                    product_id=product.id,
                    unit_price=float(product.price),
                    quantity=quantity,
                )
                session.add(item)
                subtotal += float(product.price) * quantity

            order.total_amount = round(subtotal, 2)

        session.commit()
        print_success("Created 12 orders with statuses pending/preparing/completed and linked order items successfully.")
    except Exception as exc:  # pragma: no cover - runtime seeding guard
        session.rollback()
        print(f"\033[1;31mError while creating orders: {exc}\033[0m")
        raise


def seed_database() -> None:
    """Run the full seeding flow, step by step, with rollback safety."""
    print("\n\033[1;33mStarting iLarica database seeding...\033[0m")
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        customers, _ = create_base_users_and_wallets(session)
        canteens = create_canteen_owners_and_canteens(session)
        products = create_products_for_canteens(session, canteens)
        zones = create_drop_off_zones(session)
        create_orders(session, customers, canteens, products, zones)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print("\n\033[1;32mSeeding completed successfully!\033[0m")


if __name__ == "__main__":
    seed_database()
