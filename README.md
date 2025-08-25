# Analytics Bot

Comprehensive Analytics Bot for collecting and analyzing data from multiple sources to identify pain points and unmet needs for SaaS product development.

## 🚀 Quick Start

### Windows Users
```bash
# Simply run the startup script
start.bat
```

### Linux/Mac Users
```bash
# Make the script executable and run
chmod +x start.sh
./start.sh
```

### Manual Setup

#### Backend Setup
```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

#### Database Setup
```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Or run the full stack
docker-compose up
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

## 📋 Features

### Data Collection
- **Search Engines**: Google Custom Search, Yandex Search API
- **Social Media**: Telegram channels, VKontakte, Reddit
- **Web Scraping**: Forums, websites, blogs
- **Real-time Processing**: Background task processing with Celery

### Text Analysis
- **Sentiment Analysis**: Multi-language support (Russian, English)
- **Topic Clustering**: Automatic grouping of similar content
- **Keyword Extraction**: TF-IDF and frequency analysis
- **Pain Point Detection**: AI-powered identification of user problems

### Report Generation
- **PDF Reports**: Professional formatted documents with charts
- **Excel Exports**: Detailed data tables and analysis
- **Real-time Dashboard**: Web-based analytics interface
- **Custom Visualizations**: Charts and graphs for insights

### User Management
- **Authentication**: JWT-based secure login system
- **Project Management**: Organize analysis by projects
- **Task Tracking**: Monitor data collection progress
- **Subscription Tiers**: Free and premium features

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database for structured data
- **Redis**: Caching and message broker
- **Celery**: Background task processing
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### Frontend Stack
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing

### Analysis Engine
- **spaCy**: Natural language processing
- **scikit-learn**: Machine learning algorithms
- **NLTK**: Text processing utilities
- **Dostoevsky**: Russian sentiment analysis
- **TextBlob**: English text analysis

## 📁 Project Structure

```
AnalyticsBot/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── collectors/     # Data collection modules
│   │   ├── analyzers/      # Text analysis engines
│   │   └── reports/        # Report generation
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── contexts/       # React contexts
│   │   ├── lib/            # Utilities and API client
│   │   └── utils/          # Helper functions
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── docker/                 # Docker configurations
├── docs/                   # Documentation
├── docker-compose.yml      # Multi-container setup
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/analytics_bot
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/analytics_bot

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GOOGLE_API_KEY=your-google-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
YANDEX_API_KEY=your-yandex-api-key
TELEGRAM_API_ID=your-telegram-api-id
TELEGRAM_API_HASH=your-telegram-api-hash
VK_ACCESS_TOKEN=your-vk-access-token
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# Application
APP_NAME=Analytics Bot
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### API Integration Test
```bash
# Test API connectivity
node -e "require('./frontend/src/utils/testAPI.ts').testAPIConnection()"
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run all services
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. **Backend**: Deploy to any Python hosting service
2. **Frontend**: Build and deploy to static hosting
3. **Database**: Set up PostgreSQL and Redis
4. **Environment**: Configure production environment variables

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

- `POST /api/v1/auth/login` - User authentication
- `GET /api/v1/projects` - List user projects
- `POST /api/v1/search` - Create search task
- `GET /api/v1/analysis/project/{id}` - Get analysis results
- `POST /api/v1/reports/generate` - Generate reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Review the [API documentation](http://localhost:8000/docs)
3. Create an issue in the GitHub repository

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the modern UI library
- All the open-source libraries that make this project possible

## Описание проекта

Бот-аналитик - это комплексная система для автоматического сбора, анализа и структурирования информации из различных источников (поисковые системы, социальные сети, форумы) с целью выявления болей, рутинных задач и неудовлетворенных потребностей специалистов различных профессий.

## Возможности

### MVP Функциональность
- 🔍 **Автоматизированный поиск** по ключевым словам
- 🌐 **Множественные источники данных**:
  - Google Search API
  - Yandex Search API  
  - Telegram каналы и группы
  - VKontakte (планируется)
  - Reddit (планируется)
  - Тематические форумы
- 📊 **Анализ данных**:
  - Кластеризация запросов
  - Частотный анализ
  - Анализ тональности
- 📄 **Генерация отчетов**: PDF, Excel, интерактивные дашборды
- 🔐 **Аутентификация и авторизация пользователей**
- 💎 **Система подписок** (Free, Basic, Premium)

## Технологический стек

### Backend
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - основная база данных
- **Redis** - кеширование и брокер сообщений
- **Celery** - асинхронные задачи
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД

### Data Processing
- **BeautifulSoup4** - парсинг HTML
- **Scrapy** - веб-скрапинг
- **Telethon** - Telegram API
- **spaCy** - обработка естественного языка
- **scikit-learn** - машинное обучение

### Infrastructure
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy
- **Gunicorn** - WSGI сервер

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git
- Минимум 4GB RAM

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd AnalyticsBot
```

### 2. Настройка переменных окружения

Скопируйте файл с примером настроек:

```bash
cp backend/.env.example backend/.env
```

Отредактируйте файл `backend/.env` и укажите ваши API ключи:

```env
# API ключи для поисковых систем
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
YANDEX_API_KEY=your-yandex-api-key

# API ключи для социальных сетей
TELEGRAM_API_ID=your-telegram-api-id
TELEGRAM_API_HASH=your-telegram-api-hash
VK_API_TOKEN=your-vk-api-token
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# Безопасность (ОБЯЗАТЕЛЬНО измените в продакшене!)
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Запуск с помощью Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

### 4. Проверка работоспособности

После запуска будут доступны следующие сервисы:

- **API документация**: http://localhost/docs
- **Frontend**: http://localhost
- **Adminer (управление БД)**: http://localhost:8080
- **Flower (мониторинг Celery)**: http://localhost:5555

## Получение API ключей

### Google Search API

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Custom Search API
4. Создайте учетные данные (API ключ)
5. Настройте Custom Search Engine на https://cse.google.com/

### Yandex Search API

1. Перейдите в [Yandex.Cloud](https://cloud.yandex.ru/)
2. Создайте сервисный аккаунт
3. Получите API ключ для Yandex Search API

### Telegram API

1. Перейдите на https://my.telegram.org/apps
2. Войдите с помощью номера телефона
3. Создайте новое приложение
4. Получите API ID и API Hash

## Использование API

### Аутентификация

```bash
# Регистрация
curl -X POST "http://localhost/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpassword123",
       "full_name": "Test User"
     }'

# Авторизация
curl -X POST "http://localhost/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword123"
```

### Создание проекта

```bash
curl -X POST "http://localhost/api/v1/projects/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Анализ IT рынка",
       "description": "Исследование болей разработчиков"
     }'
```

### Получение списка проектов

```bash
curl -X GET "http://localhost/api/v1/projects/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Разработка

### Структура проекта

```
AnalyticsBot/
├── backend/                 # Backend приложение (FastAPI)
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Основные настройки
│   │   ├── db/             # Конфигурация БД
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── services/       # Бизнес-логика
│   │   ├── collectors/     # Коллекторы данных
│   │   └── analyzers/      # Анализаторы текста
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Frontend приложение (React)
├── docker/                 # Docker конфигурации
├── docs/                   # Документация
├── tests/                  # Тесты
└── docker-compose.yml
```

### Запуск в режиме разработки

```bash
# Только база данных и Redis
docker-compose up -d postgres redis

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (в отдельном терминале)
cd frontend
npm install
npm start
```

### Миграции базы данных

```bash
# Создание миграции
alembic revision --autogenerate -m "Add new table"

# Применение миграций
alembic upgrade head
```

### Тестирование

```bash
# Запуск тестов
cd backend
pytest

# С покрытием кода
pytest --cov=app
```

## Мониторинг и логирование

### Логи

Логи доступны в следующих местах:

```bash
# API логи
docker-compose logs api

# Celery логи
docker-compose logs celery_worker

# Nginx логи
docker-compose logs nginx

# Логи в файлах
tail -f backend/logs/app.log
```

### Мониторинг Celery

Flower доступен по адресу http://localhost:5555 для мониторинга:
- Активные задачи
- Статистика воркеров
- История выполнения задач
- Метрики производительности

## Безопасность

### Рекомендации для продакшена

1. **Смените SECRET_KEY** в .env файле
2. **Используйте HTTPS** для всех соединений
3. **Настройте файрвол** для ограничения доступа к портам
4. **Регулярно обновляйте** зависимости
5. **Настройте backup** базы данных
6. **Используйте environment-specific** конфигурации

### Rate Limiting

API автоматически применяет ограничения:
- **Бесплатный план**: 100 запросов/день
- **Базовый план**: 500 запросов/день  
- **Премиум план**: 2000 запросов/день

## Troubleshooting

### Частые проблемы

**1. Ошибки подключения к БД**
```bash
# Проверьте статус контейнера
docker-compose ps postgres

# Перезапустите БД
docker-compose restart postgres
```

**2. Проблемы с API ключами**
```bash
# Проверьте настройки в .env
cat backend/.env | grep API_KEY

# Тестирование источников данных
curl http://localhost/api/v1/search/test-sources
```

**3. Celery воркеры не запускаются**
```bash
# Проверьте Redis
docker-compose logs redis

# Перезапустите воркеры
docker-compose restart celery_worker
```

## Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [документацию](./docs/)
2. Посмотрите [issues](../../issues)
3. Создайте новый issue с подробным описанием проблемы

## Лицензия

Этот проект лицензирован под MIT License. Подробности в файле [LICENSE](LICENSE).

## Дорожная карта

### Планируемые функции

- [ ] Интеграция с VKontakte API
- [ ] Интеграция с Reddit API
- [ ] Парсер веб-форумов
- [ ] Улучшенный анализ тональности для русского языка
- [ ] Система уведомлений
- [ ] Экспорт данных в различных форматах
- [ ] Интеграция с внешними системами аналитики
- [ ] Мобильное приложение
- [ ] Многоязычная поддержка