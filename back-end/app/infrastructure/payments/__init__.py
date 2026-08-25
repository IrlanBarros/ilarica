"""Payment provider adapters and composition root."""

from app.infrastructure.payments.provider_factory import get_payment_provider

__all__ = ["get_payment_provider"]
