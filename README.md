# Cinema Project (FastAPI)

Микросервисный учебный проект для бронирования и покупки билетов в кинотеатр.

Проект состоит из двух FastAPI-сервисов:

- `booking-service` - регистрация, логин, баланс клиента, бронирование и покупка билетов
- `cinema-service` - фильмы, залы, сеансы и места в сеансах

Дополнительно используются:

- `PostgreSQL` - отдельная БД для каждого сервиса
- `Redis` - временное хранение брони места и TTL
- `Celery` - фоновые задачи в `booking-service`
- `pgAdmin` - просмотр БД

## Архитектура

```text
client
  -> booking-service
       -> PostgreSQL (booking)
       -> Redis
       -> HTTP -> cinema-service
                     -> PostgreSQL (cinema)
                     -> Redis expired listener
```

### Что где хранится

- `booking-service` хранит клиентов, заявки и купленные билеты
- `cinema-service` хранит фильмы, залы, сеансы и статус мест
- `Redis` хранит ключи вида `reservation:{session_id}:{place_number}`

## Основные возможности

### booking-service

- регистрация клиента
- логин по email или номеру телефона
- пополнение баланса
- просмотр профиля
- создание заявки
- бронирование места
- покупка билета
- просмотр своих билетов
- деактивация аккаунта

### cinema-service

- создание зала и мест
- создание фильма
- создание сеанса
- просмотр мест сеанса
- смена статуса места
- покупка места внутри `cinema-service`

## Как работает бронь

Сценарий бронирования сейчас такой:

1. клиент вызывает `PATCH /client/book_place`
2. `booking-service` меняет статус места в `cinema-service` на `booked`
3. в `Redis` создаётся ключ:

```text
reservation:{session_id}:{place_number}
```

4. TTL ключа сейчас задаётся прямо в коде и равен `900` секунд
5. после истечения ключа `cinema-service` через listener возвращает место в `available`

Если другой пользователь попытается купить чужую бронь, `booking-service` отклонит покупку.

## Celery

В проекте уже подключён базовый `Celery` в `booking-service`.

Сейчас он используется для простой фоновой задачи после покупки билета:

- `app.tasks.send_ticket_notification`

Текущий пример задачи просто пишет сообщение в лог/stdout. Это заготовка под:

- email-уведомления
- audit log
- генерацию QR/PDF
- аналитику

Запуск worker вручную:

```powershell
docker compose exec booking_service celery -A app.celery_app:celery_app worker --loglevel=info
```

## Структура проекта

```text
booking-service/
  app/
    core/
    models/
    routers/
    schemas/
    utils/
    celery_app.py
    tasks.py

cinema-service/
  app/
    core/
    models/
    routers/
    schemas/
    utils/

common_auth/
  jwt.py
  dependencies.py
  redis.py

tests/
  conftest.py
  test_reservations.py

docker-compose.yaml
docker-compose.test.yml
```

## Быстрый старт

### 1. Подготовка

Нужны:

- Docker
- Docker Compose

Файл `.env` уже используется сервисами. Основные переменные:

```env
BOOKING_USER=postgres_boocking
BOOKING_PASSWORD=test1234
BOOKING_HOST=boocking_db
BOOKING_DB=boockingdb
BOOKING_SETTINGS__DB_URL=postgresql+asyncpg://${BOOKING_USER}:${BOOKING_PASSWORD}@${BOOKING_HOST}:5432/${BOOKING_DB}
BOOKING_SETTINGS__DB_ECHO=True

CINEMA_USER=postgres_cinema
CINEMA_PASSWORD=test1234
CINEMA_HOST=cinema_db
CINEMA_DB=cinemadb
CINEMA_SETTINGS__DB_URL=postgresql+asyncpg://${CINEMA_USER}:${CINEMA_PASSWORD}@${CINEMA_HOST}:5432/${CINEMA_DB}
CINEMA_SETTINGS__DB_ECHO=True

PGADMIN_EMAIL=...
PGADMIN_PASSWORD=...
```

### 2. Запуск основного стека

```powershell
docker compose up -d --build
```

### 3. Полезные адреса

- `booking-service` docs: `http://localhost:8001/docs`
- `cinema-service` docs: `http://localhost:8002/docs`
- `pgAdmin`: `http://localhost:5050`

## Пример минимального сценария

### 1. Создать администратора

Через Swagger `booking-service`:

- `POST /admin/create_admin`

### 2. Создать клиента

- `POST /client/register_client`

### 3. Выполнить логин

- `POST /login`

Полученный `access_token` использовать как `Bearer token`.

### 4. Создать фильм, зал и сеанс

Через `cinema-service`:

- `POST /movies/create_movie`
- `POST /control/create_hall`
- `POST /session/create_session`

### 5. Пополнить баланс клиента

- `PATCH /client/replenish`

### 6. Забронировать место

- `PATCH /client/book_place`

Пример тела:

```json
{
  "status": "booked"
}
```

Параметры:

- `session_id`
- `place_number`

### 7. Купить билет

- `POST /client/buy_ticket`

Пример тела:

```json
{
  "session_id": 1,
  "place_number": 5
}
```

## Тесты

Для проекта добавлен отдельный тестовый стек:

- отдельная тестовая БД `booking`
- отдельная тестовая БД `cinema`
- отдельный тестовый `Redis`
- отдельный контейнер `tests`

Запуск тестов:

```powershell
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests tests
```

Это нормальное поведение, если в конце ты видишь:

```text
tests-1 exited with code 0
Aborting on container exit...
```

Это значит, что тесты прошли, а Compose просто остановил временный тестовый стек.

Удаление тестового стека:

```powershell
docker compose -f docker-compose.test.yml down -v
```

### Что покрыто тестами

- пользователь бронирует `available` место
- другой пользователь не может купить чужую бронь
- владелец брони может купить билет
- после истечения TTL место снова становится `available`

## Полезные замечания

- `booking-service` общается с `cinema-service` по HTTP через `httpx`
- listener истечения Redis-ключей живёт в `cinema-service`
- `Celery` сейчас не встроен в `docker-compose.yaml` как отдельный сервис, worker запускается вручную
- миграции Alembic применяются автоматически при старте контейнеров

## Команды

Поднять проект:

```powershell
docker compose up -d --build
```

Посмотреть логи:

```powershell
docker compose logs -f
```

Остановить проект:

```powershell
docker compose down
```

Остановить проект с удалением volume:

```powershell
docker compose down -v
```
