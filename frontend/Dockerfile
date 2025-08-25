# Используем Node.js для сборки и запуска React приложения
FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем libc6-compat для совместимости esbuild
RUN apk add --no-cache libc6-compat

# Копируем только package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости (включая dev зависимости для Vite)
RUN npm ci

# Копируем исходный код (исключая node_modules через .dockerignore)
COPY . .

# Открываем порт 3000
EXPOSE 3000

# Запускаем приложение в режиме разработки
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]