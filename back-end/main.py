import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.routes import (
    auth_router,
    canteen_router,
    delivery_ride_router,
    drop_off_zone_router,
    invitation_key_router,
    order_router,
    payment_transaction_router,
    product_router,
    transport_kit_router,
    user_router,
    wallet_router,
)

app = FastAPI(
    title="iLarica API",
    description="Backend do iLarica - Web App de delivery colaborativo universitário",
    version="0.1.0",
)

logger = logging.getLogger(__name__)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures without exposing internals to API clients."""
    logger.exception("Unhandled API error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# CORS configuration: read allowed origins from environment (comma-separated)
_env_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(canteen_router)
app.include_router(wallet_router)
app.include_router(invitation_key_router)
app.include_router(drop_off_zone_router)
app.include_router(delivery_ride_router)
app.include_router(payment_transaction_router)
app.include_router(transport_kit_router)

@app.get("/", include_in_schema=False)
def root():
    """Redireciona a raiz da API direto para a documentação."""
    return RedirectResponse(url="/docs")

@app.get("/ping", status_code=200)
def ping() -> dict[str, str]:
    """Rota de teste para verificar se a API está no ar."""
    return {"status": "pong"}
