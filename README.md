# Microblog Practice Project

Учебный веб-проект «Microblog» — небольшой сервис для создания и управления публикациями пользователей.

Проект разработан в рамках учебной практики и реализован с использованием Python, Flask, SQLite, HTML, CSS и JavaScript.

## Возможности

* регистрация пользователя;
* авторизация и выход из аккаунта;
* просмотр публикаций;
* создание публикаций;
* редактирование собственных публикаций;
* удаление собственных публикаций;
* просмотр профиля пользователя;
* загрузка и изменение аватара;
* REST API для работы с публикациями;
* автоматическое тестирование основных функций приложения.

## Технологический стек

### Backend

* Python 3
* Flask
* Flask-SQLAlchemy
* Werkzeug

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Database

* SQLite

### Testing

* pytest

### Version control

* Git
* GitHub

## Структура проекта

```text
microblog-practice/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   └── uploads/
│   │       └── avatars/
│   ├── templates/
│   ├── __init__.py
│   ├── auth.py
│   ├── models.py
│   ├── routes.py
│   ├── api.py
│   └── migrate_avatar.py
├── tests/
│   └── test_app.py
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Модель данных

В приложении используются две основные сущности:

### User

Пользователь системы.

Поля:

* `id` — идентификатор пользователя;
* `username` — имя пользователя;
* `email` — электронная почта;
* `password_hash` — хеш пароля;
* `created_at` — дата создания аккаунта;
* `avatar` — имя файла аватара.

### Post

Публикация пользователя.

Поля:

* `id` — идентификатор публикации;
* `title` — заголовок;
* `content` — текст публикации;
* `created_at` — дата создания;
* `updated_at` — дата последнего изменения;
* `user_id` — идентификатор автора.

Связь между таблицами:

```text
User 1 ───────── N Post
```

Один пользователь может иметь несколько публикаций.

## Основные маршруты

### Аутентификация

```text
GET/POST /register
GET/POST /login
GET      /logout
```

### Публикации

```text
GET      /
GET/POST /posts/create
GET/POST /posts/<id>/edit
POST     /posts/<id>/delete
```

### Профиль

```text
GET      /profile/<username>
GET/POST /profile/edit
```

## REST API

API располагается по адресу:

```text
/api
```

Поддерживаемые операции:

```text
GET    /api/posts
POST   /api/posts
GET    /api/posts/<id>
PUT    /api/posts/<id>
DELETE /api/posts/<id>
```

API использует формат JSON.

### Пример GET-запроса

```http
GET /api/posts
```

Пример ответа:

```json
[
    {
        "id": 1,
        "title": "Example post",
        "content": "Hello world",
        "user_id": 1,
        "username": "admin"
    }
]
```

### Создание публикации

```http
POST /api/posts
Content-Type: application/json
```

Пример тела запроса:

```json
{
    "title": "New post",
    "content": "Post content",
    "user_id": 1
}
```

## Локальный запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/AlexPy-hub/microblog-practice.git
cd microblog-practice
```

### 2. Создание виртуального окружения

Windows:

```powershell
python -m venv .venv
```

Активация:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```powershell
pip install -r requirements.txt
```

### 4. Запуск приложения

```powershell
python run.py
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:5000
```

## Запуск тестов

Для запуска автоматических тестов используется pytest:

```powershell
pytest
```

Тесты проверяют:

* главную страницу;
* регистрацию;
* авторизацию;
* создание публикаций;
* редактирование публикаций;
* удаление публикаций;
* получение публикаций через API;
* создание публикации через API;
* получение одной публикации через API;
* обновление публикации через API;
* удаление публикации через API.

## Безопасность

Пароли пользователей не сохраняются в базе данных в открытом виде.

Для хранения паролей используется хеширование с помощью Werkzeug.

Данные пользователей и публикаций хранятся в SQLite.

## Git

Проект разрабатывается с использованием Git.

Основная ветка:

```text
main
```

Репозиторий проекта:

https://github.com/AlexPy-hub/microblog-practice

## Назначение проекта

Проект предназначен для демонстрации навыков разработки веб-приложений на Python и Flask, работы с базой данных, создания REST API, реализации аутентификации, тестирования и использования системы контроля версий Git.
