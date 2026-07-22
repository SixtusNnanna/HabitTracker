import pytest
from sqlalchemy import select
from app.core.email_token import generate_verification_token
from app.database.models import User


async def _signup(client, db_session, email="loginuser@example.com", password="Nna@37832435"):
    e = await client.post(
        "auth/signup", json={"full_name": "Login User", "email": email, "password": password}
    )
    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()
    user.is_verified = True
    await db_session.commit()
    return e


@pytest.mark.asyncio
async def test_sign_up_success(client):
    response = await client.post(
        "/auth/signup",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "Strong@37832435"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_for_password_validation_signup(client):
    payload = {
        "full_name": "Test User2",
        "email": "testuser2@gmail.com",
        "password": "testuserismadded"
    }

    response = await client.post("auth/signup", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_for_duplicate_email(client):
    payload = {
            "full_name": "Test User2",
            "email": "testuser2@gmail.com",
            "password": "Nna@378324353"
        }

    await client.post("auth/signup", json=payload)
    response = await client.post("auth/signup", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client, db_session):
    email, password = "sample@example.com", "Sample#t23421"
    await _signup(client, db_session, email, password)
    response = await client.post(
        "auth/token",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_wrong_password(client, db_session):
    email, password = "sample@example.com", "Sample#t23421"
    await _signup(client, db_session, email, password)
    response = await client.post(
        "auth/token",
        data={"username": email, "password": "@001rgeThrT"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password and Email"


@pytest.mark.asyncio
async def test_login_with_Non_existent_email(client, db_session):
    # email, password = "sample@example.com", "Sample#t23421"
    # await _signup(client, db_session, email, password)
    response = await client.post(
        "auth/token",
        data={"username": "franpaic@gmail.com", "password": "@001rgeThrT"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User is not registered"


@pytest.mark.asyncio
async def test_login_token_actually_works(client, db_session):
    email, password = "tokencheck@example.com", "StrongPass123!"
    await _signup(client, db_session, email, password)

    login_response = await client.post(
        "auth/token",
        data={"username": email, "password": password},
    )
    token = login_response.json()["access_token"]
    print(f"Login Response {login_response}")
    me_response = await client.get(
        "auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    print(f"Me response {me_response}")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email






