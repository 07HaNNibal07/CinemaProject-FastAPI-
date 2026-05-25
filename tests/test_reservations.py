import asyncio

import pytest


@pytest.mark.asyncio
async def test_user_can_book_available_place(
    booking_client,
    create_client,
    create_session,
    auth_headers,
    get_session_place,
    redis_client,
):
    user = await create_client()
    session = await create_session()

    response = await booking_client.patch(
        "/client/book_place",
        params={"session_id": session["id"], "place_number": 1},
        json={"status": "booked"},
        headers=auth_headers(user["token"]),
    )

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "booked"

    place = await get_session_place(session["id"], 1)
    assert place["status"] == "booked"

    owner = await redis_client.get(f"reservation:{session['id']}:1")
    assert owner == str(user["id"])


@pytest.mark.asyncio
async def test_other_user_cannot_buy_foreign_reservation(
    booking_client,
    create_client,
    create_session,
    auth_headers,
    get_session_place,
):
    owner = await create_client()
    intruder = await create_client()
    session = await create_session()

    book_response = await booking_client.patch(
        "/client/book_place",
        params={"session_id": session["id"], "place_number": 1},
        json={"status": "booked"},
        headers=auth_headers(owner["token"]),
    )
    assert book_response.status_code == 200, book_response.text

    buy_response = await booking_client.post(
        "/client/buy_ticket",
        json={"session_id": session["id"], "place_number": 1},
        headers=auth_headers(intruder["token"]),
    )

    assert buy_response.status_code == 403, buy_response.text
    assert buy_response.json()["detail"] == "This reservation belongs to another user"

    place = await get_session_place(session["id"], 1)
    assert place["status"] == "booked"


@pytest.mark.asyncio
async def test_reservation_owner_can_buy_ticket(
    booking_client,
    create_client,
    create_session,
    auth_headers,
    get_session_place,
    redis_client,
):
    user = await create_client()
    session = await create_session()

    book_response = await booking_client.patch(
        "/client/book_place",
        params={"session_id": session["id"], "place_number": 1},
        json={"status": "booked"},
        headers=auth_headers(user["token"]),
    )
    assert book_response.status_code == 200, book_response.text

    buy_response = await booking_client.post(
        "/client/buy_ticket",
        json={"session_id": session["id"], "place_number": 1},
        headers=auth_headers(user["token"]),
    )

    assert buy_response.status_code == 200, buy_response.text
    ticket = buy_response.json()
    assert ticket["session_id"] == session["id"]
    assert ticket["place_number"] == 1
    assert ticket["ticket_status"] == "active"

    place = await get_session_place(session["id"], 1)
    assert place["status"] == "paid"

    reservation_key = await redis_client.get(f"reservation:{session['id']}:1")
    assert reservation_key is None


@pytest.mark.asyncio
async def test_place_becomes_available_after_reservation_ttl(
    booking_client,
    create_client,
    create_session,
    auth_headers,
    redis_client,
    wait_for_place_status,
):
    user = await create_client()
    session = await create_session()

    book_response = await booking_client.patch(
        "/client/book_place",
        params={"session_id": session["id"], "place_number": 1},
        json={"status": "booked"},
        headers=auth_headers(user["token"]),
    )
    assert book_response.status_code == 200, book_response.text

    reservation_key = f"reservation:{session['id']}:1"
    await redis_client.expire(reservation_key, 1)
    await asyncio.sleep(2)

    place = await wait_for_place_status(session["id"], 1, "available")
    assert place["status"] == "available"
