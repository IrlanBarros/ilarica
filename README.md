# iLarica

Projeto com arquitetura orientada a dominio usando FastAPI no backend, React + Vite no frontend e infraestrutura com PostgreSQL, Redis, Nginx e Docker Compose.

## Requisitos

- Docker
- Docker Compose

Verificacao:

```bash
docker --version
docker compose version
```

## Estrutura de Compose

- `docker-compose.yaml`: servicos base (`db`, `cache`)
- `docker-compose.dev.yaml`: ambiente de desenvolvimento (`backend`, `frontend`, `nginx`)
- `docker-compose.prod.yaml`: ambiente de producao

## Configuracao de ambiente

1. Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

2. Ajuste os valores no `.env` para sua maquina.

Importante: nunca comite `.env`.

## Subir em desenvolvimento

Na raiz do projeto:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up --build -d
```

Parar:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down
```

Resetar volumes de dados locais:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml down -v
```

## Endpoints locais

- Frontend: `http://localhost:5173`
- API FastAPI: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Nginx: `http://localhost:8080`

## Seed de dados

Com os servicos em execucao, rode:

```bash
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml exec -T backend python scripts/seed.py
```

O seed cria usuarios de teste, wallets, cantinas, produtos e pedidos.

## Testes

Para rodar os testes do backend localmente:

```bash
cd back-end
PYTHONPATH=. pytest -q
```

## Qualidade de codigo (local)

Para validar localmente os mesmos gates principais do CI:

```bash
cd back-end
ruff check app tests scripts
mypy app
```

## CI

Pipeline GitHub Actions em `.github/workflows/ci.yml` com:

- lint (`ruff`)
- type-check (`mypy`)
- testes (`pytest`)
- PostgreSQL 15 como service container
- upload de artefatos de teste (`coverage.xml` e `pytest-report.xml`)