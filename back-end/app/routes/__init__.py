"""API route registries for the iLarica backend."""

from app.routes.auth_routes import router as auth_router
from app.routes.canteen_routes import router as canteen_router
from app.routes.delivery_ride_routes import router as delivery_ride_router
from app.routes.drop_off_zone_routes import router as drop_off_zone_router
from app.routes.invitation_key_routes import router as invitation_key_router
from app.routes.order_routes import router as order_router
from app.routes.payment_transaction_routes import router as payment_transaction_router
from app.routes.product_routes import router as product_router
from app.routes.transport_kit_routes import router as transport_kit_router
from app.routes.user_routes import router as user_router
from app.routes.wallet_routes import router as wallet_router

__all__ = [
    "auth_router",
    "user_router",
    "product_router",
    "order_router",
    "canteen_router",
    "wallet_router",
    "invitation_key_router",
    "drop_off_zone_router",
    "delivery_ride_router",
    "payment_transaction_router",
    "transport_kit_router",
]
