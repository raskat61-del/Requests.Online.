# Схема базы данных для бота-аналитика

## Структура таблиц

### Таблица users (Пользователи)
```sql
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
```

### Таблица projects (Проекты анализа)
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица keywords (Ключевые слова)
```sql
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    keyword VARCHAR(500) NOT NULL,
    category VARCHAR(100), -- pain_points, solutions, complaints, etc.
    priority INTEGER DEFAULT 1, -- 1-5 приоритет
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица search_sources (Источники поиска)
```sql
CREATE TABLE search_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL, -- google, yandex, telegram, vk, reddit, forums
    is_enabled BOOLEAN DEFAULT TRUE,
    api_config JSONB, -- конфигурация API (ключи, настройки)
    rate_limit INTEGER DEFAULT 100, -- лимит запросов в час
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица search_tasks (Задачи поиска)
```sql
CREATE TABLE search_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES search_sources(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица collected_data (Собранные данные)
```sql
CREATE TABLE collected_data (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES search_tasks(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL, -- google, yandex, telegram, etc.
    source_url TEXT,
    title TEXT,
    content TEXT NOT NULL,
    author VARCHAR(200),
    published_at TIMESTAMP,
    metadata JSONB, -- дополнительные данные (лайки, репосты, etc.)
    language VARCHAR(10) DEFAULT 'ru',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица text_analysis (Результаты анализа текста)
```sql
CREATE TABLE text_analysis (
    id SERIAL PRIMARY KEY,
    data_id INTEGER REFERENCES collected_data(id) ON DELETE CASCADE,
    sentiment_score FLOAT, -- -1 to 1 (negative to positive)
    sentiment_label VARCHAR(20), -- negative, neutral, positive
    keywords_extracted JSONB, -- массив извлеченных ключевых слов
    topics JSONB, -- массив топиков
    cluster_id INTEGER, -- ID кластера
    pain_points JSONB, -- выявленные болевые точки
    confidence_score FLOAT, -- уверенность анализа
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица clusters (Кластеры)
```sql
CREATE TABLE clusters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200),
    description TEXT,
    keywords JSONB, -- основные ключевые слова кластера
    size INTEGER DEFAULT 0, -- количество документов в кластере
    avg_sentiment FLOAT, -- средняя тональность
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица frequency_analysis (Частотный анализ)
```sql
CREATE TABLE frequency_analysis (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    term VARCHAR(200) NOT NULL,
    frequency INTEGER NOT NULL,
    tf_idf_score FLOAT,
    document_count INTEGER, -- в скольких документах встречается
    category VARCHAR(100), -- pain_point, solution, complaint, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица reports (Отчеты)
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL, -- summary, detailed, sentiment, clusters
    format VARCHAR(10) NOT NULL, -- pdf, excel, json
    file_path VARCHAR(500),
    file_size INTEGER,
    parameters JSONB, -- параметры генерации отчета
    status VARCHAR(20) DEFAULT 'generating', -- generating, completed, failed
    generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица api_usage (Использование API)
```sql
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES search_sources(id),
    requests_count INTEGER DEFAULT 1,
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, source_id, date)
);
```

### Таблица user_subscriptions (Подписки пользователей)
```sql
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_name VARCHAR(50) NOT NULL, -- free, basic, premium
    max_projects INTEGER DEFAULT 1,
    max_keywords_per_project INTEGER DEFAULT 10,
    max_requests_per_day INTEGER DEFAULT 100,
    price_per_month DECIMAL(10,2),
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ends_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Индексы для оптимизации

```sql
-- Индексы для быстрого поиска
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_keywords_project_id ON keywords(project_id);
CREATE INDEX idx_search_tasks_project_id ON search_tasks(project_id);
CREATE INDEX idx_search_tasks_status ON search_tasks(status);
CREATE INDEX idx_collected_data_task_id ON collected_data(task_id);
CREATE INDEX idx_collected_data_published_at ON collected_data(published_at);
CREATE INDEX idx_text_analysis_data_id ON text_analysis(data_id);
CREATE INDEX idx_text_analysis_cluster_id ON text_analysis(cluster_id);
CREATE INDEX idx_clusters_project_id ON clusters(project_id);
CREATE INDEX idx_frequency_analysis_project_id ON frequency_analysis(project_id);
CREATE INDEX idx_frequency_analysis_frequency ON frequency_analysis(frequency DESC);
CREATE INDEX idx_reports_project_id ON reports(project_id);
CREATE INDEX idx_api_usage_user_date ON api_usage(user_id, date);

-- Полнотекстовый поиск
CREATE INDEX idx_collected_data_content_fts ON collected_data USING gin(to_tsvector('russian', content));
CREATE INDEX idx_collected_data_title_fts ON collected_data USING gin(to_tsvector('russian', title));
```

## Триггеры для автоматического обновления

```sql
-- Триггер для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Триггер для подсчета размера кластера
CREATE OR REPLACE FUNCTION update_cluster_size()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE clusters 
        SET size = size + 1 
        WHERE id = NEW.cluster_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.cluster_id != NEW.cluster_id THEN
        UPDATE clusters 
        SET size = size - 1 
        WHERE id = OLD.cluster_id;
        UPDATE clusters 
        SET size = size + 1 
        WHERE id = NEW.cluster_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE clusters 
        SET size = size - 1 
        WHERE id = OLD.cluster_id;
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_cluster_size_trigger 
    AFTER INSERT OR UPDATE OR DELETE ON text_analysis
    FOR EACH ROW EXECUTE FUNCTION update_cluster_size();
```

## Представления для быстрого доступа

```sql
-- Представление для статистики проекта
CREATE VIEW project_stats AS
SELECT 
    p.id,
    p.name,
    p.user_id,
    COUNT(DISTINCT k.id) as keywords_count,
    COUNT(DISTINCT st.id) as tasks_count,
    COUNT(DISTINCT cd.id) as collected_data_count,
    COUNT(DISTINCT c.id) as clusters_count,
    COUNT(DISTINCT r.id) as reports_count,
    AVG(ta.sentiment_score) as avg_sentiment
FROM projects p
LEFT JOIN keywords k ON p.id = k.project_id
LEFT JOIN search_tasks st ON p.id = st.project_id
LEFT JOIN collected_data cd ON st.id = cd.task_id
LEFT JOIN clusters c ON p.id = c.project_id
LEFT JOIN reports r ON p.id = r.project_id
LEFT JOIN text_analysis ta ON cd.id = ta.data_id
GROUP BY p.id, p.name, p.user_id;

-- Представление для топ ключевых слов
CREATE VIEW top_keywords AS
SELECT 
    fa.project_id,
    fa.term,
    fa.frequency,
    fa.tf_idf_score,
    fa.category,
    RANK() OVER (PARTITION BY fa.project_id ORDER BY fa.frequency DESC) as rank
FROM frequency_analysis fa;
```

## Начальные данные

```sql
-- Источники поиска
INSERT INTO search_sources (name, is_enabled, rate_limit) VALUES
('google', true, 100),
('yandex', true, 100),
('telegram', true, 50),
('vkontakte', true, 100),
('reddit', true, 60),
('forums', true, 200);

-- Планы подписки
INSERT INTO user_subscriptions (user_id, plan_name, max_projects, max_keywords_per_project, max_requests_per_day, price_per_month) VALUES
(1, 'free', 1, 10, 100, 0.00),
(1, 'basic', 5, 50, 500, 29.99),
(1, 'premium', 20, 200, 2000, 99.99);
```