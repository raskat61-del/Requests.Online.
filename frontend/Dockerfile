FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы
COPY . .

# Открываем порт
EXPOSE 3000

# Запускаем в development режиме
CMD ["npm", "run", "dev", "--", "--host"]