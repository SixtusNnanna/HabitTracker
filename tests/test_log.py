import pytest

from sqlalchemy import select
from app.database.models import User


INTERVAL_HABIT_DATA = {
            "name": "Gym",
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "interval",
            "target_value": 3,
            "target_unit": "Times",
            "interval_days": 3
}

DAILY_HABIT_DATA = {
            "name": "Gym",
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "daily",
            "target_value": 3,
            "target_unit": "Times"
}

WEEKLY_HABIT_DATA = {
            "name": "Gym",
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "weekly",
            "target_value": 3,
            "target_unit": "Times",
            "day_of_week": ["Thursay", "Friday"]
}


LOG_DATA = {
            "date_": "2026-07-22",
            "status": "completed",
            "value": 2,
            "note": "This is logged"
        }


async def _get_authorized_header(client, db_session, email="loginuser@example.com", password="Nna@37832435"):
    await client.post(
        "/auth/signup",
        json={"full_name": "Test User", "email": email, "password": password}
    )
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.is_verified = True
    await db_session.commit()

    login_response = await client.post(
        "auth/token",
        data={"username": email, "password": password},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _get_habit_id(client, db_session):
    headers = await _get_authorized_header(client, db_session)
    habit_response = await client.post(
        "/habit/",
        json=INTERVAL_HABIT_DATA,
        headers=headers
    )
    return habit_response.json()["id"], headers


async def _get_daily_habit_id(client, db_session):
    headers = await _get_authorized_header(client, db_session)
    habit_response = await client.post(
        "/habit/",
        json=DAILY_HABIT_DATA,
        headers=headers
    )
    return habit_response.json()["id"], headers

async def _get_weekly_habit_id(client, db_session):
    headers = await _get_authorized_header(client, db_session)
    habit_response = await client.post(
        "/habit/",
        json=WEEKLY_HABIT_DATA,
        headers=headers
    )
    return habit_response.json()["id"], headers


async def _return_created_log(client, db_session):
    habit_id, headers = await _get_habit_id(client, db_session)
    response = await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    return response


@pytest.mark.asyncio
async def test_create_log_success(client, db_session):
    response = await _return_created_log(client, db_session)
    assert response.status_code == 201


async def test_creating_two_log_in_on_habit_due_date(client, db_session):
    habit_id, headers = await _get_daily_habit_id(client, db_session)
    await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    response = await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    body = response.json()
    assert response.status_code == 409
    assert body["detail"] == "Habit already logged for this date"


async def test_create_log_outside_habit_due_date(client, db_session):
    habit_id, headers = await _get_weekly_habit_id(client, db_session)
    response = await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    body = response.json()
    assert response.status_code == 409
    assert body["detail"] == "Today is not your due date"






@pytest.mark.asyncio
async def test_get_log_list_success(client, db_session):
    habit_id, headers = await _get_habit_id(client, db_session)
    await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    response = await client.get(f"/habit/{habit_id}/logs", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["habit_id"] == habit_id


@pytest.mark.asyncio
async def test_get_log_list_wrong_user(client, db_session):
    habit_id, headers = await _get_habit_id(client, db_session)
    await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    headers2 = await _get_authorized_header(client, db_session, email="cjiks@hi.com")
    response = await client.get(f"/habit/{habit_id}/logs", headers=headers2)

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Not Found"



@pytest.mark.asyncio
async def test_get_log_by_id_wrong_user(client, db_session):
    habit_id, headers = await _get_habit_id(client, db_session)
    log = await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    log_id = log.json()["id"]
    headers2 = await _get_authorized_header(client, db_session, email="cjiks@hi.com")
    response = await client.get(f"/habit/{habit_id}/logs/{log_id}", headers=headers2)

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Not Found"



@pytest.mark.asyncio
async def test_delete_log_with_wrong_user(client, db_session):
    habit_id, headers = await _get_habit_id(client, db_session)

    log = await client.post(
        f"/habit/{habit_id}/logs",
        json=LOG_DATA,
        headers=headers
    )
    log_id = log.json()["id"]
    headers2 = await _get_authorized_header(client, db_session, email="cjiks@hi.com")
    response = await client.delete(f"/habit/{habit_id}/logs/{log_id}", headers=headers2)

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Not Found"
