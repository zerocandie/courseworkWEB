-- Кодировка (обязательно для русского текста)
SET client_encoding = 'UTF8';

-- =============================
-- 1. ПОЛЬЗОВАТЕЛИ
-- =============================
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- 2. РОЛИ
-- =============================
CREATE TABLE roles (
    id SMALLINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

-- =============================
-- 3. СВЯЗЬ ПОЛЬЗОВАТЕЛИ-РОЛИ
-- =============================
CREATE TABLE users_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id SMALLINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- =============================
-- 4. КАТЕГОРИИ
-- =============================
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT REFERENCES categories(id) ON DELETE SET NULL,
    date_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- 5. КУРСЫ
-- =============================
CREATE TABLE courses (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE,
    description TEXT NOT NULL,
    short_desc VARCHAR(300),
    instructor_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    is_published BOOLEAN DEFAULT true,
    is_deleted BOOLEAN DEFAULT false,
    thumbnail_url VARCHAR(500),
    duration_hours INT CHECK (duration_hours >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- 6. МОДУЛИ
-- =============================
CREATE TABLE modules (
    id BIGSERIAL PRIMARY KEY,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_deleted BOOLEAN DEFAULT false,
    order_num INT NOT NULL DEFAULT 0,
    UNIQUE (course_id, order_num)
);

-- =============================
-- 7. УРОКИ
-- =============================
CREATE TABLE lessons (
    id BIGSERIAL PRIMARY KEY,
    module_id BIGINT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    video_url VARCHAR(500),
    is_deleted BOOLEAN DEFAULT false,
    order_num INT NOT NULL DEFAULT 0,
    is_locked BOOLEAN DEFAULT false,
    duration_min INT CHECK (duration_min >= 0),
    UNIQUE (module_id, order_num)
);

-- =============================
-- 8. ПЛАТЕЖИ
-- =============================
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL DEFAULT 'RUB' CHECK (currency IN ('RUB', 'USD', 'EUR')),
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    transaction_id VARCHAR(255),
    paid_at TIMESTAMP
);

-- =============================
-- 9. ЗАПИСИ НА КУРСЫ
-- =============================
CREATE TABLE enrollments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    payment_id BIGINT REFERENCES payments(id) ON DELETE SET NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    progress_pct SMALLINT DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
    UNIQUE (user_id, course_id)
);

-- =============================
-- 10. ОЦЕНКИ
-- =============================
CREATE TABLE ratings (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, course_id)
);

-- =============================
-- 11. ДОМАШНИЕ ЗАДАНИЯ
-- =============================
CREATE TABLE assignments (
    id BIGSERIAL PRIMARY KEY,
    lesson_id BIGINT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    max_score INT NOT NULL CHECK (max_score > 0),
    is_required BOOLEAN DEFAULT true
);

-- =============================
-- 12. РЕШЕНИЯ
-- =============================
CREATE TABLE submissions (
    id BIGSERIAL PRIMARY KEY,
    assignment_id BIGINT NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT,
    file_url VARCHAR(500),
    score INT CHECK (score >= 0),
    feedback TEXT,
    is_graded BOOLEAN DEFAULT false,
    UNIQUE (assignment_id, user_id)
);

-- =============================
-- 13. СЕРТИФИКАТЫ
-- =============================
CREATE TABLE certificates (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    certificate_url VARCHAR(500) NOT NULL,
    verification_code VARCHAR(50) NOT NULL UNIQUE,
    UNIQUE (user_id, course_id)
);

-- =============================
-- 14. КОММЕНТАРИИ
-- =============================
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES comments(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id BIGINT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    lesson_id BIGINT REFERENCES lessons(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,
    CONSTRAINT chk_comment_target
        CHECK (
            (lesson_id IS NOT NULL AND course_id IS NOT NULL) OR
            (lesson_id IS NULL AND course_id IS NOT NULL)
        )
);

-- =============================
-- ФУНКЦИЯ И ТРИГГЕРЫ ДЛЯ updated_at
-- =============================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================
-- ИНДЕКСЫ
-- =============================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_category ON courses(category_id);
CREATE INDEX idx_courses_slug ON courses(slug);
CREATE INDEX idx_enrollments_user ON enrollments(user_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_comments_course ON comments(course_id);
CREATE INDEX idx_comments_lesson ON comments(lesson_id);
CREATE INDEX idx_comments_parent ON comments(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);

-- =============================
-- ДАННЫЕ
-- =============================

-- Роли
INSERT INTO roles (id, name, description) VALUES
(1, 'admin', 'Администратор'),
(2, 'instructor', 'Преподаватель'),
(3, 'student', 'Студент');

-- Пользователи
INSERT INTO users (email, password_hash, first_name, last_name, phone, avatar_url)
VALUES
  ('nikita@edu.ru', 'hash1', 'Никита', 'Поляков', '+79001111111', 'https://a.com/nikita.jpg'),
  ('liza@edu.ru', 'hash2', 'Лиза', 'Смирнова', '+79002222222', 'https://a.com/liza.jpg'),
  ('python_teacher@edu.ru', 'hash3', 'Анна', 'Котова', '+79003333333', 'https://a.com/anna.jpg'),
  ('web_teacher@edu.ru', 'hash4', 'Иван', 'Сергеев', '+79004444444', 'https://a.com/ivan.jpg'),
  ('student1@edu.ru', 'hash5', 'Мария', 'Иванова', '+79005555555', 'https://a.com/mary.jpg'),
  ('student2@edu.ru', 'hash6', 'Артём', 'Фёдоров', '+79006666666', NULL),
  ('student3@edu.ru', 'hash7', 'Ольга', 'Петрова', '+79007777777', 'https://a.com/olga.jpg'),
  ('student4@edu.ru', 'hash8', 'Дмитрий', 'Сидоров', '+79008888888', NULL);

-- Роли пользователей
INSERT INTO users_roles (user_id, role_id)
VALUES
  (1, 1), (2, 1),
  (3, 2), (4, 2),
  (5, 3), (6, 3), (7, 3), (8, 3);

-- Категории
INSERT INTO categories (name, slug, parent_id)
VALUES ('Программирование', 'programming', NULL);

-- Курсы (4 платных)
INSERT INTO courses (title, slug, description, short_desc, instructor_id, category_id, price, thumbnail_url, duration_hours)
VALUES
  ('Python', 'python', 'Полный курс по Python: синтаксис, функции, ООП.', 'Научитесь программировать на Python', 3, 1, 2990.00, 'https://t.com/py.jpg', 20),
  ('C#', 'csharp', 'Основы C# и .NET: переменные, классы, коллекции.', 'Освойте C# и создайте приложение', 4, 1, 3490.00, 'https://t.com/cs.jpg', 24),
  ('Java', 'java', 'Базовый курс по Java: синтаксис, ООП, исключения.', 'Изучите Java и напишите консольное приложение', 3, 1, 3290.00, 'https://t.com/java.jpg', 22),
  ('React', 'react', 'Современный React: компоненты, хуки, маршрутизация.', 'Создайте SPA на React', 4, 1, 3990.00, 'https://t.com/react.jpg', 26);

-- Модули
INSERT INTO modules (course_id, title, description, order_num)
VALUES
  (1, 'Основы Python', 'Первые шаги', 1),
  (1, 'Функции и ООП', 'Создание функций и классов', 2),
  (2, 'Синтаксис C#', 'Типы, циклы, условия', 1),
  (2, 'Классы и объекты', 'Основы ООП в C#', 2),
  (3, 'Основы Java', 'JDK, IDE, синтаксис', 1),
  (3, 'Коллекции и исключения', 'Работа с данными и ошибками', 2),
  (4, 'Компоненты React', 'JSX, props, state', 1),
  (4, 'Хуки и маршруты', 'useState, useEffect, React Router', 2);

-- Уроки
INSERT INTO lessons (module_id, title, content, video_url, order_num, duration_min)
VALUES
  (1, 'Установка и Hello World', 'Как установить Python', 'https://v.com/py1', 1, 10),
  (1, 'Переменные и типы', 'int, str, bool, list', 'https://v.com/py2', 2, 12),
  (2, 'Функции', 'def, аргументы, return', 'https://v.com/py3', 1, 15),
  (2, 'Классы', 'class, объекты, наследование', 'https://v.com/py4', 2, 18),
  (3, 'Первая программа', 'Hello World в Visual Studio', 'https://v.com/cs1', 1, 11),
  (3, 'Условия и циклы', 'if, for, while', 'https://v.com/cs2', 2, 13),
  (4, 'Классы', 'Определение и использование', 'https://v.com/cs3', 1, 16),
  (4, 'LINQ', 'Запросы к коллекциям', 'https://v.com/cs4', 2, 14),
  (5, 'JDK и IntelliJ IDEA', 'Настройка среды', 'https://v.com/java1', 1, 9),
  (5, 'Методы', 'Создание и вызов методов', 'https://v.com/java2', 2, 12),
  (6, 'Исключения', 'try-catch-finally', 'https://v.com/java3', 1, 14),
  (6, 'Списки и Map', 'ArrayList, HashMap', 'https://v.com/java4', 2, 15),
  (7, 'Что такое React', 'JSX, компоненты', 'https://v.com/react1', 1, 12),
  (7, 'State и Props', 'Управление данными', 'https://v.com/react2', 2, 16),
  (8, 'useState', 'Хук для состояния', 'https://v.com/react3', 1, 14),
  (8, 'React Router', 'Навигация между страницами', 'https://v.com/react4', 2, 18);

-- Платежи
INSERT INTO payments (user_id, course_id, amount, currency, payment_method, status, transaction_id, paid_at)
VALUES
  (5, 1, 2990.00, 'RUB', 'bank_card', 'completed', 'txn001', '2025-12-01 10:00:00'),
  (6, 2, 3490.00, 'RUB', 'sbp', 'completed', 'txn002', '2025-12-01 11:30:00'),
  (7, 3, 3290.00, 'RUB', 'bank_card', 'completed', 'txn003', '2025-12-02 09:15:00'),
  (8, 4, 3990.00, 'RUB', 'wallet', 'completed', 'txn004', '2025-12-02 14:20:00');

-- Записи на курсы
INSERT INTO enrollments (user_id, course_id, payment_id, progress_pct, status)
VALUES
  (5, 1, 1, 100, 'completed'),
  (6, 2, 2, 60, 'active'),
  (7, 3, 3, 40, 'active'),
  (8, 4, 4, 20, 'active');

UPDATE enrollments SET completed_at = '2025-12-10 18:00:00' WHERE user_id = 5 AND course_id = 1;

-- Оценки
INSERT INTO ratings (user_id, course_id, rating, comment)
VALUES
  (5, 1, 5, 'Отличный курс!'),
  (6, 2, 4, 'Хорошо, но сложно'),
  (7, 3, 5, 'Лучшее объяснение Java!'),
  (8, 4, 4, 'Нужно больше практики');

-- Домашние задания
INSERT INTO assignments (lesson_id, title, description, max_score)
VALUES
  (1, 'Hello World на Python', 'Напишите первую программу', 10),
  (3, 'Калькулятор на Python', 'Функции для 4 операций', 20),
  (5, 'Консольный калькулятор на C#', 'Сделайте приложение', 20),
  (7, 'Класс "Автомобиль" на C#', 'Создайте класс', 25),
  (9, 'Консольное приложение на Java', 'Hello World', 15),
  (11, 'Обработка исключений', 'Разделите два числа', 20),
  (13, 'Компонент "Карточка"', 'Создайте React-компонент', 15),
  (15, 'Счётчик на useState', 'Кнопки +1, -1', 20);

-- Решения
INSERT INTO submissions (assignment_id, user_id, content, score, is_graded)
VALUES
  (1, 5, 'print("Hello")', 10, true),
  (3, 5, 'Код функций', 18, true),
  (5, 6, 'Архив проекта', 19, true),
  (7, 6, 'Класс Car', 24, true);

-- Сертификат
INSERT INTO certificates (user_id, course_id, certificate_url, verification_code)
VALUES (5, 1, 'https://edu.ru/cert/py-5.pdf', 'CERT-PY-5-2025');

-- Комментарии
INSERT INTO comments (user_id, course_id, lesson_id, content)
VALUES
  (5, 1, 1, 'А обязательно ли использовать VS Code?'),
  (3, 1, 1, 'Нет, можно любую IDE'),
  (6, 2, 5, 'Что такое .sln файл?'),
  (4, 2, 5, 'Это решение в Visual Studio');

INSERT INTO comments (user_id, course_id, content)
VALUES (7, 3, 'Когда выйдет следующий модуль?');