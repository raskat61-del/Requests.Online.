# Analytics Bot - Comprehensive Data Collection & Analysis Platform

## Быстрый API тест

Вы можете протестировать API следующим образом:

### 1. Запуск системы

```bash
# Клонируем репозиторий
git clone https://github.com/raskat61-del/Requests.Online.
cd Requests.Online.

# Запускаем через Docker Compose
docker-compose up -d
```

### 2. Тест подключения

```bash
# Проверяем здоровье API
curl http://localhost:8000/health

# Регистрируем пользователя
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Авторизуемся
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# Создаем проект
curl -X POST "http://localhost:8000/api/v1/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing analytics capabilities"
  }'
```

### 3. Доступ к документации

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000

## Возможности

✅ **Мультиисточниковый сбор данных**
- Google Search API
- Yandex Search API  
- Telegram каналы
- VKontakte API
- Reddit API
- Веб-форумы

✅ **Продвинутая аналитика**
- Анализ тональности (русский/английский)
- Кластеризация тем
- Извлечение ключевых слов
- Выявление болевых точек

✅ **Гибкие отчеты**
- PDF с графиками
- Excel таблицы
- Интерактивные дашборды
- JSON экспорт

✅ **Enterprise готовность**
- JWT авторизация
- Rate limiting
- Docker контейнеризация
- Horizontal scaling
- Comprehensive testing

## Архитектура

```
Nginx → React Frontend → FastAPI Backend → PostgreSQL
                    ↓
                Redis + Celery Workers
                    ↓
            External APIs & Scrapers
```

## Лицензия

MIT License - свободное использование для коммерческих и некоммерческих проектов.