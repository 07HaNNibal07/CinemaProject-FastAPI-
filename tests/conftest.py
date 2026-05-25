import asyncio
import os
from itertools import count
from time import monotonic

import httpx
import pytest
import pytest_asyncio
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


BOOKING_TRUNCATE_SQL = text(
    "TRUNCATE TABLE requests, tickets, clients, admins RESTART IDENTITY CASCADE"
)
CINEMA_TRUNCATE_SQL = text(
    "TRUNCATE TABLE session_places, sessions, places, halls, movies RESTART IDENTITY CASCADE"
)


async def _truncate(engine: AsyncEngine, statement) -> None:
    async with engine.begin() as connection:
        await connection.execute(statement)


async def _wait_for_json(base_url: str, path: str = "/openapi.json", timeout: float = 60.0) -> None:
    deadline = monotonic() + timeout
    last_error = None

    async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
        while monotonic() < deadline:
            try:
                response = await client.get(path)
                if response.status_code == 200:
                    return
            except Exception as exc:  # pragma: no cover - retry loop
                last_error = exc

            await asyncio.sleep(1)

    raise RuntimeError(f"Service {base_url}{path} is not ready: {last_error}")


@pytest.fixture(scope="session")
def booking_base_url() -> str:
    return os.environ["BOOKING_BASE_URL"]


@pytest.fixture(scope="session")
def cinema_base_url() -> str:
    return os.environ["CINEMA_BASE_URL"]


@pytest_asyncio.fixture
async def booking_db_engine() -> AsyncEngine:
    engine = create_async_engine(os.environ["BOOKING_TEST_DB_URL"], future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def cinema_db_engine() -> AsyncEngine:
    engine = create_async_engine(os.environ["CINEMA_TEST_DB_URL"], future=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client() -> Redis:
    client = Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ["REDIS_PORT"]),
        decode_responses=True,
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def wait_for_services(booking_base_url: str, cinema_base_url: str) -> None:
    await _wait_for_json(booking_base_url)
    await _wait_for_json(cinema_base_url)


@pytest_asyncio.fixture
async def booking_client(booking_base_url: str) -> httpx.AsyncClient:
    async with httpx.AsyncClient(base_url=booking_base_url, timeout=15.0) as client:
        yield client


@pytest_asyncio.fixture
async def cinema_client(cinema_base_url: str) -> httpx.AsyncClient:
    async with httpx.AsyncClient(base_url=cinema_base_url, timeout=15.0) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def cleanup_state(
    booking_db_engine: AsyncEngine,
    cinema_db_engine: AsyncEngine,
    redis_client: Redis,
) -> None:
    await redis_client.flushall()
    await _truncate(booking_db_engine, BOOKING_TRUNCATE_SQL)
    await _truncate(cinema_db_engine, CINEMA_TRUNCATE_SQL)

    yield

    await redis_client.flushall()
    await _truncate(booking_db_engine, BOOKING_TRUNCATE_SQL)
    await _truncate(cinema_db_engine, CINEMA_TRUNCATE_SQL)


@pytest.fixture(scope="session")
def auth_headers():
    def factory(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return factory


@pytest_asyncio.fixture
async def create_client(booking_client: httpx.AsyncClient):
    counter = count(1)

    async def factory(*, balance: str = "2000.00", password: str = "Qwerty_123"):
        index = next(counter)
        payload = {
            "name": f"User{index}",
            "surname": f"Test{index}",
            "email": f"user{index}@example.com",
            "number": f"+79990000{index:03d}",
            "password": password,
            "balance": balance,
        }

        register_response = await booking_client.post("/client/register_client", json=payload)
        assert register_response.status_code == 200, register_response.text
        user = register_response.json()

        login_response = await booking_client.post(
            "/login",
            data={"username": payload["email"], "password": password},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        return {
            "id": user["id"],
            "email": payload["email"],
            "password": password,
            "token": token,
            "profile": user,
        }

    return factory


@pytest_asyncio.fixture
async def create_session(cinema_client: httpx.AsyncClient):
    counter = count(1)

    async def factory(*, hall_number: int | None = None, place_count: int = 5):
        index = next(counter)
        current_hall_number = hall_number or index
        movie_name = f"Movie {index}"

        hall_response = await cinema_client.post(
            "/control/create_hall",
            json={
                "hall_data": {
                    "number_hall": current_hall_number,
                    "count_place": place_count,
                },
                "place_data": {
                    "number": 1,
                    "price": "300.00",
                    "status": "available",
                    "place_type": "standard",
                },
            },
        )
        assert hall_response.status_code == 200, hall_response.text

        movie_response = await cinema_client.post(
            "/movies/create_movie",
            json={
                "name": movie_name,
                "genre": "Sci-Fi",
                "aboutMovie": "Test movie",
                "age_limit": 16,
            },
        )
        assert movie_response.status_code == 200, movie_response.text

        session_response = await cinema_client.post(
            "/session/create_session",
            json={
                "movie_name": movie_name,
                "number_hall": current_hall_number,
                "session_date": "2030-01-01",
                "session_time": "19:00:00",
            },
        )
        assert session_response.status_code == 200, session_response.text
        return session_response.json()

    return factory


@pytest_asyncio.fixture
async def get_session_place(cinema_client: httpx.AsyncClient):
    async def factory(session_id: int, place_number: int) -> dict:
        response = await cinema_client.get(
            "/control/show_session_places",
            params={"session_id": session_id},
        )
        assert response.status_code == 200, response.text
        places = response.json()
        return next(place for place in places if place["place_number"] == place_number)

    return factory


@pytest_asyncio.fixture
async def wait_for_place_status(get_session_place):
    async def factory(
        session_id: int,
        place_number: int,
        expected_status: str,
        timeout: float = 8.0,
    ) -> dict:
        deadline = monotonic() + timeout
        last_place = None

        while monotonic() < deadline:
            last_place = await get_session_place(session_id, place_number)
            if last_place["status"] == expected_status:
                return last_place
            await asyncio.sleep(0.25)

        raise AssertionError(
            f"Place {place_number} in session {session_id} never became "
            f"{expected_status!r}. Last payload: {last_place}"
        )

    return factory
