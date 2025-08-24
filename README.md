# Analytics Bot

Comprehensive Analytics Bot for collecting and analyzing data from multiple sources (Google, Yandex, Telegram, VK, Reddit) to identify pain points and unmet needs for SaaS product development. Built with FastAPI, React, and advanced NLP tools.

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

## 🛠️ Technology Stack

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