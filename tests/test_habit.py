import pytest

from sqlalchemy import select
from app.database.models import User


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


@pytest.mark.asyncio
async def test_succesful_habit_create(client, db_session):
    headers = await _get_authorized_header(client, db_session)

    habit_response = await client.post(
        "/habit/",
        headers=headers,
        json={

            "name": "Gym",
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "interval",
            "target_value": 3,
            "target_unit": "Times",
            "interval_days": 3
        }
    )
    assert habit_response.status_code == 201


@pytest.mark.asyncio
async def test_missing_required_field(client, db_session):
    headers = await _get_authorized_header(client, db_session)

    habit_response = await client.post(
        "/habit/",
        headers=headers,
        json={
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "interval",
            "target_value": 3,
            "target_unit": "Times",
            "interval_days": 3
        }
    )
    assert habit_response.status_code == 422


@pytest.mark.asyncio
async def test_unauthenticate_request(client, db_session):
    headers = await _get_authorized_header(client, db_session)

    habit_response = await client.post(
        "/habit/",
        json={

            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "interval",
            "target_value": 3,
            "target_unit": "Times",
            "interval_days": 3
        }
    )
    assert habit_response.status_code == 401
    assert habit_response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_habit_by_id_succesfully(client, db_session):
    headers = await _get_authorized_header(client, db_session)

    habit_response = await client.post(
        "/habit/",
        json={
            "name": "Jesus",
            "description": "Going to the gym",
            "metric_type": "count",
            "frequency_type": "interval",
            "target_value": 3,
            "target_unit": "Times",
            "interval_days": 3
        },
        headers=headers
    )
    habit_id = habit_response.json()["id"]
    id_response = await client.get(
        f"/habit/{habit_id}",
        headers=headers
    )
    id_response.status_code == 200

