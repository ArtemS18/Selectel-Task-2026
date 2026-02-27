# Selectel Vacancies API

FastAPI-приложение для парсинга публичных вакансий Selectel, хранения в PostgreSQL и предоставления CRUD API.

## Быстрый старт

1. Клонируйте репозиторий (или распакуйте проект из архива):
   `git clone --branch with-bugs https://github.com/selectel/be-test.git`
2. Создайте `.env` на основе примера:
   `cp .env.example .env`
3. Примените переменные окружения `.env`:
   `source .env`
4. Запуск через Docker Desktop:
   `docker compose up --build`
5. Проверка работоспособности:
   откройте `http://localhost:8000/docs`
6. Остановка и очистка:
   `docker-compose down -v`

## Переменные окружения

- `DATABASE_URL` — строка подключения к PostgreSQL.
- `LOG_LEVEL` — уровень логирования (`INFO`, `DEBUG`).
- `PARSE_SCHEDULE_MINUTES` — интервал фонового парсинга в минутах.

## Основные эндпоинты

- `GET /api/v1/vacancies/` — список вакансий
- `GET /api/v1/vacancies/{id}` — детали вакансии.
- `POST /api/v1/vacancies/` — создание вакансии.
- `PUT /api/v1/vacancies/{id}` — обновление вакансии.
- `DELETE /api/v1/vacancies/{id}` — удаление вакансии.
- `POST /api/v1/parse/` — ручной запуск парсинга.

## Примечания

- При старте приложения выполняется первичный парсинг.
- Фоновый парсинг запускается планировщиком APScheduler (в рамках заданного интервала).


# Отчет

## 1. Шаг 1: Анализ и запуск

* **Что сделал:**
  Запустил `docker-compose up`, получил ошибку

  ```
  Extra inputs are not permitted [type=extra_forbidden, input_value='postgresql+asyncpg://pos...stgres@db:5432/postgres', input_type=str]
  ```

* **Проблема:**
  Контейнер не стартует из-за дополнительных полей при парсинге конфига (тк мы два раза его используем в docker-compose и в самом Docker образе, когда копируем)

* **Решение:**
  Добавил в парсинг конфига `extra="ignore"`. Также исправил алиас на `"DATABASE_URL"`

* **Что сделал:**
  Снова попытался запустить

* **Проблема:**
  Приложение выдает ошибку

  ```
  /usr/local/lib/python3.11/site-packages/uvicorn/lifespan/on.py:91: RuntimeWarning: coroutine '_run_parse_job' was never awaited
  ```

* **Решение:**
  `_scheduler = create_scheduler(_run_parse_job)` — не нужно вызывать `await _run_parse_job`, тк это запустит парсер и остановит весь event loop. Нужно передавать его в планировщик.

* **Дополнительно:**
  Исправил копирование в Dockerfile (итак копирует в WORKDIR):

  ```dockerfile
  COPY requirements.txt .
  COPY . .
  ```

---

## 2. Шаг 2: Исправление багов парсера

* **Что сделал:**
  Запустил планировщик парсера

* **Проблема:**
  Парсер запускается каждые 5 сек вместо положенных 5 минут

* **Решение:**
  Поменял `seconds` на `settings.parse_schedule_minutes * 60`

* **Что сделал:**
  Запустил еще раз планировщик парсера

* **Проблема:**
  ```python
  "city_name": item.city.name.strip(),
                   ^^^^^^^^^^^^^^
  AttributeError: 'NoneType' object has no attribute 'name'
  ```

* **Решение:**
  Добавил проверку опционального поля:

  ```python
  "city_name": item.city.name.strip() if item.city else None
  ```
---

## 3. Шаг 3: Исправление багов API

* **Что сделал:**
  Запустил ручку `POST /api/v1/vacancies/{vacancy_id}` с `external_id`, который уже существует

* **Проблема:**
  Сервер отдает статус 200, при этом возвращается ошибка

* **Решение:**
  Поменял `JSONResponse` на `HTTPException` и установил статус `status.HTTP_409_CONFLICT`

* **Что сделал:**
  Запустил ручку `PUT /api/v1/vacancies/{vacancy_id}` с `external_id`, который уже существует

* **Проблема:**
  Сервер отдает 500 ошибку

* **Решение:**
  Добавил проверку на уникальность `external_id`
---

## 4. Шаг 4: Дополнительные исправления кода и оптимизация

* Добавил GIN индексы для полей `timetable_mode_name` и `city` используя библиотеку `gin_trgm_ops` для ускорения поиска по `ILIKE %...%`

* Оптимизировал в `upsert_external_vacancies` получение вакансий (все данные с существующими `external_id` получаю одним запросом и записываю в словарь)

* Вместо `app.on_startup` / `app.on_shutdown` использовал `lifespan`

* Добавил в `docker-compose` volumes:
  ```
  - ./app:/app/app
  ```
  и флаг `--reload` на время тестов приложения

* Исправил тип у поля в конфиге `log_level`:
  ```python
  log_level: Literal["INFO", "DEBUG"]
  ```
  для прозрачности
