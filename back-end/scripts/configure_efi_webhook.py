"""Register the Efí sandbox webhook without logging credentials."""

from __future__ import annotations

import os

from app.infrastructure.payments.efi_provider import EfiPixProvider
from app.infrastructure.payments.provider_factory import get_payment_provider


def main() -> None:
    provider = get_payment_provider()
    if not isinstance(provider, EfiPixProvider):
        raise RuntimeError("Set PAYMENT_PROVIDER=efi before configuring the webhook")
    webhook_url = os.environ["EFI_WEBHOOK_URL"]
    provider.configure_webhook(webhook_url)
    print("Efí Pix webhook configured successfully.")


if __name__ == "__main__":
    main()
