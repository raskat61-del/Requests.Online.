# Архитектура системы "Analytics Bot"

## Общая схема архитектуры

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Data Collectors │
                    │  & Analyzers     │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  External APIs  │
                    │  & Sources      │
                    └─────────────────┘
```

## Компоненты системы

### 1. Backend (FastAPI)
- **Auth Module**: JWT авторизация, управление пользователями
- **Data Collection Service**: Координация сбора данных
- **Analysis Service**: Обработка и анализ собранных данных
- **Report Service**: Генерация отчетов и визуализации
- **API Endpoints**: REST API для взаимодействия с фронтендом

### 2. Database Schema (PostgreSQL)
- **users**: Пользователи системы
- **projects**: Проекты анализа
- **keywords**: Ключевые слова для поиска
- **search_tasks**: Задачи на сбор данных
- **collected_data**: Собранные данные
- **reports**: Сгенерированные отчеты

### 3. Data Collectors
- **Google Search API**: Поиск через Google Custom Search
- **Yandex Search API**: Поиск через Yandex API
- **Social Media Scrapers**:
  - Telegram (telethon)
  - VKontakte API
  - Reddit API
- **Web Scrapers**: BeautifulSoup/Scrapy для форумов

### 4. Text Analysis Engine
- **Preprocessing**: Очистка текста, токенизация
- **Clustering**: Группировка по смыслу
- **Frequency Analysis**: TF-IDF, N-граммы
- **Sentiment Analysis**: Определение тональности
- **Pain Point Detection**: Выявление проблем

## Технологический стек

### Backend
- **FastAPI**: Основной фреймворк
- **SQLAlchemy**: ORM для работы с БД
- **Alembic**: Миграции БД
- **Celery**: Асинхронные задачи
- **Redis**: Брокер для Celery, кеширование

### Data Processing
- **spaCy**: NLP библиотека
- **scikit-learn**: Машинное обучение
- **dostoevsky**: Анализ тональности
- **BeautifulSoup4**: Парсинг HTML

### Infrastructure
- **PostgreSQL**: Основная БД
- **Redis**: Кеш и брокер
- **Docker**: Контейнеризация
- **Nginx**: Reverse proxy