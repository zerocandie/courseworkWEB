# Инструкция для фронтенд-разработчика: подключение к Django-бэкенду

Данный документ описывает порядок запуска бэкенда и взаимодействия с ним через REST API.

## Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Docker и Docker Compose

## Структура проекта

```
courseworkWEB/
├── backend/                # Django-приложение
├── frontend/               # Фронтенд-часть
└── docker/projects/lms-db/ # Конфигурация PostgreSQL в Docker
```

## Запуск бэкенда

1. Запустите базу данных:

   ```bash
   cd docker/projects/lms-db
   docker-compose up -d
   ```
2. Перейдите в директорию бэкенда:

   ```bash
   cd ../../backend
   ```
3. Установите зависимости (при первом запуске):

   ```bash
   pip install django djangorestframework psycopg2-binary
   ```
4. Запустите сервер:

   ```bash
   python manage.py runserver
   ```

Бэкенд будет доступен по адресу: `http://127.0.0.1:8000`.

## Доступные эндпоинты

Все API-методы доступны по префиксу `/api/v1/`.

### Публичные методы (только чтение, `GET`)

- `/api/v1/courses/` — список курсов
- `/api/v1/courses/{slug}/` — детальная информация о курсе (включая модули и уроки)
- `/api/v1/users/` — список пользователей
- `/api/v1/categories/` — категории курсов
- `/api/v1/modules/`, `/api/v1/lessons/`, `/api/v1/comments/` и другие

### Методы с правами записи (`POST`, `PUT`, `PATCH`, `DELETE`)

Доступны только пользователям с ролью **администратора** (`role_id = 1`).

Для выполнения запросов на запись необходимо передавать идентификатор пользователя в теле запроса:

```json
{
  "user_id": 1,
  "title": "Новый курс",
  ...
}
```

Если `user_id` не указан или пользователь не является администратором, сервер вернёт ошибку `403 Forbidden`.

## Тестовые данные

В базе данных уже созданы следующие пользователи:

| Email                 | Роль                   | user_id |
| --------------------- | -------------------------- | ------- |
| nikita@edu.ru         | Администратор | 1       |
| liza@edu.ru           | Администратор | 2       |
| student1@edu.ru       | Студент             | 5       |
| python_teacher@edu.ru | Преподаватель | 3       |

Для тестирования операций записи используйте `user_id: 1` или `2`.

## Примеры запросов

Получение списка курсов:

```javascript
fetch('http://127.0.0.1:8000/api/v1/courses/')
  .then(response => response.json())
  .then(data => console.log(data));
```

Создание комментария (требуются права администратора):

```javascript
fetch('http://127.0.0.1:8000/api/v1/comments/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 1,
    course_id: 1,
    content: "Текст комментария"
  })
});
```

## Возможные проблемы

- Убедитесь, что контейнер с PostgreSQL запущен:`docker ps | grep lms_db`
- Убедитесь, что таблицы существуют:`docker exec -it lms_db psql -U postgres -d KyrsovayaBD -c "\dt"`
- В файле `backend/settings.py` должно быть указано:
  `HOST: '127.0.0.1'` в настройках базы данных.
