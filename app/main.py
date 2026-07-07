from fastapi import FastAPI

app = FastAPI(title="iLarica API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Infraestrutura iLarica operando com sucesso!"}