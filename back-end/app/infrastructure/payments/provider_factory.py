"""Backend-only payment provider composition from environment secrets."""

from functools import lru_cache
import os

from app.application.ports.payment_provider import PaymentProvider
from app.infrastructure.payments.efi_provider import EfiPixProvider
from app.infrastructure.payments.internal_provider import InternalPixProvider


@lru_cache(maxsize=1)
def get_payment_provider() -> PaymentProvider:
    provider = os.getenv("PAYMENT_PROVIDER", "internal").strip().lower()
    if provider == "internal":
        return InternalPixProvider()
    if provider != "efi":
        raise RuntimeError(f"Unsupported PAYMENT_PROVIDER: {provider}")
    return EfiPixProvider(
        client_id=os.environ["EFI_CLIENT_ID"],
        client_secret=os.environ["EFI_CLIENT_SECRET"],
        certificate_path=os.environ["EFI_CERTIFICATE_PATH"],
        private_key_path=os.environ["EFI_PRIVATE_KEY_PATH"],
        pix_key=os.environ["EFI_PIX_KEY"],
        base_url=os.getenv("EFI_API_BASE_URL", "https://pix-h.api.efipay.com.br"),
    )
