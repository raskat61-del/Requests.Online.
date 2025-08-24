# 🔑 Руководство по получению API ключей для AnalyticsBot

## 📋 Содержание
- [Google Custom Search API](#google-custom-search-api)
- [Yandex Search API](#yandex-search-api)
- [Telegram API](#telegram-api)
- [VKontakte API](#vkontakte-api)
- [Reddit API](#reddit-api)
- [Настройка .env файла](#настройка-env-файла)

---

## 🔍 Google Custom Search API

### Шаг 1: Создание Google Cloud проекта
1. Перейдите на https://console.cloud.google.com/
2. Войдите в свой Google аккаунт
3. Нажмите **"Select a project"** → **"New Project"**
4. Введите название проекта (например: "AnalyticsBot")
5. Нажмите **"Create"**

### Шаг 2: Включение Custom Search API
1. В левом меню выберите **"APIs & Services"** → **"Library"**
2. Найдите "Custom Search API"
3. Нажмите на него и затем **"Enable"**

### Шаг 3: Создание API ключа
1. Перейдите в **"APIs & Services"** → **"Credentials"**
2. Нажмите **"+ Create Credentials"** → **"API key"**
3. Скопируйте созданный ключ
4. Нажмите **"Restrict key"** для безопасности
5. В разделе "API restrictions" выберите "Restrict key"
6. Отметьте только "Custom Search API"
7. Нажмите **"Save"**

### Шаг 4: Создание Custom Search Engine
1. Перейдите на https://cse.google.com/cse/
2. Нажмите **"Add"**
3. В поле "Sites to search" введите `*` (для поиска по всему интернету)
4. Дайте название поисковику (например: "AnalyticsBot Search")
5. Нажмите **"Create"**
6. В настройках поисковика найдите "Search engine ID" и скопируйте его

**Результат:**
- `GOOGLE_API_KEY` = ваш API ключ
- `GOOGLE_CSE_ID` = ID поискового движка

---

## 🔍 Yandex Search API

### Шаг 1: Регистрация в Yandex.Cloud
1. Перейдите на https://cloud.yandex.ru/
2. Войдите или создайте Yandex аккаунт
3. Нажмите **"Попробовать бесплатно"**
4. Заполните регистрационную форму

### Шаг 2: Создание каталога
1. В консоли нажмите **"Создать каталог"**
2. Дайте название (например: "analytics-bot")
3. Нажмите **"Создать"**

### Шаг 3: Получение API ключа
1. Перейдите в **"Сервисные аккаунты"**
2. Нажмите **"Создать сервисный аккаунт"**
3. Введите имя аккаунта
4. Выберите роль **"search-api.executor"**
5. Нажмите **"Создать"**
6. Нажмите на созданный аккаунт
7. Перейдите во вкладку **"API-ключи"**
8. Нажмите **"Создать API-ключ"**
9. Скопируйте ключ

**Результат:**
- `YANDEX_API_KEY` = ваш API ключ

---

## 📱 Telegram API

### Шаг 1: Создание приложения
1. Перейдите на https://my.telegram.org/apps
2. Войдите в Telegram (введите номер телефона)
3. Нажмите **"API development tools"**

### Шаг 2: Заполнение формы
1. **App title**: AnalyticsBot
2. **Short name**: analyticsbot
3. **URL**: можете оставить пустым
4. **Platform**: Desktop
5. **Description**: Analytics bot for data collection
6. Нажмите **"Create application"**

### Шаг 3: Получение данных
После создания вы увидите:
- **api_id** - это ваш TELEGRAM_API_ID
- **api_hash** - это ваш TELEGRAM_API_HASH

**Результат:**
- `TELEGRAM_API_ID` = api_id (число)
- `TELEGRAM_API_HASH` = api_hash (строка)

---

## 🔵 VKontakte API

### Шаг 1: Создание приложения
1. Перейдите на https://vk.com/apps?act=manage
2. Войдите в свой VK аккаунт
3. Нажмите **"Создать приложение"**

### Шаг 2: Настройка приложения
1. **Название**: AnalyticsBot
2. **Платформа**: Веб-сайт
3. **Адрес сайта**: http://localhost:8000
4. **Базовый домен**: localhost
5. Нажмите **"Подключить сайт"**

### Шаг 3: Получение токена
1. В настройках приложения найдите **"ID приложения"**
2. Перейдите по ссылке: 
   ```
   https://oauth.vk.com/authorize?client_id=ВАШ_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline&response_type=token&v=5.131
   ```
3. Замените "ВАШ_ID" на ID вашего приложения
4. Разрешите доступ
5. Скопируйте токен из URL после `access_token=`

**Результат:**
- `VK_API_TOKEN` = ваш access token

---

## 🔴 Reddit API

### Шаг 1: Создание Reddit аккаунта
1. Перейдите на https://www.reddit.com/
2. Создайте аккаунт или войдите в существующий

### Шаг 2: Создание приложения
1. Перейдите на https://www.reddit.com/prefs/apps
2. Нажмите **"Create App"** или **"Create Another App"**

### Шаг 3: Заполнение формы
1. **name**: AnalyticsBot
2. **App type**: выберите **"script"**
3. **description**: Analytics bot for data collection
4. **about url**: можете оставить пустым
5. **redirect uri**: http://localhost:8000
6. Нажмите **"Create app"**

### Шаг 4: Получение данных
После создания вы увидите:
- Под названием приложения - это **client_id** (короткая строка)
- **secret** - это **client_secret** (длинная строка)

**Результат:**
- `REDDIT_CLIENT_ID` = client_id
- `REDDIT_CLIENT_SECRET` = client_secret

---

## ⚙️ Настройка .env файла

### Шаг 1: Создание файла
1. Перейдите в папку `backend/` вашего проекта
2. Скопируйте файл `.env.example` и переименуйте в `.env`
3. Откройте `.env` в текстовом редакторе

### Шаг 2: Заполнение ключей
```env
# Database (можете оставить как есть для локальной разработки)
DATABASE_URL=postgresql://analytics_user:analytics_password@localhost:5432/analytics_db
ASYNC_DATABASE_URL=postgresql+asyncpg://analytics_user:analytics_password@localhost:5432/analytics_db

# Redis (можете оставить как есть)
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security (ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ!)
SECRET_KEY=ваш-супер-секретный-ключ-минимум-32-символа
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google API (вставьте ваши ключи)
GOOGLE_API_KEY=ваш_google_api_ключ
GOOGLE_CSE_ID=ваш_google_cse_id

# Yandex API
YANDEX_API_KEY=ваш_yandex_api_ключ

# Telegram API
TELEGRAM_API_ID=ваш_telegram_api_id
TELEGRAM_API_HASH=ваш_telegram_api_hash

# VKontakte API
VK_API_TOKEN=ваш_vk_access_token

# Reddit API
REDDIT_CLIENT_ID=ваш_reddit_client_id
REDDIT_CLIENT_SECRET=ваш_reddit_client_secret

# Application
APP_NAME=Analytics Bot
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO
```

### Шаг 3: Генерация SECRET_KEY
Вы можете сгенерировать безопасный SECRET_KEY несколькими способами:

**Способ 1: Python**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Способ 2: Онлайн генератор**
- Перейдите на https://generate-secret.vercel.app/32
- Скопируйте сгенерированный ключ

**Способ 3: OpenSSL (если установлен)**
```bash
openssl rand -hex 32
```

## ⚠️ Важные замечания

### 💰 Стоимость API
- **Google Custom Search**: 100 запросов/день бесплатно
- **Yandex Search**: Первые 1000 запросов бесплатно
- **Telegram**: Полностью бесплатно
- **VKontakte**: Бесплатно с лимитами
- **Reddit**: Бесплатно с лимитами

### 🔒 Безопасность
1. **НЕ** делитесь своими API ключами
2. **НЕ** коммитьте `.env` файл в Git
3. Для продакшена используйте переменные окружения
4. Регулярно обновляйте ключи

### 🧪 Тестирование
После настройки ключей проверьте их работу:
```bash
# Запустите проект
docker-compose up -d

# Проверьте API
curl http://localhost:8000/health

# Проверьте документацию
# Откройте http://localhost:8000/docs
```

## 🆘 Решение проблем

### Проблема: Google API не работает
- Проверьте, что Custom Search API включен
- Убедитесь, что ключ не ограничен по IP/домену
- Проверьте квоты в Google Cloud Console

### Проблема: Telegram API ошибки
- Убедитесь, что api_id указан как число, не как строка
- Проверьте правильность api_hash

### Проблема: VK API не работает
- Убедитесь, что токен получен с правильными правами (scope=offline)
- Проверьте, что приложение активно

**🎉 Готово! Теперь ваш AnalyticsBot готов к сбору данных из всех источников!**