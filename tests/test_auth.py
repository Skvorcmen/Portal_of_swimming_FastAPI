import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
        "role": "athlete"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "password": "loginpass",
        "full_name": "Login User",
        "role": "athlete"
    })
    
    response = await client.post("/auth/token", data={
        "username": "loginuser",
        "password": "loginpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_get_me(client):
    await client.post("/auth/register", json={
        "email": "me@example.com",
        "username": "meuser",
        "password": "mepass",
        "full_name": "Me User",
        "role": "athlete"
    })
    
    login_resp = await client.post("/auth/token", data={
        "username": "meuser",
        "password": "mepass"
    })
    token = login_resp.json()["access_token"]
    
    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "meuser"
