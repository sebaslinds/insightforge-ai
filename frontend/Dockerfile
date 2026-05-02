# Stage 1: Build
FROM node:20-slim AS builder

WORKDIR /app

# Dépendances
COPY package.json package-lock.json ./
RUN npm install

# Copier le code
COPY . .

# Variables d'environnement pour le build
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build Next.js
RUN npm run build

# Stage 2: Production
FROM node:20-slim AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copier les fichiers nécessaires depuis le builder
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

# Cloud Run injecte $PORT
CMD ["sh", "-c", "npm start -- -p ${PORT:-3000}"]
