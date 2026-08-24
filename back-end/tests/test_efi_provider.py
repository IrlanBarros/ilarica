from decimal import Decimal

import httpx

from app.infrastructure.payments.efi_provider import EfiPixProvider


def test_efi_adapter_uses_oauth_mtls_client_and_authoritative_status_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/oauth/token":
            return httpx.Response(200, json={"access_token": "sandbox-token", "expires_in": 300})
        if request.url.path.startswith("/v2/webhook/"):
            assert request.method == "PUT"
            assert "https://sandbox.example/api/payment-transactions/provider-webhooks/efi" in request.content.decode()
            return httpx.Response(200, json={})
        if request.method == "PUT":
            assert '"original":"9.50"' in request.content.decode()
            return httpx.Response(200, json={
                "calendario": {"criacao": "2026-08-24T13:00:00Z", "expiracao": 900},
                "txid": "a" * 32, "pixCopiaECola": "000201-provider-code", "status": "ATIVA",
            })
        return httpx.Response(200, json={
            "txid": "a" * 32, "status": "CONCLUIDA", "pix": [{"valor": "9.50"}],
        })

    client = httpx.Client(base_url="https://pix-h.api.efipay.com.br", transport=httpx.MockTransport(handler))
    provider = EfiPixProvider(
        client_id="client", client_secret="secret", certificate_path="cert.pem",
        private_key_path="key.pem", pix_key="pix-key", client=client,
    )
    charge = provider.create_pix_charge(reference="a" * 32, amount=Decimal("9.50"), expiration_seconds=900, order_id="order-1")
    status = provider.get_pix_charge(charge.reference)
    provider.configure_webhook("https://sandbox.example/api/payment-transactions/provider-webhooks/efi")

    assert charge.copy_paste == "000201-provider-code"
    assert status.status == "succeeded"
    assert status.paid_amount == Decimal("9.50")
    assert len([request for request in requests if request.url.path == "/oauth/token"]) == 1
    assert all("client" not in request.url.query.decode() for request in requests)
