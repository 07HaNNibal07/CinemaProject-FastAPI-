from ..models import SessionPlace
from ..core.db_dep import session
from sqlalchemy import select
from common_auth.redis import redis

async def listen_expired():
    pubsub = redis.pubsub()
    await pubsub.subscribe("__keyevent@0__:expired")

    async for message in pubsub.listen():
        key = message["data"]

        if not isinstance(key, str) or not key.startswith("reservation:"):
            continue

        _, session_id, place_number = key.split(":")

        async with session() as db:
            place = await db.scalar(
                select(SessionPlace).where(
                    SessionPlace.session_id == int(session_id),
                    SessionPlace.place_number == int(place_number),
                    SessionPlace.status == 'booked'
                )
            )

            if place:
                place.status = "available"
                await db.commit()
