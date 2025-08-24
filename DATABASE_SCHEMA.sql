# Схема базы данных для бота-аналитика

-- Таблица users (Пользователи)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица projects (Проекты анализа)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица keywords (Ключевые слова)
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    keyword VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица search_sources (Источники поиска)
CREATE TABLE search_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    api_config JSONB,
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица search_tasks (Задачи поиска)
CREATE TABLE search_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES search_sources(id),
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица collected_data (Собранные данные)
CREATE TABLE collected_data (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES search_tasks(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    title TEXT,
    content TEXT NOT NULL,
    author VARCHAR(200),
    published_at TIMESTAMP,
    metadata JSONB,
    language VARCHAR(10) DEFAULT 'ru',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_keywords_project_id ON keywords(project_id);
CREATE INDEX idx_search_tasks_project_id ON search_tasks(project_id);
CREATE INDEX idx_search_tasks_status ON search_tasks(status);
CREATE INDEX idx_collected_data_task_id ON collected_data(task_id);

-- Начальные данные
INSERT INTO search_sources (name, is_enabled, rate_limit) VALUES
('google', true, 100),
('yandex', true, 100),
('telegram', true, 50),
('vkontakte', true, 100),
('reddit', true, 60);