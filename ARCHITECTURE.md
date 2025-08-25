# Архитектура системы "Бот-аналитик"

## Общая схема архитектуры

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/HTML)  │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
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
                    │  & Parsers      │
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
- **analysis_results**: Результаты анализа
- **reports**: Сгенерированные отчеты

### 3. Data Collectors
- **Google Search API**: Поиск через Google Custom Search
- **Yandex Search API**: Поиск через Yandex API
- **Social Media Scrapers**:
  - Telegram (телепатия/telethon)
  - VKontakte API
  - Reddit API
- **Web Scrapers**: BeautifulSoup/Scrapy для форумов

### 4. Text Analysis Engine
- **Preprocessing**: Очистка текста, токенизация
- **Clustering**: Группировка по смыслу (KMeans, DBSCAN)
- **Frequency Analysis**: TF-IDF, N-граммы
- **Sentiment Analysis**: Определение тональности (VADER, досе-RuBERT)
- **Topic Modeling**: LDA, BERTopic

### 5. Report Generation
- **PDF Reports**: ReportLab
- **Excel Reports**: openpyxl
- **Visualizations**: Plotly, Matplotlib
- **Web Dashboard**: Интерактивные графики

## API Endpoints

### Authentication
- POST `/auth/register` - Регистрация
- POST `/auth/login` - Авторизация
- POST `/auth/refresh` - Обновление токена
- GET `/auth/me` - Профиль пользователя

### Projects
- GET `/projects` - Список проектов
- POST `/projects` - Создание проекта
- GET `/projects/{id}` - Детали проекта
- PUT `/projects/{id}` - Обновление проекта
- DELETE `/projects/{id}` - Удаление проекта

### Data Collection
- POST `/projects/{id}/keywords` - Добавление ключевых слов
- POST `/projects/{id}/start-collection` - Запуск сбора данных
- GET `/projects/{id}/collection-status` - Статус сбора
- GET `/projects/{id}/collected-data` - Просмотр данных

### Analysis
- POST `/projects/{id}/analyze` - Запуск анализа
- GET `/projects/{id}/analysis-results` - Результаты анализа
- GET `/projects/{id}/clusters` - Кластеры данных
- GET `/projects/{id}/sentiment` - Анализ тональности

### Reports
- POST `/projects/{id}/generate-report` - Генерация отчета
- GET `/projects/{id}/reports` - Список отчетов
- GET `/reports/{id}/download` - Скачивание отчета

## Технологический стек

### Backend
- **FastAPI**: Основной фреймворк
- **SQLAlchemy**: ORM для работы с БД
- **Alembic**: Миграции БД
- **Celery**: Асинхронные задачи
- **Redis**: Брокер для Celery, кеширование
- **Pydantic**: Валидация данных

### Data Processing
- **BeautifulSoup4**: Парсинг HTML
- **Scrapy**: Веб-скрапинг
- **requests**: HTTP клиент
- **telethon**: Telegram API
- **vk-api**: VKontakte API
- **praw**: Reddit API

### Text Analysis
- **spaCy**: NLP библиотека
- **scikit-learn**: Машинное обучение
- **NLTK**: Дополнительный NLP инструментарий
- **transformers**: BERT модели
- **dostoevsky**: Анализ тональности для русского языка

### Reports & Visualization
- **plotly**: Интерактивные графики
- **matplotlib**: Статические графики
- **reportlab**: PDF генерация
- **openpyxl**: Excel файлы
- **jinja2**: Шаблоны для отчетов

### Frontend
- **React**: UI фреймворк
- **Material-UI**: Компоненты интерфейса
- **axios**: HTTP клиент
- **recharts**: Графики для React

### Infrastructure
- **PostgreSQL**: Основная БД
- **Redis**: Кеш и брокер сообщений
- **Docker**: Контейнеризация
- **Docker Compose**: Оркестрация контейнеров
- **Nginx**: Reverse proxy
- **Gunicorn**: WSGI сервер

## Схема развертывания

```
┌─────────────┐
│   Nginx     │ (Reverse Proxy, Static Files)
└──────┬──────┘
       │
┌──────▼──────┐
│  Frontend   │ (React App)
│  Container  │
└─────────────┘
       │
┌──────▼──────┐
│  Backend    │ (FastAPI + Gunicorn)
│  Container  │
└──────┬──────┘
       │
┌──────▼──────┐    ┌─────────────┐
│ PostgreSQL  │    │   Redis     │
│ Container   │    │ Container   │
└─────────────┘    └─────────────┘
       │                   │
┌──────▼──────┐    ┌──────▼──────┐
│   Celery    │    │   Celery    │
│   Worker    │    │   Beat      │
└─────────────┘    └─────────────┘
```

## Масштабирование

### Горизонтальное
- Несколько worker'ов для Celery
- Load balancer для FastAPI инстансов
- Реплики PostgreSQL для чтения

### Вертикальное
- Увеличение ресурсов контейнеров
- SSD диски для БД
- Больше RAM для кеширования

## Безопасность

- JWT токены с истечением срока
- Rate limiting для API
- CORS настройки
- Валидация всех входных данных
- Encrypted хранение API ключей
- HTTPS для продакшена