FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Impede a criação de arquivos .pyc e força o log no terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .