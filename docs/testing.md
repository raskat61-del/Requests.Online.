# Testing Guide

## Обзор тестирования

Проект использует комплексный подход к тестированию, включая:
- Модульные тесты (Unit tests)
- Интеграционные тесты
- Тесты API
- Тесты frontend компонентов

## Backend тесты

### Запуск тестов

```bash
cd backend

# Установка тестовых зависимостей
pip install -r requirements-test.txt

# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Запуск определенной категории
pytest -m auth
pytest -m projects
```

### Структура тестов

```
tests/
├── test_auth.py          # Аутентификация
├── test_projects.py      # Проекты
├── test_collectors.py    # Коллекторы данных
├── test_analyzers.py     # Анализаторы
└── test_integration.py   # Интеграционные
```

## Frontend тесты

### Запуск тестов

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск всех тестов
npm run test

# Запуск с UI
npm run test:ui

# Покрытие кода
npm run test:coverage
```