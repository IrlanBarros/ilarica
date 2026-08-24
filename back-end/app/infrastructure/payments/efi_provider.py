"""Efí Pix API adapter using OAuth2 and mutual TLS."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import httpx

from app.application.ports.payment_provider import PaymentProvider, PixCharge, PixChargeStatus


class PaymentProviderError(RuntimeError):
    """Safe infrastructure failure that must not expose provider credentials."""


class EfiPixProvider(PaymentProvider):
    name = "efi"

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        certificate_path: str,
        private_key_path: str,
        pix_key: str,
        base_url: str = "https://pix-h.api.efipay.com.br",
        timeout_seconds: float = 15.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not all((client_id, client_secret, certificate_path, private_key_path, pix_key)):
            raise ValueError("Efí credentials, PEM certificate/private key and Pix key are required")
        self.client_id = client_id
        self.client_secret = client_secret
        self.pix_key = pix_key
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(
            base_url=self.base_url,
            cert=(certificate_path, private_key_path),
            timeout=timeout_seconds,
            headers={"Accept": "application/json", "Accept-Encoding": "identity"},
        )
        self._access_token: str | None = None
        self._token_expires_at = datetime.min.replace(tzinfo=timezone.utc)
        self._token_lock = threading.Lock()

    def _token(self) -> str:
        now = datetime.now(timezone.utc)
        with self._token_lock:
            if self._access_token and now < self._token_expires_at:
                return self._access_token
            try:
                response = self.client.post(
                    "/oauth/token",
                    auth=(self.client_id, self.client_secret),
                    json={"grant_type": "client_credentials"},
                )
                response.raise_for_status()
                payload = response.json()
                self._access_token = str(payload["access_token"])
                lifetime = max(60, int(payload.get("expires_in", 300)) - 30)
                self._token_expires_at = now + timedelta(seconds=lifetime)
                return self._access_token
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                raise PaymentProviderError("Unable to authenticate with Efí Pix") from exc

    def _request(self, method: str, path: str, **kwargs) -> dict:
        try:
            response = self.client.request(
                method, path, headers={"Authorization": f"Bearer {self._token()}"}, **kwargs
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, TypeError, ValueError) as exc:
            raise PaymentProviderError("Efí Pix request failed") from exc

    def create_pix_charge(
        self, *, reference: str, amount: Decimal, expiration_seconds: int, order_id: str
    ) -> PixCharge:
        payload = self._request(
            "PUT",
            f"/v2/cob/{reference}",
            json={
                "calendario": {"expiracao": expiration_seconds},
                "valor": {"original": f"{amount:.2f}"},
                "chave": self.pix_key,
                "solicitacaoPagador": f"Pedido iLarica {order_id}",
            },
        )
        try:
            created_at = datetime.fromisoformat(
                str(payload["calendario"]["criacao"]).replace("Z", "+00:00")
            )
            expiration = int(payload["calendario"]["expiracao"])
            return PixCharge(
                reference=str(payload["txid"]),
                copy_paste=str(payload["pixCopiaECola"]),
                expires_at=created_at + timedelta(seconds=expiration),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PaymentProviderError("Efí returned an invalid Pix charge contract") from exc

    def get_pix_charge(self, reference: str) -> PixChargeStatus:
        payload = self._request("GET", f"/v2/cob/{reference}")
        provider_status = str(payload.get("status", "")).upper()
        status = {
            "ATIVA": "pending",
            "CONCLUIDA": "succeeded",
            "REMOVIDA_PELO_USUARIO_RECEBEDOR": "failed",
            "REMOVIDA_PELO_PSP": "failed",
        }.get(provider_status, "pending")
        paid_amount = None
        if status == "succeeded":
            pix_entries = payload.get("pix") or []
            if pix_entries:
                paid_amount = Decimal(str(pix_entries[0].get("valor")))
        return PixChargeStatus(reference=reference, status=status, paid_amount=paid_amount)

    def configure_webhook(self, webhook_url: str) -> None:
        """Register the public HTTPS base URL; Efí appends `/pix` to callbacks."""
        if not webhook_url.startswith("https://"):
            raise ValueError("Efí webhook URL must use HTTPS")
        self._request(
            "PUT",
            f"/v2/webhook/{self.pix_key}",
            json={"webhookUrl": webhook_url.rstrip("/")},
        )
