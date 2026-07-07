# 🍽️ iLarica

Projeto em desenvolvimento utilizando FastAPI, PostgreSQL, Redis e Nginx com Docker.

## ✅ Pré-requisitos

Antes de rodar o projeto, tenha instalado na máquina:

- Git
- Docker
- Docker Compose

Para verificar se está tudo instalado:

```bash
git --version
docker --version
docker compose version
```

## 📥 Como clonar o projeto

Clone o repositório:

```bash
git clone LINK_DO_REPOSITORIO_AQUI
```

Entre na pasta do projeto:

```bash
cd NOME_DA_PASTA_DO_PROJETO
```

## ⚙️ Configuração do ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
DB_USER=ilarica_user
DB_PASSWORD=ilarica_pass
DB_NAME=ilarica_db
```

Esses valores são usados apenas para o ambiente de desenvolvimento local.

## 🚀 Como subir o projeto

Na raiz do projeto, execute:

```bash
docker compose up --build
```

Esse comando irá criar e iniciar os containers da aplicação, banco de dados, Redis e Nginx.

## 🌐 Acessando a aplicação

Após subir os containers, acesse no navegador:

```text
http://localhost:8080
```

Também é possível acessar diretamente a aplicação FastAPI em:

```text
http://localhost:8000
```

## 📦 Verificar containers em execução

Para conferir se os containers estão rodando:

```bash
docker compose ps
```

## 🧾 Ver logs da aplicação

Para acompanhar os logs de todos os serviços:

```bash
docker compose logs -f
```

Ou apenas os logs da aplicação:

```bash
docker compose logs -f app
```

## 🛑 Parar o projeto

Para parar os containers:

```bash
docker compose down
```

## ♻️ Resetar o banco de dados

Caso seja necessário apagar os dados locais e recriar os volumes:

```bash
docker compose down -v
```

Depois suba novamente:

```bash
docker compose up --build
```

## ⚠️ Observações importantes

- Não envie o arquivo `.env` para o GitHub.
- O arquivo `.env` deve ser criado manualmente por cada pessoa que clonar o projeto.
- Certifique-se de que as portas `8080`, `8000`, `5432` e `6379` não estejam sendo usadas por outros serviços.
- O projeto está configurado para desenvolvimento, com recarregamento automático da aplicação.