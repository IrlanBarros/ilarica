# Usa uma imagem oficial do Node.js
FROM node:20-alpine

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de configuração de pacotes
COPY package.json package-lock.json* ./

# Instala as dependências
RUN npm install

# Copia o restante do código
COPY . .

# Expõe a porta padrão do Vite
EXPOSE 5173

# Roda o servidor de desenvolvimento expondo para a rede do Docker
CMD ["npm", "run", "dev", "--", "--host"]