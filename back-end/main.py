from fastapi import FastAPI

app = FastAPI(
    title="iLarica API",
    description="Backend do iLarica - Web App de delivery colaborativo universitário",
    version="0.1.0",
)


@app.get("/ping", status_code=200)
def ping() -> dict[str, str]:
    """Rota de teste para verificar se a API está no ar."""
    return {"status": "pong"}