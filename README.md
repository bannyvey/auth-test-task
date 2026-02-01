# Auth Service

Сервис аутентификации на FastAPI с использованием JWT токенов, Redis и PostgreSQL.

## Требования

- Python 3.12
- Docker Compose
- uv (менеджер пакетов Python)

## Быстрый старт

### 1. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл, указав необходимые параметры (см. раздел "Переменные окружения").

### 2. Запуск Redis и PostgreSQL

```bash
docker-compose up -d
```

Эта команда запустит:
- **Redis** на порту `6377` (внешний) → `6379` (внутри контейнера)
- **PostgreSQL** на порту, указанном в `POSTGRES_HOST_PORT`

### 3. Установка зависимостей

Создайте виртуальное окружение и установите зависимости:

```bash
uv venv
uv sync
```

### 4. Инициализация базы данных (опционально)

Если нужно создать тестовых пользователей:

```bash
uv run python seed_db.py
```

Это создаст:
- 4 администратора (`admin1@example.com` - `admin4@example.com`)
- 26 обычных пользователей (`user1@example.com` - `user26@example.com`)
- Пароль для всех: `password123`

### 5. Запуск приложения

```bash
uv run uvicorn main:app --reload
```

Сервис будет доступен по адресу: **http://127.0.0.1:8000**

API документация (Swagger): **http://127.0.0.1:8000/docs**

## Переменные окружения

Создайте файл `.env` со следующими переменными:

```env 
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_HOST_PORT=5429
POSTGRES_PASSWORD=callofduty
POSTGRES_USER=postgres
POSTGRES_DB=auth

# JWT settings
JWT_SECRET_KEY=your-super-mega-puper-key-123-awdawdc
JWT_ALGORITHM=HS256
JWT_ISSUER=AuthAuthAuth
JWT_AUDIENCE=AuthAuth



REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_HOST_PORT=6377
REDIS_PASSWORD=redis
REDIS_CACHE_TTL=300

## Как работает аутентификация

Система использует JWT токены с cookie-based аутентификацией и автоматической ротацией refresh токенов.

### Процесс аутентификации

1. **Логин** (`POST /auth/login`)
   - Пользователь отправляет `email` и `password`
   - Backend проверяет учетные данные
   - Генерируется два токена:
     - **Access token** (короткий, 1 минута для теста) — для доступа к API
     - **Refresh token** (длинный, 7 дней) — для обновления access token
   - Оба токена отправляются клиенту через **httpOnly cookie** (защита от XSS)
   - Refresh token сохраняется в **Redis** для валидации

2. **Авторизованные запросы**
   - Клиент делает запросы к API
   - Браузер автоматически прикрепляет `access_token` из cookie
   - Backend проверяет токен (подпись + срок действия)
   - Если токен валиден → запрос обрабатывается

3. **Истечение access token**
   - Через 15 минут access token истекает
   - API возвращает `401 Unauthorized`
   - Frontend автоматически делает запрос на `/auth/refresh`

4. **Обновление токенов** (`POST /auth/refresh`)
   - Браузер отправляет `refresh_token` из cookie
   - Backend проверяет токен в Redis
   - Если валиден:
     - Старый refresh token **удаляется** из Redis
     - Генерируются **новые** access и refresh токены
     - Новые токены устанавливаются в cookie
   - Пользователь продолжает работу без повторного ввода пароля

### Преимущества подхода

- ✅ **Безопасность**: httpOnly cookie защищают от XSS атак
- ✅ **Удобство**: автоматическое обновление без участия пользователя
- ✅ **Ротация токенов**: каждый refresh используется только один раз
- ✅ **Централизованная инвалидация**: через Redis можно отозвать токены
- ✅ **Короткий срок жизни access token**: минимизирует риски при компрометации

## API Endpoints

### Аутентификация

- `POST /auth/register` — Регистрация нового пользователя
- `POST /auth/login` — Вход в систему
- `POST /auth/refresh` — Обновление токенов
- `GET /auth/me` — Получить данные текущего пользователя
- `PATCH /auth/me` — Обновить профиль
- `DELETE /auth/me` — Удалить аккаунт (soft delete)

### Администрирование

- `PATCH /admin/users/{user_id}/role` — Изменить роль пользователя (только для админов)

## Безопасность

- Пароли хешируются с использованием **bcrypt**
- JWT токены подписываются с использованием **HS256**
- Refresh токены хранятся в **Redis** с TTL
- Cookie с флагами `httpOnly`, `secure`, `samesite=lax`
- Валидация данных через **Pydantic**

## Логирование

Приложение использует стандартное логирование Python. Логи настраиваются в `settings.py`.

## Разработка

### Запуск в режиме разработки

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

